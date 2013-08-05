from httpretty import HTTPretty
from httpretty import httprettified

from django.db.models import get_model
from django.core.urlresolvers import reverse

from oscar.core.loading import get_class
from oscar.apps.basket.models import Basket
from oscar.apps.address.models import Country
from oscar_testsupport.testcases import WebTestCase
from oscar_testsupport.factories import create_product

Order = get_model('order', 'Order')
OrderNumberGenerator = get_class('order.utils', 'OrderNumberGenerator')


class MockRequestResponse(object):
    json = {}
    status_code = 200
    reason = 'OK'


class TestARegisteredUser(WebTestCase):
    is_anonymous = False

    def setUp(self):
        super(TestARegisteredUser, self).setUp()
        self.country = Country.objects.create(
            name='AUSTRALIA',
            iso_3166_1_a2='AU',
            iso_3166_1_a3='AUS',
            iso_3166_1_numeric=36,
            printable_name="Australia",
            is_shipping_country=True
        )
        self.user.first_name = "Peter"
        self.user.last_name = "Griffin"
        self.user.save()

    def go_to_payment_detail_page(self):
        product = create_product()

        page = self.get(reverse(
            'catalogue:detail',
            args=(product.slug, product.id)
        ))

        page = page.forms[2].submit()
        self.assertEquals(Basket.objects.count(), 1)

        page = self.get(reverse('checkout:index'))
        self.assertRedirects(page, reverse('checkout:shipping-address'))

        shipping_form = page.follow().form
        shipping_form['title'] = ''
        shipping_form['first_name'] = "Peter"
        shipping_form['last_name'] = "Griffin"
        shipping_form['line1'] = "31 Spooner St"
        shipping_form['line4'] = "Quahog"
        shipping_form['state'] = "Victoria"
        shipping_form['country'] = 'AU'
        shipping_form['postcode'] = "3070"
        shipping_form['phone_number'] = "+61 (3) 121 121"
        shipping_form['notes'] = "Some additional notes"
        page = shipping_form.submit().follow().follow()

        self.assertRedirects(page, reverse('checkout:payment-details'))
        return page.follow()

    @httprettified
    def test_can_place_an_order_using_eway_payment(self):
        page = self.go_to_payment_detail_page()

        access_code = "nvt0mwZXN9aU43rsIRPlve3aNziYqA7VHLT3RurzaEvm"
        generator = OrderNumberGenerator()
        order_number = generator.order_number(Basket.objects.all()[0])

        HTTPretty.register_uri(
            HTTPretty.POST,
            "https://api.sandbox.ewaypayments.com/AccessCodes",
            body=TOKEN_PAYMENT_AC_RESPONSE % {
                'access_code': access_code,
                'token_customer_id': '',
                'card_number': '444433XXXXXX1111',
                'expiry_month': '12',
                'expiry_year': '18',
                'card_name': 'Peter Griffin',
                'form_action_url': "http://localhost:8000/test",
                'order_number': order_number,
            },
            content_type='text/json',
        )

        card_form = page.form
        card_form['EWAY_CARDNAME'] = 'Visa'
        card_form['EWAY_CARDNUMBER'] = '4444333322221111'
        card_form['EWAY_CARDEXPIRYMONTH'] = '12'
        card_form['EWAY_CARDEXPIRYYEAR'] = '2016'
        card_form['EWAY_CARDCVN'] = '121'

        page = card_form.submit()

        self.assertContains(page, 'EWAY_CARDNUMBER')
        self.assertContains(page, '4444333322221111')
        self.assertContains(page, access_code)

        HTTPretty.register_uri(
            HTTPretty.GET,
            "https://api.sandbox.ewaypayments.com/AccessCode/%s" % access_code,
            body=GET_ACCESS_CODE_RESPONSE % {
                'access_code': access_code,
                'token_customer_id': '',
                'order_number': order_number,
            },
            content_type='text/json',
        )

        page = self.get(reverse('eway-rapid-response'), params={
            'AccessCode': access_code,
        })

        self.assertRedirects(page, reverse("checkout:thank-you"))
        self.assertEquals(Order.objects.count(), 1)

        order = Order.objects.get(number=order_number)
        self.assertEquals(order.user, self.user)

        #page = page.follow()


GET_ACCESS_CODE_RESPONSE = """{
    "AccessCode": "%(access_code)s",
    "AuthorisationCode": "592733",
    "ResponseCode": "00",
    "ResponseMessage": "A2000",
    "InvoiceNumber": null,
    "InvoiceReference": %(order_number)s,
    "TotalAmount": 30000,
    "TransactionID": 9868584,
    "TransactionStatus": true,
    "TokenCustomerID": "%(token_customer_id)s",
    "BeagleScore": 0,
    "Options": [],
    "Verification": {
        "CVN": 0,
        "Address": 0,
        "Email": 0,
        "Mobile": 0,
        "Phone": 0
    },
    "Errors": null
}"""

TOKEN_PAYMENT_AC_RESPONSE = """{
    "Customer": {
        "TokenCustomerID": "%(token_customer_id)s",
        "Reference": null,
        "Title": "Prof.",
        "FirstName": "Peter",
        "LastName": "Griffin",
        "CompanyName": "",
        "JobDescription": "",
        "Street1": "31 Spooner St",
        "Street2": "",
        "City": "Quahog",
        "State": "Victoria",
        "PostalCode": "3006",
        "Country": "au",
        "Email": "",
        "Phone": "",
        "Mobile": "",
        "Comments": "",
        "Fax": "",
        "Url": "",
        "CardNumber": "%(card_number)s",
        "CardStartMonth": "",
        "CardStartYear": "",
        "CardIssueNumber": "",
        "CardName": "%(card_name)s",
        "CardExpiryMonth": "%(expiry_month)s",
        "CardExpiryYear": "%(expiry_year)s"
    },
    "Payment": {
        "TotalAmount": 30000,
        "InvoiceNumber": null,
        "InvoiceDescription": null,
        "InvoiceReference": "%(order_number)s",
        "CurrencyCode": "AUD"
    },
    "AccessCode": "%(access_code)s",
    "FormActionURL": "https://secure.ewaypayments.com/AccessCode/%(access_code)s",
    "Errors": null
}"""
