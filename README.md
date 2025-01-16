# django-puzzlecaptcha
PuzzleCaptcha: Simplified Math CAPTCHA Using Pillow Image Library

![Preview](./img/preview.png?raw=true)



## Features

- Easy integration with Django projects
- Use pillow & numpy to generate image
- Customizable configuration

## Installation

### 1. Install the Package

```bash
pip install django-puzzlecaptcha
```

### 2. Configure Django Settings

Add `puzzlecaptcha` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'puzzlecaptcha',
    ...
]
```

### 3. Configuration
In your `settings.py`, you can customize the puzzlecaptcha behavior:
```
PUZZLECAPTCHA = {
    "CAPTCHA_FONT_SIZE": 35,
    "CAPTCHA_IMAGE_SIZE": (150, 50),
    "CAPTCHA_NOISE_LINES": 20,
    "CAPTCHA_NOISE_LINES_WIDTH": 2,
    "CAPTCHA_NOISE_COLOR": "black",
    "CAPTCHA_FOREGROUND_COLOR": "black",
    "CAPTCHA_BACKGROUND_COLOR": "white",
    "CAPTCHA_CACHE_PREFIX": "puzzlecaptcha",
    "CAPTCHA_CACHE_BACKEND": "default",
    "CAPTCHA_TIMEOUT": 300,
}
```

### 4. To Enable on Admin Login Form (Optional)
In your project's `urls.py`:

```python
from puzzlecaptcha.forms import AdminAuthenticationForm

admin.site.login_form = AdminAuthenticationForm
admin.site.login_template = 'puzzlecaptcha/admin_login.html'

urlpatterns = [
    path("admin/", admin.site.urls),
    ....
]
```

## Usage Example

```python
from puzzlecaptcha.field import MathCaptchaField

class AuthenticationForm(form.Form):
    captcha = MathCaptchaField()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/surajsinghbisht054/django-puzzlecaptcha/issues) on GitHub.
