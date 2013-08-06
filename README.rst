======================
eWay Payment for Oscar
======================

**Disclaimer:** The eWay API defined in this project is *incomplete* and
currently only provides the `Token Payment`_ using `eWay's Rapid 3.0 API`_. We
haven't had the need or time to provide any other part(s) of the API, yet.
Contributions to extend the functionality are more than welcome.


Installation
------------

You can install ``django-oscar-eway`` directly from github by running::

    $ pip install git+https://github.com/tangentlabs/django-oscar-eway.git#egg=django-oscar-eway-dev

After you have successfully installed it, you should add the app to your
``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'eway',
    )

and provide the eWay-specific settings in your ``settings.py``::

    EWAY_API_KEY = "YOUR API KEY"
    EWAY_PASSWORD = "YOUR API PASSWORD"
    EWAY_USE_SANDBOX = True
    EWAY_CURRENCY = "AUD"

To obtain access to their developer sandbox, head over to their `developer
site`_ and create an account.

Finally, you have to apply the migrations provided by the package to your
project's database. These are necessary for logging of eWay communication
during the payment process and will make tracking down errors easier::

    $ ./sandbox/manage.py migrate eway


Integrate eWay In The Checkout
------------------------------

To use only eWay as a payment method in your checkout, you only need to hook
the views provided by this package into your application. Add the following to
``urls.py`` and you should be able to use eWay and their sandbox to go through
the checkout::

    urlpatterns = patterns('',
        ...
        url(r'^checkout/eway/', include('eway.rapid.urls')),
        ...
    )

Further Documentation
---------------------

This package is still in its early stages. We'll try and provide more
documentation soon. Until then, feel free to raise an issue or ask questions
on the `django-oscar mailing list`_.


Contributing
------------

Your need more functionality, found a bug or simply want to help us make this
package better? Create a fork, make your changes and open a pull request. We'll
be thankful fort it!


License
-------

The package is released under the new BSD license.


.. _`Oscar`: http://github.com/tangentlabs/django-oscar
.. _`eWay`: http://www.eway.com.au
.. _`Token Payment`: http://www.eway.com.au/developers/api/token
.. _`eWay's Rapid 3.0 API`: http://www.eway.com.au/developers/api
.. _`developer site`: http://www.eway.com.au/developers/partners/become-a-partner
.. _`django-oscar mailing list`: https://groups.google.com/forum/#!forum/django-oscar
