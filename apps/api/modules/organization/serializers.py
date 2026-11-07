from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from .models import Membership, Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ("id", "name", "is_active")
        read_only_fields = ("id",)

    def validate_name(self, value):
        organization = self.context["organization"]
        existing = Store.objects.filter(organization=organization, name=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError("Ya existe una sucursal con ese nombre.")
        return value


class EmployeeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", read_only=True)

    class Meta:
        model = Membership
        fields = ("id", "username", "role", "is_active")
        read_only_fields = ("id", "username", "is_active")


class EmployeeCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, trim_whitespace=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False, style={"input_type": "password"})
    role = serializers.ChoiceField(choices=[Membership.Role.MANAGER, Membership.Role.CASHIER])

    def validate_username(self, value):
        User = get_user_model()
        field = User._meta.get_field(User.USERNAME_FIELD)
        for validator in field.validators:
            try:
                validator(value)
            except Exception as exc:
                raise serializers.ValidationError(str(exc)) from exc
        if User.objects.filter(**{User.USERNAME_FIELD: value}).exists():
            raise serializers.ValidationError("El usuario ya existe.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.create_user(
            username=validated_data["username"], password=validated_data["password"]
        )
        return Membership.objects.create(
            user=user, organization=self.context["organization"], role=validated_data["role"]
        )
