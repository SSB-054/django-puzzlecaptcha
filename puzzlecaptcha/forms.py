from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.admin.forms import AdminAuthenticationForm as BaseAdminAuthenticationForm
from puzzlecaptcha.field import MathCaptchaField

class AuthenticationForm(BaseAuthenticationForm):
    captcha = MathCaptchaField()

class AdminAuthenticationForm(BaseAdminAuthenticationForm):
    captcha = MathCaptchaField()
