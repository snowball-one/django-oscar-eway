from django.conf import settings
from django.utils.unittest import skipUnless
from django.core.urlresolvers import reverse

from oscar.apps.basket.models import Basket
from oscar.test.helpers import create_product
from oscar.apps.address.models import Country

from tests import WebTestCase

@skipUnless(
    getattr(settings, "EWAY_RUN_EXTERNAL_TESTS", False),
    "Run tests against the eWay sandbox. Disabled by default"
)


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

    def test_can_place_an_order_using_eway_payment(self):
        product = create_product()

        page = self.get(reverse(
            'catalogue:detail',
            args=(product.slug, product.id)
        ))

        page = page.forms[1].submit()
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

        page = page.follow()
        card_form = page.form
        card_form['EWAY_CARDNAME'] = 'Visa'
        card_form['EWAY_CARDNUMBER'] = '4444333322221111'
        card_form['EWAY_CARDEXPIRYMONTH'] = '12'
        card_form['EWAY_CARDEXPIRYYEAR'] = '2016'
        card_form['EWAY_CARDCVN'] = '121'
        page = card_form.submit()
        page = page.form.submit(index=1)
