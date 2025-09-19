from django.contrib.auth import authenticate
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.fields import SerializerMethodField, EmailField, CharField
from rest_framework.exceptions import ValidationError

from .models import CustomUser


class UserProfileSerializer(ModelSerializer):

    role_name = SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Получаем список исключаемых полей из context, если он указан
        exclude_fields = self.context.get('exclude_fields', [])
        # Удаляем поля, указанные в exclude_fields, из сериализатора
        for field_name in exclude_fields:
            if field_name in self.fields:
                self.fields.pop(field_name)

    class Meta:
        model = CustomUser
        fields = ("first_name", "second_name", "last_name", "avatar",
                  "role_id", "role_name", "email")

    def get_role_name(self, model_obj):
        return model_obj.role_name


class LoginUserSerializer(Serializer):

    email = EmailField()
    password = CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not (email and password):
            raise ValidationError(
                "Must include 'email' and 'password'"
            )

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )

        if not user or not user.is_active:
            raise ValidationError(
                "Such user does not exists or was delete"
            )
        attrs['user'] = user
        return attrs