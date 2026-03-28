from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Applicant, OTPVerification
from .serializers import ApplicantSerializer, RegisterSerializer


class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = Applicant.objects.all().order_by('-id')
    serializer_class = ApplicantSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():

            user = serializer.save()
            
            # Generate JWT tokens so user is logged in immediately
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Account created successfully!',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response(
                {'error': 'Email and code are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            otp = OTPVerification.objects.get(user=user)
        except OTPVerification.DoesNotExist:
            return Response(
                {'error': 'No OTP found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if expired
        if otp.is_expired:
            otp.delete()
            return Response(
                {'error': 'OTP has expired. Please register again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if code matches
        if otp.code != str(code):
            return Response(
                {'error': 'Invalid OTP code'},
                status=status.HTTP_400_BAD_REQUEST
            )


        # Activate user
        user.is_active = True
        user.save()

        # Delete OTP
        otp.delete()

        # Generate JWT tokens so user is logged in immediately
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Email verified successfully!',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)



class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found or already verified'},
                status=status.HTTP_404_NOT_FOUND
            )


         # Generate new OTP
        code = OTPVerification.generate_otp()
        expires_at = timezone.now() + timedelta(minutes=10)

        OTPVerification.objects.filter(user=user).delete()
        OTPVerification.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )

        try:
            send_mail(
                subject='Your new verification code - Smart Budget',
                message=f'''
Hi {user.username}!

Your new verification code is: {code}

This code expires in 10 minutes.
                ''',
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )

        except Exception as e:
            return Response(
                {'error': 'Failed to send email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {'message': 'New OTP sent to your email!'},
            status=status.HTTP_200_OK
        )

    

class LogoutView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self, request):
        try:
            refresh_token= request.data.get("refresh")
            if refresh_token is None:
                return Response({"error": "Refresh Toke Required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist() 
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
