from django.contrib.auth.models import User

from django_webtest import WebTest


class WebTestCase(WebTest):
    is_staff = False
    is_anonymous = True
    username = 'testuser'
    email = 'testuser@buymore.com'
    password = 'somefancypassword'

    def setUp(self):
        self.user = None
        if not self.is_anonymous or self.is_staff:
            self.user = User.objects.create_user(self.username, self.email,
                                                 self.password)
            self.user.is_staff = self.is_staff
            self.user.save()

    def get(self, url, **kwargs):
        kwargs.setdefault('user', self.user)
        return self.app.get(url, **kwargs)

    def post(self, url, **kwargs):
        kwargs.setdefault('user', self.user)
        return self.app.post(url, **kwargs)
