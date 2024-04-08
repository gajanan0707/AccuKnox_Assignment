from rest_framework import serializers
from accounts.models import FriendRequest, User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


# The `UserSerializer` class defines serialization for user data including email and password fields
# with validation and creation logic.
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="User Email already exist!"
            )
        ],
    )

    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data.get("email", ""),
            user_name=validated_data.get("email"),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


# The `UserSearchSerializer` class is a Django REST framework serializer for the User model with
# fields for id, user_name, and email.
class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "user_name", "email"]


# The `FriendRequestSerializer` class defines a serializer for the `FriendRequest` model with
# specified fields and read-only fields.
class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ["id", "sender", "receiver", "status", "created_at"]
        read_only_fields = ["sender", "status", "created_at"]
