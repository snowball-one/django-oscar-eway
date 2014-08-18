from django.test import TestCase

from eway.rapid.forms import BankcardForm


def test_obfuscates_card_number_correctly():
    card_number = BankcardForm.get_obfuscated_card_number('4444333322221111')
    assert card_number == '444433XXXXXX1111'


def test_obfuscates_card_number_with_short_number():
    card_number = BankcardForm.get_obfuscated_card_number('4444')
    assert card_number == 'XXXX'


def test_get_obfuscated_kwargs_empty_if_no_data():
    form = BankcardForm()
    kwargs = form.get_obfuscated_kwargs()
    assert kwargs['card_type'] == ''
    assert kwargs['name'] == ''
    assert kwargs['number'] == ''
    assert kwargs['expiry_date'] == '/'


def test_get_obfuscated_kwargs_returns_correct_data():
    form = BankcardForm(data={
        'EWAY_CARDNUMBER': '4444333322221111',
        'EWAY_CARDNAME': 'Peter Griffin',
        'EWAY_CARDEXPIRYMONTH': '12',
        'EWAY_CARDEXPIRYYEAR': '19'})
    kwargs = form.get_obfuscated_kwargs()
    assert kwargs['card_type'] == 'Visa'
    assert kwargs['name'] == 'Peter Griffin'
    assert kwargs['number'] == '444433XXXXXX1111'
    assert kwargs['expiry_date'] == '12/19'
