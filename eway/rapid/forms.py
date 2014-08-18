from datetime import date

from django import forms
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _

from oscar.apps.payment import forms as payment_forms

BankcardModel = get_model('payment', 'Bankcard')

try:
    from oscar.apps.payment.bankcards import bankcard_type
    Bankcard = BankcardModel
except ImportError:
    from oscar.apps.payment.forms import bankcard_type
    from oscar.core.loading import get_class
    Bankcard = get_class('payment.utils', 'Bankcard')


def expiry_month_choices():
    """
    Get a list of numeric month as tuples (*numeric month*, *numeric month*).
    The months are numbered one through 12 according to ISO standard.
    """
    return [("%.2d" % x, "%.2d" % x) for x in xrange(1, 13)]


def expiry_year_choices(num_years=5):
    """
    Get a list of years starting with the current year and going
    *num_years* into the future. The returned list contains
    tuples of the form (*numeric year*, *numeric lyear*) with years
    in 4-digit notation, e.g. 2016.
    """
    return [(x, x) for x in xrange(date.today().year,
                                   date.today().year + num_years)]


def start_month_choices():
    """
    Get a list of numeric month as tuples (*numeric month*, *numeric month*).
    The months are numbered one through 12 according to ISO standard. The first
    item in the list is '--' to allow for not selecting a month.
    """
    return [("", _("--"))] + expiry_month_choices()


def start_year_choices(num_years=5):
    """
    Get a list of years for the starting date of a bank card with the
    range of years  starting *num_years* ago ranging up to the current
    year. The returned list contains tuples of the form (*numeric year*,
    *numeric year*) in 4-digit notation, e.g. 2016. The first item in the
    list is '--' to allow for not selecting a year.
    """
    years = [("", _("--"))]
    for year in xrange(date.today().year - num_years, date.today().year + 1):
        years.append((year, year))
    return years


