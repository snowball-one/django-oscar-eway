from datetime import date

from django import forms
from django.utils.translation import ugettext_lazy as _

from oscar.apps.payment import forms


def expiry_month_choices(self):
        return [("%.2d" % x, "%.2d" % x) for x in xrange(1, 13)]


def expiry_year_choices(self, num_years=5):
    return [(x, x) for x in xrange(date.today().year, date.today().year + num_years)]


def start_month_choices(self):
    months = [("%.2d" % x, "%.2d" % x) for x in xrange(1, 13)]
    months.insert(0, ("", "--"))
    return months


def start_year_choices(self, num_years=5):
    years = [(x, x) for x in xrange(date.today().year - num_years, date.today().year + 1)]
    years.insert(0, ("", "--"))
    return years


class EwayBankcardForm(forms.Form):
    token_customer_id = forms.ChoiceField(required=False, label=_("Existing cards")) 
    EWAY_CARDNAME = forms.CharField(label=_("Card type"))
    EWAY_CARDNUMBER = forms.BankcardNumberField(
        max_length=20,
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
        label=_("Expiry month")
    )
    EWAY_CARDEXPIRYYEAR = forms.ChoiceField(
        choices=expiry_year_choices(5),
        label=_("Expiry year")
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


class EwayHiddenBankcardForm(EwayBankcardForm):
    EWAY_ACCESSCODE = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(EwayHiddenBankcardForm, self).__init__(*args, **kwargs)
        for fname in self.fields:
            self.fields[fname].widget = forms.HiddenInput()
