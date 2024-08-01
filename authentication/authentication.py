from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

User = get_user_model()


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
        except ObjectDoesNotExist:
            return None
        except MultipleObjectsReturned:
            raise ValueError('Multiple accounts found with this email.')
        else:
            if user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        try:
            obj = User.objects.get(pk=user_id)
            print("========111111", obj)
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            print("-@@@@@@@", User)
            return None