class BankcardForm(forms.Form):
    """
    A form specific for eWay as specified in the Rapid 3.0 API documentation.
    Submitting the details directly to eWay requires the form's input field
    to have the exact names specified in the API docs. The field names in this
    form therefore violate PEP8 knowingly to remain explicit and not introduce
    too much magic.
    """
    token_customer_id = forms.ChoiceField(
        required=False,
        label=_("Existing cards"),
        widget=forms.RadioSelect(),
    )

    EWAY_ACCESSCODE = forms.CharField(
        label=_("Access code"),
        widget=forms.HiddenInput(),
        required=False,
    )
    EWAY_CARDNAME = forms.CharField(
        required=False,
        label=_("Name"),
        help_text=_("Your name as it appears on the card")
    )
    EWAY_CARDNUMBER = payment_forms.BankcardNumberField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
        label=_("Card number")
    )
    EWAY_CARDCVN = forms.RegexField(
        required=True,
        label=_("CVV Number"),
        regex=r'^\d{3,4}$',
        widget=forms.TextInput(attrs={'size': '5'}),
        help_text=_("This is the 3 or 4 digit security number on the back of "
                    "your bankcard")
    )

    EWAY_CARDEXPIRYMONTH = forms.ChoiceField(
        choices=expiry_month_choices(),
        label=_("Valid to"),
        required=False
    )
    EWAY_CARDEXPIRYYEAR = forms.ChoiceField(
        choices=expiry_year_choices(6),
        label="",
        required=False
    )

    # these fields are used in the UK only
    EWAY_CARDSTARTMONTH = forms.ChoiceField(
        choices=start_month_choices(),
        widget=forms.HiddenInput(),
        required=False
    )
    EWAY_CARDSTARTYEAR = forms.ChoiceField(
        choices=start_year_choices(),
        widget=forms.HiddenInput(),
        required=False
    )
    EWAY_CARDISSUENUMBER = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_hidden = kwargs.pop('is_hidden', None)

        super(BankcardForm, self).__init__(*args, **kwargs)

        if user and user.is_authenticated():
            choices = self.get_existing_cards(user)
            self.fields['token_customer_id'].choices = choices
        else:
            self.fields['token_customer_id'].widget = forms.HiddenInput()

        if is_hidden:
            for fname in self.fields:
                self.fields[fname].widget = forms.HiddenInput()

    def get_existing_cards(self, user):
        """
        Get a list of tuples for existing cards of the specified *user*.
        Each tuple contains the ``token_customer_id`` and the obfuscated
        bankcard number.
        """
        existing_cards = BankcardModel.objects.filter(
            user=user,
            partner_reference__isnull=False
        )
        return [(c.partner_reference, c.number) for c in existing_cards]

    def check_is_required(self, field_name):
        """
        Check if the field with *field_name* is required based on the
        selection of a ``token_customer_id`` indicating the use of an
        existing payment.
        A field is required if no ``token_customer_id`` is provided
        and having the field *field_name* empty will raise a
        ``ValidationError``.
        """
        data = self.cleaned_data[field_name]
        if not data and not self.cleaned_data['token_customer_id']:
            raise forms.ValidationError(_("This field is required"))
        return data

    def clean_EWAY_CARDNAME(self):
        return self.check_is_required('EWAY_CARDNAME')

    def clean_EWAY_CARDNUMBER(self):
        return self.check_is_required('EWAY_CARDNUMBER')

    def clean_EWAY_CARDEXPIRYMONTH(self):
        return self.check_is_required('EWAY_CARDEXPIRYMONTH')

    def clean_EWAY_CARDEXPIRYYEAR(self):
        return self.check_is_required('EWAY_CARDEXPIRYYEAR')

    def get_obfuscated_kwargs(self):
        """
        Get a dictionary containing the obfuscated bank card details used
        in the eway form. The card number is **not** stored in plain
        text but is obfuscated in the same way eWay obfuscates their card
        numers (first 6 and last 4 digits visible).
        """
        card_number = self.data.get('EWAY_CARDNUMBER', '')
        return {
            'card_type': bankcard_type(card_number) or '',
            'name': self.data.get('EWAY_CARDNAME', ''),
            'number': self.get_obfuscated_card_number(card_number),
            'expiry_date': "%s/%s" % (
                self.data.get('EWAY_CARDEXPIRYMONTH', ''),
                self.data.get('EWAY_CARDEXPIRYYEAR', ''),
            ),
        }

    @classmethod
    def get_obfuscated_card_number(cls, number):
        """
        Get an obfuscated version of the bankcard *number* with several
        digits replaced with 'X'. We obfuscate using the same method as
        eWay uses which shows the first six and the last four digits. For
        a credit card '4444333322221111' this method returns
        '444433XXXXXX1111'. If *number* has less than 11 digits, the number
        is obfuscated completely to avoid accidentally storing a complete
        bankcard number.
        """
        # if the number is shorter than 10 digits the whole number would
        # show up, in this special case we obfuscate every digit just to
        # be sure that we don't accidentally store actual credit card data
        if len(number) < 11:
            return len(number) * 'X'

        # eway uses 10 visible digits in their obfuscation, we replicate
        # this here to stay compliant
        start, masked, end = number[:6], number[6:-4], number[-4:]
        return "".join([start, len(masked) * 'X', end])

    def get_bankcard_obj(self):
        """
        Returns a Bankcard object for use in payment processing.
        """
        kwargs = {
            'name': self.cleaned_data['EWAY_CARDNAME'],
            'card_number': self.cleaned_data['EWAY_CARDNUMBER'],
            'expiry_date': "%s/%s" % (
                self.cleaned_data['EWAY_CARDEXPIRYMONTH'],
                self.cleaned_data['EWAY_CARDEXPIRYYEAR'],
            ),
            'cvv': self.cleaned_data['EWAY_CARDCVN'],
        }
        if (self.cleaned_data['EWAY_CARDSTARTMONTH']
           and self.cleaned_data['EWAY_CARDSTARTMONTH']):
            kwargs['start_date'] = "%s/%s" % (
                self.cleaned_data['EWAY_CARDSTARTMONTH'],
                self.cleaned_data['EWAY_CARDSTARTMONTH'])
        return Bankcard(**kwargs)
