from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_number", "password", "confirm_password", "first_name", "last_name"]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        # Check if email already exists
        if User.objects.filter(email=attrs.get("email")).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        # Generate username from email (before @)
        email = validated_data.get("email")
        username = email.split("@")[0]
        
        # Make username unique
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        validated_data["username"] = username
        
        user = User.objects.create_user(
            username=username,
            email=validated_data["email"],
            phone_number=validated_data.get("phone_number"),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            password=validated_data["password"],
            role="citizen",
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_number", "role", "first_name", "last_name", "full_name", "created_at", "badge_number"]
        read_only_fields = ["role"]

    def get_full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username

class EmailOrPhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer that allows login with email OR phone_number.
    The frontend sends 'username' field which can be either email or phone.
    """
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["role"] = user.role
        token["username"] = user.username
        token["email"] = user.email
        token["full_name"] = f"{user.first_name} {user.last_name}".strip()
        return token

    def validate(self, attrs):
        # Get the login value (email or phone)
        login_value = attrs.get(self.username_field)
        
        # Try to find user by email first, then by phone
        user_obj = None
        try:
            user_obj = User.objects.get(email=login_value)
        except User.DoesNotExist:
            try:
                user_obj = User.objects.get(phone_number=login_value)
            except User.DoesNotExist:
                pass
        
        # If user found, set the username for validation
        if user_obj is not None:
            attrs[self.username_field] = user_obj.username
        
        # Call parent validation
        data = super().validate(attrs)
        
        # Add additional user info to response
        user = self.user
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "role": user.role,
            "phone_number": user.phone_number,
        }
        
        return data