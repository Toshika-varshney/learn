import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if password is None or password.strip() == "":
            raise ValidationError(
                _("Enter password"),
                code="password_blank",
            )

        if len(password) < 8:
            raise ValidationError(
                _("Password must be at least 8 characters long"),
                code='password_too_short'
            )

        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter"),
                code='password_no_upper'
            )

        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter"),
                code='password_no_lower'
            )

        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("Password must contain at least one number"),
                code='password_no_number'
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Password must contain at least one special character"),
                code='password_no_special'
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 8 characters, "
            "including uppercase, lowercase, number and special character."
        )
