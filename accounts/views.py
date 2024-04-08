from accounts.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from accounts.serializer import UserSearchSerializer, UserSerializer


# Create your views here.
class UserSignupView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Congratulations! User creation successful!",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": True, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)
        print("user", user)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {"message": "Login successful.", "token": token.key},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
            )


class UserSearchView(APIView, PageNumberPagination):
    page_size = 10
    max_page_size = 10

    def get(self, request):
        keyword = request.query_params.get("search", "").strip()
        if not keyword:
            return Response(
                {"error": "A search keyword is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "@" in keyword:
            users = User.objects.filter(email__iexact=keyword)
        else:
            users = User.objects.filter(user_name__icontains=keyword)

        results = self.paginate_queryset(users, request, view=self)
        serializer = UserSearchSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)
