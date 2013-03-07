from decimal import Decimal as D

from django.utils import simplejson as json

from django.test import TestCase
from django.db.models import get_model

from eway import gateway


Country = get_model('address', 'Country')
BillingAddress = get_model('order', 'BillingAddress')
ShippingAddress = get_model('order', 'ShippingAddress')


class TestAnOptionObject(TestCase):

    def test_can_be_serialised_to_json(self):
        option = gateway.Option(u'test_value')
        self.assertEquals(option.serialise(), u'{"Value": "test_value"}')


class TestAnItemObject(TestCase):

    def test_can_be_serialised_to_json(self):
        json_sample = """{"SKU": "SKU1", "Description": "Description1"}"""

        item = gateway.Item(sku='SKU1', description="Description1")
        self.assertEquals(item.serialise(), json_sample)


class TestAShippingAddressObject(TestCase):

    def setUp(self):
        super(TestAShippingAddressObject, self).setUp()
        self.country = Country.objects.create(
            name="AUSTRALIA",
            iso_3166_1_a2="au",
            iso_3166_1_a3="aus",
            iso_3166_1_numeric=36,
            printable_name="Australia",
        )

    def test_can_be_serialised_to_json(self):
        json_sample = json.dumps({
            "ShippingMethod": gateway.EWAY_SHIPPING_LOWCOST,
            "FirstName": "Peter",
            "LastName": "Griffin",
            "Street1": "31 Spooner Street",
            "City": "Quahog",
            "State": "Victoria",
            "PostalCode": "3070",
            "Country": "au",
        })
        address = ShippingAddress.objects.create(
            first_name="Peter",
            last_name="Griffin",
            line1="31 Spooner Street",
            line4="Quahog",
            state="Victoria",
            country=self.country,
            postcode='3070',
        )

        shipping_address = gateway.ShippingAddress(
            shipping_method=gateway.EWAY_SHIPPING_LOWCOST,
            shipping_address=address
        )

        self.assertItemsEqual(shipping_address.serialise(), json_sample)


class TestARequest(TestCase):

    def test_can_be_serialised_to_json(self):
        self.maxDiff = None
        sample_json = {
            "Customer": {
                "TokenCustomerID": 987654321000,
                "Reference": "A12345",
                "Title": "Mr.",
                "FirstName": "John",
                "LastName": "Smith",
                "CompanyName": "Demo Shop 123",
                "JobDescription": "Developer",
                "Street1": "Level 5",
                "Street2": "369 Queen Street",
                "City": "Auckland",
                "State": "",
                "PostalCode": "1010",
                "Country": "nz",
                "Email": "sales@demoshop123.com",
                "Phone": "09 889 0986",
                "Mobile": "09 889 0986"
            },
            "Options": [
                {
                    "Value": "Option1"
                },
                {
                    "Value": "Option2"
                },
                {
                    "Value": "Option3"
                }
            ],
            "RedirectUrl": "http://mysite.co.nz/Results",
            "Method": "UpdateTokenCustomer",
            "DeviceID": "D1234",
            "CustomerIP": "127.0.0.1"
        }
        options = [
            gateway.Option("Option1"),
            gateway.Option("Option2"),
            gateway.Option("Option3"),
        ]

        rapid_request = gateway.Request(
            redirect_url="http://mysite.co.nz/Results",
            method=gateway.EWAY_UPDATE_TOKEN_CUSTOMER,
            device_id="D1234",
            customer_ip="127.0.0.1",
            options=options,
        )

        country = Country.objects.create(
            name="NEW ZEALAND",
            iso_3166_1_a2="NZ",
            iso_3166_1_a3="NZL",
            iso_3166_1_numeric=554,
            printable_name="New Zealand",
        )
        address = BillingAddress.objects.create(
            title="Mr.",
            first_name="John",
            last_name="Smith",
            line1="Level 5",
            line2="369 Queen Street",
            line4="Auckland",
            state="",
            postcode="1010",
            country=country,
        )

        rapid_request.customer = gateway.Customer(
            token_customer_id=987654321000,
            reference="A12345",
            email="sales@demoshop123.com",
            company_name="Demo Shop 123",
            job_description="Developer",
            address=address,
            phone="09 889 0986",
            mobile="09 889 0986",
        )

        self.assertItemsEqual(rapid_request.json(), sample_json)


