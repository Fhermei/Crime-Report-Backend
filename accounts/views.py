from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .serializers import RegisterSerializer, UserSerializer, EmailOrPhoneTokenObtainPairSerializer
from .permissions import IsAdmin

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "message": "Registration successful! Please login."
        }, status=status.HTTP_201_CREATED)

class RegisterPoliceView(APIView):
    """Admin-only endpoint to register police officers"""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        # Get data from request
        data = request.data
        
        # Check if user already exists
        if User.objects.filter(email=data.get('email')).exists():
            return Response({"email": "A user with this email already exists."}, status=400)
        
        if User.objects.filter(username=data.get('username')).exists():
            return Response({"username": "A user with this username already exists."}, status=400)
        
        # Create police user
        try:
            user = User.objects.create_user(
                username=data.get('username'),
                email=data.get('email'),
                password=data.get('password'),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone_number=data.get('phone_number', ''),
                role='police',
                badge_number=data.get('badge_number', ''),
                is_staff=True,
            )
            
            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "badge_number": user.badge_number,
                "message": "Police officer registered successfully!"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

class LoginView(TokenObtainPairView):
    serializer_class = EmailOrPhoneTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user