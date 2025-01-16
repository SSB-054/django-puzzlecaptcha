from django import forms
import uuid
import base64
from io import BytesIO
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from django.core import cache
from django.core.exceptions import ValidationError
from django.conf import settings


DEFAULT_PUZZLECAPTCHA = {
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

if hasattr(settings, "PUZZLECAPTCHA"):
    DEFAULT_PUZZLECAPTCHA.update(settings.PUZZLECAPTCHA)


class MathCaptchaWidget(forms.MultiWidget):
    cache = cache.caches[DEFAULT_PUZZLECAPTCHA["CAPTCHA_CACHE_BACKEND"]]
    font = ImageFont.load_default(size=DEFAULT_PUZZLECAPTCHA["CAPTCHA_FONT_SIZE"])
    template_name = "puzzlecaptcha/captcha.html"

    def __init__(self, *args, **kwargs):
        widgets = [
            forms.HiddenInput(),  # For UUID
            forms.HiddenInput(),  # For image data
            forms.NumberInput(attrs={"placeholder": "Enter the result"}),
        ]
        widgets[1].template_name = "puzzlecaptcha/captcha_image.html"
        widgets[2].template_name = "puzzlecaptcha/captcha_result.html"
        super().__init__(*args, **kwargs, widgets=widgets)

    def generate_math_problem(self):
        num1 = random.randint(1, 9)
        num2 = random.randint(1, 9)
        operator = random.choice(["+", "*"])

        if operator == "+":
            result = num1 + num2
        else:
            result = num1 * num2

        problem = f"{num1} {operator} {num2}"
        return problem, result

    def generate_captcha(self, text):

        img = Image.new(
            "RGB",
            DEFAULT_PUZZLECAPTCHA["CAPTCHA_IMAGE_SIZE"],
            color=DEFAULT_PUZZLECAPTCHA["CAPTCHA_BACKGROUND_COLOR"],
        )
        d = ImageDraw.Draw(img)

        d.text(
            (random.randint(2, 50), random.randint(2, 20)),
            text,
            fill=DEFAULT_PUZZLECAPTCHA["CAPTCHA_FOREGROUND_COLOR"],
            font=self.font,
        )

        for _ in range(DEFAULT_PUZZLECAPTCHA["CAPTCHA_NOISE_LINES"]):
            x1 = random.randint(0, DEFAULT_PUZZLECAPTCHA["CAPTCHA_IMAGE_SIZE"][0])
            y1 = random.randint(0, DEFAULT_PUZZLECAPTCHA["CAPTCHA_IMAGE_SIZE"][1])
            x2 = random.randint(0, DEFAULT_PUZZLECAPTCHA["CAPTCHA_IMAGE_SIZE"][0])
            y2 = random.randint(0, DEFAULT_PUZZLECAPTCHA["CAPTCHA_IMAGE_SIZE"][1])
            d.line(
                [(x1, y1), (x2, y2)],
                fill=DEFAULT_PUZZLECAPTCHA["CAPTCHA_FOREGROUND_COLOR"],
                width=DEFAULT_PUZZLECAPTCHA["CAPTCHA_NOISE_LINES_WIDTH"],
            )
        # Convert the image to a numpy array
        np_image = np.array(img)

        # Add noise to the image
        noise = np.random.randint(-150, 150, np_image.shape)
        noisy_image = np.clip(np_image + noise, 0, 255).astype(np.uint8)

        # Convert the numpy array back to an image
        noisy_image = Image.fromarray(noisy_image)

        # Convert to base64
        buffer = BytesIO()
        noisy_image.save(buffer, format="JPEG")

        return str(uuid.uuid4()), base64.b64encode(buffer.getvalue()).decode()

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        problem_statement, result = self.generate_math_problem()
        problem_uuid, image_data = self.generate_captcha(problem_statement + "=")
        self.cache.set(
            f"{DEFAULT_PUZZLECAPTCHA['CAPTCHA_CACHE_PREFIX']}_{problem_uuid}",
            str(result),
            DEFAULT_PUZZLECAPTCHA["CAPTCHA_TIMEOUT"],
        )
        ctx["widget"]["subwidgets"][0]["value"] = problem_uuid
        ctx["widget"]["subwidgets"][1]["value"] = f"data:image/jpeg;base64,{image_data}"
        ctx["widget"]["subwidgets"][2]["value"] = ""
        return ctx

    def decompress(self, value):
        if value:
            return value
        return [None, None, None]


class MathCaptchaField(forms.Field):
    cache = cache.caches[DEFAULT_PUZZLECAPTCHA["CAPTCHA_CACHE_BACKEND"]]
    widget = MathCaptchaWidget
    default_error_messages = {
        "captcha_invalid": ("Error verifying CAPTCHA, please try again."),
        "captcha_error": ("Error verifying CAPTCHA, please try again."),
    }

    def clean(self, value):
        if not value:
            raise ValidationError("This field is required.")

        uuid_value, image_data, answer = value
        # Get stored result from cache
        stored_result = cache.get(f"captcha_{str(uuid_value)}")
        if not stored_result:
            raise ValidationError("Captcha has expired. Please try again.")

        # Clean up cache
        self.cache.delete(f"captcha_{uuid_value}")

        # Compare results
        try:
            if str(answer).strip() != stored_result.strip():
                raise ValidationError("Incorrect captcha answer. Please try again.")
        except (ValueError, AttributeError):
            raise ValidationError("Invalid input. Please enter a number.")

        return value
