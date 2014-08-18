# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import json
import logging
import requests

from decimal import Decimal as D

from django.conf import settings
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from eway.rapid import RESPONSE_CODES

logger = logging.getLogger('eway')

Transaction = get_model('eway', 'Transaction')
RequestLog = get_model('eway', 'RequestLog')


EWAY_PROCESS_PAYMENT = 'ProcessPayment'
EWAY_CREATE_TOKEN_CUSTOMER = 'CreateTokenCustomer'
EWAY_UPDATE_TOKEN_CUSTOMER = 'UpdateTokenCustomer'
EWAY_TOKEN_PAYMENT = 'TokenPayment'

EWAY_PAYMENT_METHODS = (
    EWAY_PROCESS_PAYMENT,
    EWAY_CREATE_TOKEN_CUSTOMER,
    EWAY_UPDATE_TOKEN_CUSTOMER,
    EWAY_TOKEN_PAYMENT,
)

EWAY_TITLE_VALUES = (
    'Mr.',
    'Ms.',
    'Mrs.',
    'Miss',
    'Dr.',
    'Sir.',
    'Prof.',
)

EWAY_SHIPPING_UNKNOWN = 'Unknown'
EWAY_SHIPPING_LOWCOST = 'LowCost'
EWAY_SHIPPING_DESIGNATEDBYCUSTOMER = 'DesignatedByCustomer'
EWAY_SHIPPING_INTERNATIONAL = 'International'
EWAY_SHIPPING_MILITARY = 'Military'
EWAY_SHIPPING_NEXTDAY = 'NextDay'
EWAY_SHIPPING_STOREPICKUP = 'StorePickup'
EWAY_SHIPPING_TWODAYSERVICE = 'TwoDayService'
EWAY_SHIPPING_THREEDAYSERVICE = 'ThreeDayService'
EWAY_SHIPPING_OTHER = 'Other'

EWAY_API_KEY = None
EWAY_PASSWORD = None
EWAY_CURRENCY = 'AUD'


class RapidError(BaseException):
    pass


class RapidResponse(object):

    def __init__(self, access_code, form_action_url, payment, customer, errors,
                 json_raw=None):
        self.access_code = access_code
        self.form_action_url = form_action_url
        self.payment = payment
        self.customer = customer

        self.errors = errors

        # Try to get properly indented JSON, if that fails we fall back to
        # the raw data.
        try:
            self.json_raw = json.dumps(json_raw, indent=4)
        except ValueError:
            self.json_raw = json_raw

    @classmethod
    def from_json(cls, response):
        return cls(
            access_code=response['AccessCode'],
            form_action_url=response['FormActionURL'],
            payment=Payment.from_json(response['Payment']),
            customer=Customer.from_json(response['Customer']),
            errors=cls.extract_errors(response['Errors']),
            json_raw=response)

    @classmethod
    def extract_errors(cls, error_codes):
        if not error_codes:
            return []

        errors = []
        for error_code in error_codes.split(','):
            errors.append(RapidResponseCode(error_code))

        return errors


class RapidResponseCode(object):

    def __init__(self, code):
        self.code = code
        self.message = RESPONSE_CODES.get(code, '')


class TotalAmountMixin(object):

    @property
    def total_amount(self):
        if self.total_amount_raw is None:
            return None
        left = int(self.total_amount_raw / 100)
        right = self.total_amount_raw - int(left * 100)
        return D("%d.%02d" % (left, right))

    @total_amount.setter
    def total_amount(self, value):
        if value is None:
            self.total_amount_raw = None
            return None
        self.total_amount_raw = int(value * 100)
        return value