class TestTheAccessCodeResult(TestCase):

    def test_can_be_created_from_json(self):
        json_sample = json.loads("""{
"AccessCode": "nvt0mwZXN9aU43rsIRPlve3aNziYqA7VHLT3RurzaEvm",
"AuthorisationCode": "592733",
"ResponseCode": "00",
"ResponseMessage": "A2000",
"InvoiceNumber": "Inv 21540",
"InvoiceReference": "513456",
"TotalAmount": 139,
"TransactionID": 9868584,
"TransactionStatus": true,
"TokenCustomerID": 987654321000,
"BeagleScore": 0,
"Options": [
{
"Value": "Option1"
},
{
"Value": "Option2"
},
{
"Value": "Option3"
}
],
"Verification": {
"CVN": 0,
"Address": 0,
"Email": 0,
"Mobile": 0,
"Phone": 0
},
"Errors": null
}""")

        result = gateway.RapidAccessCodeResult.from_json(json_sample)
        self.assertEquals(result.total_amount, D('1.39'))
        self.assertEquals(result.authorisation_code, "592733")
        self.assertEquals(
            result.access_code,
            "nvt0mwZXN9aU43rsIRPlve3aNziYqA7VHLT3RurzaEvm"
        )
        self.assertEquals(result.errors, None)
        self.assertEquals(len(result.response_message), 1)
        self.assertEquals(result.response_message[0].code, "A2000")
        self.assertEquals(result.response_code.code, '00')

        self.assertEquals(result.transaction_id, 9868584)
        self.assertEquals(result.transaction_status, True)

        verification = result.verification
        self.assertEquals(verification.cvn, 0)
        self.assertEquals(verification.address, 0)
        self.assertEquals(verification.email, 0)
        self.assertEquals(verification.mobile, 0)
        self.assertEquals(verification.phone, 0)


from mock import MagicMock


class TestAccessCodeResponse(TestCase):

    def test_containing_errors_is_logged_correctly(self):
        json_data = json.loads("""{"Customer": {"City": null, "FirstName": null, "Title": null, "LastName": null, "CardStartYear": null, "Comments": null, "State": null, "JobDescription": null, "TokenCustomerID": null, "Email": null, "Fax": null, "Phone": null, "Street1": null, "Street2": null, "Mobile": null, "CardNumber": null, "CardExpiryMonth": null, "Url": null, "Country": null, "CardExpiryYear": null, "CardIssueNumber": null, "CardStartMonth": null, "PostalCode": null, "Reference": null, "CompanyName": null, "CardName": null, "IsActive": false}, "FormActionURL": null, "Errors": "V6042,V6043", "Payment": {"InvoiceReference": "100215", "TotalAmount": 2590, "CurrencyCode": "AUD", "InvoiceNumber": null, "InvoiceDescription": null}, "AccessCode": null}""")
        RequestsResponse = MagicMock(name='RequestsResponse')
        RequestsResponse.json = MagicMock(return_value=json_data)

        eway = gateway.Gateway('no_key', 'no_password')
        eway._post = MagicMock(name='_post')
        eway._post.return_value =  RequestsResponse

        response = eway.access_codes(gateway.Request(
            redirect_url='http://test.example.com/',
            method=gateway.EWAY_TOKEN_PAYMENT,
            payment=gateway.Payment(
                total_amount=D('25.90'),
                invoice_reference='100215',
                currency_code="AUD",
            )
        ))
        txn = gateway.EwayTransaction.objects.get(
            order_number=response.payment.invoice_reference
        )
        self.assertEquals(
            txn.response_json,
            json.dumps(RequestsResponse.json(), indent=4)
        )
        self.assertEquals(gateway.EwayResponseCode.objects.count(), 2)
