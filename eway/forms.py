from datetime import date

from django import forms
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_class
from oscar.apps.payment import forms as payment_forms
from oscar.apps.payment.forms import bankcard_type

BankcardModel = get_model('payment', 'Bankcard')
Bankcard = get_class('payment.utils', 'Bankcard')


def expiry_month_choices():
        return [("%.2d" % x, "%.2d" % x) for x in xrange(1, 13)]


def expiry_year_choices(num_years=5):
    return [(x, x) for x in xrange(date.today().year, date.today().year + num_years)]


def start_month_choices():
    months = [("%.2d" % x, "%.2d" % x) for x in xrange(1, 13)]
    months.insert(0, ("", "--"))
    return months


def start_year_choices(num_years=5):
    years = [(x, x) for x in xrange(date.today().year - num_years, date.today().year + 1)]
    years.insert(0, ("", "--"))
    return years


class EwayBankcardForm(forms.Form):
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
        widget=forms.TextInput(attrs={'autocomplete':'off'}),
        label=_("Card number")
    )
    EWAY_CARDCVN = forms.RegexField(
        required=True,
        label=_("CVV Number"),
        regex=r'^\d{3,4}$',
        widget=forms.TextInput(attrs={'size': '5'}),
        help_text=_("This is the 3 or 4 digit security number on the back of your bankcard")
    )

    EWAY_CARDEXPIRYMONTH = forms.ChoiceField(
        choices=expiry_month_choices(),
        label=_("Valid to"),
        required=False
    )
    EWAY_CARDEXPIRYYEAR = forms.ChoiceField(
        choices=expiry_year_choices(5),
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

        super(EwayBankcardForm, self).__init__(*args, **kwargs)

        if user and user.is_authenticated():
            choices = self.get_existing_card_choices(user)
            self.fields['token_customer_id'].choices = choices
        else:
            self.fields['token_customer_id'].widget = forms.HiddenInput()

        if is_hidden:
            for fname in self.fields:
                self.fields[fname].widget = forms.HiddenInput()

    def get_existing_card_choices(self, user):
        existing_cards = BankcardModel.objects.filter(
            user=user,
            partner_reference__isnull=False
        )
        return [(c.partner_reference, c.number) for c in existing_cards]

    def check_is_required(self, field_name):
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
        card_number = self.data['EWAY_CARDNUMBER']
        mask_length = len(card_number)
        return {
            'card_type': bankcard_type(card_number),
            'name': self.data['EWAY_CARDNAME'],
            'number': card_number[:7] + mask_length * 'X' + card_number[-4:],
            'expiry_date': "%s/%s" %(
                self.data['EWAY_CARDEXPIRYMONTH'],
                self.data['EWAY_CARDEXPIRYYEAR'],
            ),
        }

    def get_bankcard_obj(self):
        """
        Returns a Bankcard object for use in payment processing.
        """
        kwargs = {
            'name': self.cleaned_data['EWAY_CARDNAME'],
            'card_number': self.cleaned_data['EWAY_CARDNUMBER'],
            'expiry_date': "%s/%s" %(
                self.cleaned_data['EWAY_CARDEXPIRYMONTH'],
                self.cleaned_data['EWAY_CARDEXPIRYYEAR'],
            ),
            'cvv': self.cleaned_data['EWAY_CARDCVN'],
        }
        if (self.cleaned_data['EWAY_CARDSTARTMONTH']
            and self.cleaned_data['EWAY_CARDSTARTMONTH']):
            kwargs['start_date'] = "%s/%s" % (
                self.cleaned_data['EWAY_CARDSTARTMONTH'],
                self.cleaned_data['EWAY_CARDSTARTMONTH'],
            )
        return Bankcard(**kwargs)
