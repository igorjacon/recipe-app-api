from django.contrib.auth import get_user_model, authenticate

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
import re


class UserSerializer(serializers.ModelSerializer):
    """serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
            }
        }

    def create(self, validated_data):
        """Create new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update user and set password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def validate(self, data):
        """Check that password contains at least 1 uppercase and 1 digit"""
        if 'password' in data and not re.findall('[A-Z]', data['password']):
            raise serializers.ValidationError('Password must containt at '
                                              'least 1 uppercase')

        if 'password' in data and not re.findall('[0-9]', data['password']):
            raise serializers.ValidationError('Password must contain at least '
                                              '1 digit')

        return data


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, data):
        """Validate and authenticate user"""
        user = authenticate(
            request=self.context.get('request'),
            username=data['email'],
            password=data['password']
        )

        if not user:
            msg = _('Unable to authenticate the credentials provided.')
            raise serializers.ValidationError(msg, code='authentication')

        data['user'] = user
        return data