class RapidAccessCodeResult(TotalAmountMixin):

    def __init__(self, authorisation_code, token_customer_id, access_code,
                 response_message, response_code, transaction_status,
                 transaction_id, total_amount=None, total_amount_raw=None,
                 **kwargs):
        self.total_amount_raw = total_amount_raw

        if self.total_amount_raw is None:
            self.total_amount = total_amount

        self.authorisation_code = authorisation_code
        self.token_customer_id = token_customer_id
        self.access_code = access_code
        self.response_code = response_code
        self.response_message = response_message or []
        self.transaction_status = transaction_status
        self.transaction_id = transaction_id

        self.errors = kwargs.get('errors', [])
        self.verification = kwargs.get('verification', None)
        self.beagle_score = kwargs.get('beagle_score', None)
        self.invoice_reference = kwargs.get('invoice_reference', None)
        self.invoice_number = kwargs.get('invoice_number', None)

        try:
            self.json_raw = json.dumps(kwargs.get('json_raw'), indent=4)
        except ValueError:
            self.json_raw = kwargs.get('json_raw')

    @classmethod
    def from_json(cls, response):
        errors = response.get('Errors', [])
        if errors:
            errors = [RapidResponseCode(c) for c in errors.split(',')]
        else:
            errors = []

        response_message = response.get('ResponseMessage', None)
        if response_message:
            response_message = [RapidResponseCode(c) for c in response_message.split(',')]

        options = []
        for option in response.get('Options', []):
            options.append(Option(option.get("Value", None)))

        verification = Verification.from_json(response.get('Verification', None))

        return cls(
            authorisation_code=response.get('AuthorisationCode', None),
            token_customer_id=response.get('TokenCustomerID', None),
            access_code=response.get('AccessCode', None),
            transaction_status=response.get('TransactionStatus', None),
            response_code=RapidResponseCode(response.get('ResponseCode', None)),
            response_message=response_message,
            verification=verification,
            errors=errors,
            invoice_reference=response.get('InvoiceReference', None),
            total_amount_raw=response.get('TotalAmount', None),
            transaction_id=response.get('TransactionID', None),
            invoice_number=response.get('InvoiceNumber', None),
            options=options,
            json_raw=response
        )


class Verification(object):

    def __init__(self, cvn, mobile, email, phone, address):
        self.cvn = cvn
        self.mobile = mobile
        self.email = email
        self.phone = phone
        self.address = address

    @classmethod
    def from_json(cls, response):
        if response is None:
            return
        return cls(
            cvn=response.get('CVN', None),
            mobile=response.get('Mobile', None),
            email=response.get('Email', None),
            phone=response.get('Phone', None),
            address=response.get('Address', None),
        )


class RapidAttribute(object):

    def __init__(self, name, max_length=None, attr_type=None):
        self.name = name
        self.max_length = max_length
        self.type = attr_type

    def validate(self, value):
        if value is None or self.type in (None, list):
            return

        if len(unicode(value)) > self.max_length:
            raise RapidError(
                _("Attribute value '%s' exceeds maximum length: %d") % (
                    value,
                    self.max_length
                )
            )

    def force_type(self, value):
        return self.type(value)


class RapidBaseObject(object):
    REST_ATTRIBUTES = {}

    def json(self):
        json_dict = {}
        for attr_name, rapid_attr in self.REST_ATTRIBUTES.items():
            attr_value = getattr(self, attr_name, None)

            if attr_value is None and attr_name != 'title':
                continue

            if rapid_attr.type is None:
                json_dict[rapid_attr.name] = attr_value.json()
                continue

            if issubclass(rapid_attr.type, (tuple, list)):
                if not attr_value:
                    continue
                json_dict[rapid_attr.name] = []
                for value in attr_value:
                    json_dict[rapid_attr.name].append(value.json())
                continue

            rapid_attr.validate(attr_value)
            json_dict[rapid_attr.name] = rapid_attr.force_type(attr_value)
        return json_dict

    def serialise(self):
        return json.dumps(self.json())


class Request(RapidBaseObject):
    REST_ATTRIBUTES = {
        'redirect_url': RapidAttribute('RedirectUrl', 512, unicode),
        'customer_ip': RapidAttribute('CustomerIP', 50, unicode),
        'method': RapidAttribute('Method', 20, unicode),
        'device_id': RapidAttribute('DeviceID', 50, unicode),

        'payment': RapidAttribute('Payment'),
        'customer': RapidAttribute('Customer'),
        'shipping_address': RapidAttribute('ShippingAddress'),

        'items': RapidAttribute('Items', None, list),
        'options': RapidAttribute('Options', None, list),
    }

    def __init__(self, redirect_url, method, customer_ip=None, device_id=None,
                 customer=None, payment=None, shipping_address=None, items=None,
                 options=None):

        if method not in EWAY_PAYMENT_METHODS:
            raise RapidError(
                _("payment method %s is not a valid Rapid 3.0 method") % method
            )

        self.redirect_url = redirect_url
        self.method = method
        self.customer_ip = customer_ip or u''
        self.device_id = device_id or u''

        self.payment = payment
        self.customer = customer
        self.shipping_address = shipping_address

        self.items = items or []

        self.options = []
        if options:
            for option in options:
                self.options.append(Option(option))

    def __repr__(self):
        return unicode(self)

    def __unicode__(self):
        return self.serialise()


