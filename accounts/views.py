from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from accounts.models import FriendRequest, User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from accounts.serializer import (
    FriendRequestSerializer,
    UserSearchSerializer,
    UserSerializer,
)


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


class SendFriendRequestView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, receiver_id):
        if (
            FriendRequest.objects.filter(
                sender=request.user,
                created_at__gte=timezone.now() - timedelta(minutes=1),
            ).count()
            >= 3
        ):
            return Response(
                {"error": "Rate limit exceeded"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        if FriendRequest.objects.filter(
            sender=request.user, receiver_id=receiver_id
        ).exists():
            return Response(
                {"error": "Friend request already sent"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        FriendRequest.objects.create(sender=request.user, receiver_id=receiver_id)
        return Response(
            {"success": "Friend request sent"}, status=status.HTTP_201_CREATED
        )


class UpdateFriendRequestView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, request_id, action):
        try:
            friend_request = FriendRequest.objects.get(
                id=request_id, receiver=request.user
            )
            if action == "accept":
                friend_request.status = "ACCEPTED"
            elif action == "reject":
                friend_request.status = "REJECTED"
            else:
                return Response(
                    {"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST
                )

            friend_request.save()
            return Response(
                {"success": f"Friend request {action}ed."}, status=status.HTTP_200_OK
            )
        except FriendRequest.DoesNotExist:
            return Response(
                {"error": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ListFriendsView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        friends = User.objects.filter(
            Q(
                received_requests__sender=request.user,
                received_requests__status="ACCEPTED",
            )
            | Q(sent_requests__receiver=request.user, sent_requests__status="ACCEPTED")
        ).distinct()
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)


class ListPendingFriendRequestsView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        pending_requests = FriendRequest.objects.filter(
            receiver=request.user, status="PENDING"
        )
        serializer = FriendRequestSerializer(pending_requests, many=True)
        return Response(serializer.data)
