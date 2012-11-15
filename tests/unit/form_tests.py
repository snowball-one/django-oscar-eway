from django.test import TestCase

from eway.forms import BankcardForm


class TestBankcardForm(TestCase):

    def test_obfuscates_card_number_correctly(self):
        number = '4444333322221111'
        self.assertEquals(
            BankcardForm.get_obfuscated_card_number(number),
            '444433XXXXXX1111'
        )

    def test_obfuscates_card_number_with_short_number(self):
        number = '4444'
        self.assertEquals(
            BankcardForm.get_obfuscated_card_number(number),
            'XXXX'
        )
