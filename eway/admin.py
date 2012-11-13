from django.contrib import admin
from django.db.models import get_model


EwayTransaction = get_model('eway', 'EwayTransaction')
EwayResponseCode = get_model('eway', 'EwayResponseCode')


class ErrorInline(admin.StackedInline):
    model = EwayResponseCode.transactions.through

class EwayResponseCodeAdmin(admin.ModelAdmin):
    inlines = [
        ErrorInline,
    ]
    exclude = ('transactions',)

class EwayTransactionAdmin(admin.ModelAdmin):
    inlines = [
        ErrorInline,
    ]


admin.site.register(EwayTransaction, EwayTransactionAdmin)
admin.site.register(EwayResponseCode)
