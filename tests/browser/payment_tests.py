# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest

from django.db.models import get_model
from django.core.urlresolvers import reverse

from oscar_testsupport.factories import create_product

User = get_model('auth', 'User')
Basket = get_model('basket', 'Basket')
Country = get_model('address', 'Country')
Order = get_model('order', 'Order')

Transaction = get_model('eway', 'Transaction')
RequestLog = get_model('eway', 'RequestLog')


@pytest.fixture
def shipping_country(transactional_db):
    return Country.objects.create(
        name='AUSTRALIA', iso_3166_1_a2='AU', iso_3166_1_a3='AUS',
        iso_3166_1_numeric=36, printable_name="Australia",
        is_shipping_country=True)


@pytest.fixture
def customer_password():
    return 'somefancypassword'


@pytest.fixture
def customer(transactional_db, customer_password):
    user = User.objects.create_user(
        username='testuser', email='testuser@buymore.com',
        password=customer_password)

    user.first_name = 'Peter'
    user.last_name = 'Griffin'
    user.save()

    return user


@pytest.mark.browser
def test_registered_user_can_make_payment(browser, live_server, customer,
                                          customer_password, shipping_country):
    browser.visit(live_server.url + reverse('customer:login'))
    browser.fill_form({
        'login-username': customer.email,
        'login-password': customer_password})

    browser.find_by_name('login_submit').click()
    assert browser.is_text_present('Logout')

    product = create_product()
    browser.visit(live_server.url + product.get_absolute_url())
    assert browser.is_text_present(product.title)

    buttons = browser.find_by_css('[value="Add to basket"]')
    try:
        button = buttons[0]
    except IndexError:
        button = buttons
    button.click()

    assert browser.is_text_present(
        "{} has been added to your basket.".format(product.title), wait_time=2)

    browser.visit(live_server.url + reverse('checkout:index'))

    form_data = {
        'title': '', 'first_name': "Peter", 'last_name': "Griffin",
        'line1': "31 Spooner St", 'line4': "Quahog", 'state': "Victoria",
        'postcode': "3070", 'phone_number': "+61 (0)3 1121 1121",
        'notes': "Some additional notes"}

    # the country field will be hidden in Oscar 0.6+
    if browser.is_element_present_by_name('country'):
        form_data['country'] = 'AU'

    browser.fill_form(form_data)
    browser.find_by_css('[type=submit]').click()
    assert browser.is_text_present('Enter payment details')

    browser.fill_form({
        'EWAY_CARDNAME': 'Peter Griffin',
        'EWAY_CARDNUMBER': '4444333322221111', 'EWAY_CARDEXPIRYMONTH': '12',
        'EWAY_CARDEXPIRYYEAR': '2016', 'EWAY_CARDCVN': '121'})
    browser.find_by_css('[type=submit]').click()
    assert browser.is_text_present('Please review the information')

    browser.find_by_id("place-order").click()

    assert Order.objects.count() == 1
    order = Order.objects.all()[0]
    assert browser.is_text_present('{}'.format(order.number))

    assert Transaction.objects.count() == 1
    transaction = Transaction.objects.all()[0]

    assert transaction.transaction_id != ''
    assert transaction.access_code != ''
    assert transaction.status == transaction.COMPLETED
    assert browser.is_text_present(transaction.transaction_id)

    assert RequestLog.objects.count() == 2

    browser.quit()