class Payment(RapidBaseObject, TotalAmountMixin):
    REST_ATTRIBUTES = {
        'total_amount_raw': RapidAttribute('TotalAmount', 10, int),
        'invoice_number': RapidAttribute('InvoiceNumber', 50, unicode),
        'invoice_description': RapidAttribute('InvoiceDescription', 5, unicode),
        'invoice_reference': RapidAttribute('InvoiceReference', 50, unicode),
        'currency_code': RapidAttribute('CurrencyCode', 50, unicode),
    }

    def __init__(self, total_amount=None, invoice_number=None,
                 invoice_description=None, invoice_reference=None,
                 currency_code=None, total_amount_raw=None):

        self.total_amount_raw = total_amount_raw
        if self.total_amount_raw is None:
            self.total_amount = total_amount

        self.invoice_number = invoice_number
        self.invoice_description = invoice_description
        self.invoice_reference = invoice_reference

        if not currency_code:
            currency_code = getattr(settings, 'EWAY_CURRENCY', EWAY_CURRENCY)

        self.currency_code = currency_code

    @classmethod
    def from_json(cls, response):
        return cls(
            total_amount_raw=response.get("TotalAmount", None),
            invoice_number=response.get('InvoiceNumber', None),
            invoice_description=response.get('InvoiceDescription', None),
            invoice_reference=response.get('InvoiceReference', None),
            currency_code=response.get('CurrencyCode', None),
        )


class Customer(RapidBaseObject):
    REST_ATTRIBUTES = {
        'token_customer_id': RapidAttribute('TokenCustomerID', 16, int),
        'reference': RapidAttribute('Reference', 50, unicode),
        'title': RapidAttribute('Title', 5, unicode),
        'first_name': RapidAttribute('FirstName', 50, unicode),
        'last_name': RapidAttribute('LastName', 50, unicode),
        'company_name': RapidAttribute('CompanyName', 50, unicode),
        'job_description': RapidAttribute('JobDescription', 50, unicode),
        'street1': RapidAttribute('Street1', 50, unicode),
        'street2': RapidAttribute('Street2', 50, unicode),
        'city': RapidAttribute('City', 50, unicode),
        'state': RapidAttribute('State', 50, unicode),
        'postal_code': RapidAttribute('PostalCode', 50, unicode),
        'country': RapidAttribute('Country', 2, unicode),
        'email': RapidAttribute('Email', 50, unicode),
        'phone': RapidAttribute('Phone', 32, unicode),
        'mobile': RapidAttribute('Mobile', 32, unicode),
        'comments': RapidAttribute('Comments', 255, unicode),
        'fax': RapidAttribute('Fax', 32, unicode),
        'url': RapidAttribute('Url', 512, unicode),
    }

    def __init__(self, token_customer_id=None, billing_address=None, reference=None,
                 title=None, email=None, phone=None, mobile=None, comments=None,
                 fax=None, url=None, **kwargs):
        self.token_customer_id = token_customer_id  # this is the TokenCustomerID
        self.reference = reference
        self.title = self.get_valid_title(title)
        self.email = email
        self.phone = phone
        self.mobile = mobile
        self.comments = comments
        self.fax = fax
        self.url = url

        self.first_name = kwargs.get('first_name', None)
        self.last_name = kwargs.get('last_name', None)
        self.company_name = kwargs.get('company_name', None)
        self.job_description = kwargs.get('job_description', None)
        self.street1 = kwargs.get('street1', None)
        self.street2 = kwargs.get('street2', None)
        self.city = kwargs.get('city', None)
        self.state = kwargs.get('state', None)
        self.postal_code = kwargs.get('postal_code', None)
        self.country = kwargs.get('country', None)

        self.card_name = kwargs.get('card_name', None)
        self.card_number = kwargs.get('card_number', None)
        self.card_start_month = kwargs.get('card_start_month', None)
        self.card_start_year = kwargs.get('card_start_year', None)
        self.card_issue_number = kwargs.get('card_issue_number', None)
        self.card_expiry_month = kwargs.get('card_expiry_month', None)
        self.card_expiry_year = kwargs.get('card_expiry_year', None)

        if billing_address:
            self.set_address(billing_address)

    def get_valid_title(self, title):
        if title is None:
            return u'Prof.'
        for eway_title in  EWAY_TITLE_VALUES:
            if eway_title.startswith(title):
                return eway_title
        return u'Prof.'

    def set_address(self, address):
        self.title = self.get_valid_title(address.title)

        self.first_name = address.first_name
        self.last_name = address.last_name
        self.street1 = address.line1
        self.street2 = address.line2
        self.city = address.line4
        self.state = address.state
        self.postal_code = address.postcode
        self.country = address.country.iso_3166_1_a2.lower()

    @classmethod
    def from_json(cls, response):
        return cls(
            token_customer_id=response.get("TokenCustomerID", None),
            reference=response.get("Reference", None),
            title=response.get("Title", None),
            first_name=response.get("FirstName", None),
            last_name=response.get("LastName", None),
            company_name=response.get("CompanyName", None),
            job_description=response.get("JobDescription", None),
            street1=response.get("Street1", None),
            street2=response.get("Street2", None),
            city=response.get("City", None),
            state=response.get("State", None),
            postal_code=response.get("PostalCode", None),
            country=response.get("Country", None),
            email=response.get("Email", None),
            phone=response.get("Phone", None),
            mobile=response.get("Mobile", None),
            comments=response.get("Comments", None),
            fax=response.get("Fax", None),
            url=response.get("Url", None),
            card_number=response.get("CardNumber", None),
            card_start_month=response.get("CardStartMonth", None),
            card_start_year=response.get("CardStartYear", None),
            card_issue_number=response.get("CardIssueNumber", None),
            card_name=response.get("CardName", None),
            card_expiry_month=response.get("CardExpiryMonth", None),
            card_expiry_year=response.get("CardExpiryYear", None),
        )


