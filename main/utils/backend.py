from django.db.models import Q

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class PhoneAndEmailBackend(ModelBackend):
    def authenticate(self, request, email=None, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            _filter = Q(email__iexact=email)
            if email.isnumeric():
                _filter = Q(phone_number=email)
            user = UserModel.objects.get(_filter)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
