from django.contrib import admin
from django.urls import path
from puzzlecaptcha.forms import AdminAuthenticationForm

admin.site.login_form = AdminAuthenticationForm
admin.site.login_template = 'puzzlecaptcha/admin_login.html'

urlpatterns = [
    path("admin/", admin.site.urls),
]
