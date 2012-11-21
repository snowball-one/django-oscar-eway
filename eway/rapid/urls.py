from django.conf.urls.defaults import *

from eway.rapid import views


urlpatterns = patterns('',
    url(
        r'^preview/$',
        views.RapidResponseView.as_view(preview=True),
        name='eway-rapid-response'
   ),
)
