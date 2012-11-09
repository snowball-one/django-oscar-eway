from django import forms
from django.utils.translation import ugettext_lazy as _


class EwayBankcardForm(forms.Form):
    token_customer_id = forms.ChoiceField(required=False, label=_("Existing cards"))

    EWAY_CARDNAME = forms.CharField(label=_("Card type"))
    EWAY_CARDNUMBER = forms.CharField(label=_("Card number"))
    EWAY_CARDEXPIRYMONTH = forms.CharField(label=_("Expiry month"))
    EWAY_CARDEXPIRYYEAR = forms.CharField(label=_("Expiry year"))

    EWAY_CARDSTARTMONTH = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    EWAY_CARDENDMONTH = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    EWAY_CARDISSUENUMBER = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    EWAY_CARDCVN = forms.CharField(label=_("CVN"))


class EwayHiddenBankcardForm(EwayBankcardForm):
    EWAY_ACCESSCODE = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(EwayHiddenBankcardForm, self).__init__(*args, **kwargs)
        for fname in self.fields:
            self.fields[fname].widget = forms.HiddenInput()