class ShippingAddress(RapidBaseObject):
    REST_ATTRIBUTES = {
        'shipping_method': RapidAttribute('ShippingMethod', 30, unicode),
        'first_name': RapidAttribute('FirstName', 50, unicode),
        'last_name': RapidAttribute('LastName', 50, unicode),
        'street1': RapidAttribute('Street1', 50, unicode),
        'street2': RapidAttribute('Street2', 50, unicode),
        'city': RapidAttribute('City', 50, unicode),
        'state': RapidAttribute('State', 50, unicode),
        'postal_code': RapidAttribute('PostalCode', 50, unicode),
        'country': RapidAttribute('Country', 2, unicode),
        'email': RapidAttribute('Email', 50, unicode),
        'phone': RapidAttribute('Phone', 32, unicode),
        'fax': RapidAttribute('Fax', 32, unicode),
    }

    def __init__(self, shipping_method, shipping_address=None, email=None,
                 phone=None, fax=None):
        self.shipping_method = shipping_method
        self.email = email
        self.phone = phone
        self.fax = fax

        self.first_name = None
        self.last_name = None
        self.street1 = None
        self.street2 = None
        self.city = None
        self.state = None
        self.postal_code = None
        self.country = None

        if shipping_address:
            self.set_shipping_address(shipping_address)

    def set_shipping_address(self, shipping_address):
        self.first_name = shipping_address.first_name
        self.last_name = shipping_address.last_name
        self.street1 = shipping_address.line1
        self.street2 = shipping_address.line2
        self.city = shipping_address.line4
        self.state = shipping_address.state
        self.postal_code = shipping_address.postcode
        self.country = shipping_address.country.iso_3166_1_a2.lower()


class Item(RapidBaseObject):
    REST_ATTRIBUTES = {
        'sku': RapidAttribute('SKU', 12, unicode),
        'description': RapidAttribute('Description', 26, unicode),
        'quantity': RapidAttribute('Quantity', 6, int),
        'unit_cost': RapidAttribute('UnitCost', 8, int),
        'tax': RapidAttribute('Tax', 8, int),
        'total': RapidAttribute('Total', 8, int),
    }

    def __init__(self, sku=None, description=None, quantity=None,
                 unit_cost=None, tax=None, total=None):
        self.sku = sku
        self.description = description
        self.quantity = quantity
        self.unit_cost = unit_cost
        self.tax = tax
        self.total = total


class Option(RapidBaseObject):
    REST_ATTRIBUTES = {
        u'value': RapidAttribute('Value', 254, unicode),
    }

    def __init__(self, value):
        self.value = unicode(value)


class Gateway(object):
    API_URL = u"https://api.ewaypayments.com"
    SANDBOX_URL = u"https://api.sandbox.ewaypayments.com"

    def __init__(self, api_key, password, use_sandbox=False):
        self.base_url = self.API_URL
        self.api_key = api_key
        if not self.api_key:
            raise ImproperlyConfigured(
                "API key for eWay required but can't find EWAY_API_KEY "
                "in setting. Please check and try again.")

        self.password = password
        if not self.password:
            raise ImproperlyConfigured(
                "API key for eWay required but can't find EWAY_PASSWORD "
                "in setting. Please check and try again.")

        if settings.EWAY_USE_SANDBOX:
            self.base_url = self.SANDBOX_URL

    def process_payment(self):
        raise NotImplementedError()

    def token_payment(self, order_number, total_incl_tax, redirect_url,
                      billing_address, **kwargs):

        eway_request = Request(
            method=EWAY_TOKEN_PAYMENT,
            redirect_url=redirect_url,
            payment=Payment(
                total_amount=total_incl_tax,
                # use invoice reference rather then invoice number because
                # a 16-digit restriction might be too tough
                invoice_reference=order_number,
            ),
            customer=Customer(
                billing_address=billing_address,
                **kwargs
            ),
            customer_ip=kwargs.get('customer_ip', None),
            device_id=kwargs.get('device_id', None),
            #FIXME add the shipping address properly
            #shipping_address=kwargs.get('shipping_address', None),
            items=kwargs.get('items', None),
            options=kwargs.get('options', None),
        )

        response = self.access_codes(eway_request)
        return response

    def create_token_customer(self, title, first_name, last_name,
                              country_code):
        raise NotImplementedError()

    def update_token_customer(self):
        raise NotImplementedError()

    def access_codes(self, request):
        url = "%s/AccessCodes" % self.base_url
        request_json = request.serialise()

        logger.info("requesting new access code: {0}".format(url))

        transaction = Transaction.objects.create(access_code='')
        request_log = RequestLog.objects.create(
            transaction=transaction, request=request_json)

        response = self._post(url, data=request_json)
        response = RapidResponse.from_json(response.json())

        transaction.access_code = response.access_code
        transaction.amount = request.payment.total_amount

        transaction.order_number = request.payment.invoice_reference
        transaction.save()

        request_log.method = unicode(request.method)
        request_log.url = url
        request_log.request = json.dumps(request.json(), indent=4)
        request_log.response = response.json_raw

        errors = {}
        for error in response.errors:
            errors[error.code] = error.message

        request_log.errors = json.dumps(errors)
        request_log.save()

        return response

    def get_access_code_result(self, access_code):
        request_url = "%s/AccessCode/%s" % (self.base_url, access_code)

        logger.info(
            'requesting results for access code: {0}'.format(access_code))

        transaction, __ = Transaction.objects.get_or_create(
            access_code=access_code)

        request_log = RequestLog.objects.create(
            transaction=transaction, request='{}')

        response = self._get(request_url)
        response = RapidAccessCodeResult.from_json(response.json())

        logger.info("results for access code '{0}': {1}".format(
            access_code, response.json_raw))

        transaction.order_number = response.invoice_reference
        transaction.amount = response.total_amount

        if response.transaction_id:
            transaction.transaction_id = response.transaction_id

        if response.token_customer_id:
            transaction.token_customer_id = response.token_customer_id

        transaction.status = transaction.COMPLETED
        transaction.save()

        request_log.method = "GetAccessCodeResult"
        request_log.url = request_url
        request_log.response = response.json_raw

        errors = {}
        for error in response.errors:
            errors[error.code] = error.message

        request_log.errors = json.dumps(errors)
        request_log.response_code = response.response_code.code
        request_log.response_message = response.response_code.message

        request_log.save()

        return response

    def _get(self, url):
        try:
            response = requests.get(url, auth=(self.api_key, self.password))
        except Exception as exc:
            logger.error("could not connect to eWay server: {0}".format(url))
            raise RapidError(
                'problem connecting to eWay server: %s' % (exc.message))

        if response.status_code != 200:
            logger.error("eWay responded with error {0}: {1}".format(
                response.status_code, response.reason))
            raise RapidError(
                'received error response: [%s] %s' % (
                    response.status_code, response.reason))
        return response

    def _post(self, url, data):
        headers = {'content-type': 'application/json'}
        try:
            response = requests.post(
                "%s/AccessCodes" % self.base_url,
                auth=(self.api_key, self.password), data=data, headers=headers)
        except Exception as exc:
            logger.error(
                "could not connect to eWay server: {0}".format(url),
                extra={"data": data, 'headers': headers})
            raise RapidError(
                'problem connecting to eWay server: %s' % (exc.message))

        if response.status_code != 200:
            logger.error("eWay responded with error {0}: {1}".format(
                response.status_code, response.reason),
                extra={"data": data, 'headers': headers})
            raise RapidError(
                'received error response: [%s] %s' % (
                    response.status_code, response.reason))
        return response
