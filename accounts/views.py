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
        """
        Handle POST request for user signup.

        Validates the incoming data with the UserSerializer. If the data is valid, saves the new user
        and returns a 200 OK response with a success message and the serialized user data. If the data
        is invalid, returns a 400 Bad Request response with the validation errors.

        Parameters:
        - request: HttpRequest object containing the request data.

        Returns:
        - Response object with status code 200 OK and user data if data is valid.
        - Response object with status code 400 Bad Request and error details if data is invalid.
        """
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
        """
        Handle POST request for user login.

        Extracts email and password from the request data, authenticates the user, and if successful, generates
        and returns a unique login token. If authentication fails, it returns an error indicating that the credentials
        are invalid.

        Parameters:
        - request: HttpRequest object containing the request data, specifically email and password for authentication.

        Returns:
        - Response object with status code 200 OK and the login token if authentication is successful.
        - Response object with status code 401 Unauthorized and error message if authentication fails.
        """
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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    page_size = 10
    max_page_size = 10

    def get(self, request):
        """
        Handle GET request for user search.

        Searches for users based on a keyword provided via query parameters. The search considers the keyword as
        an exact match for email addresses or a partial match for usernames. Returns paginated search results.

        Parameters:
        - request: HttpRequest object containing the search keyword as a query parameter.

        Returns:
        - Paginated response object with a list of users matching the search criteria if the keyword is provided.
        - Response object with status code 400 Bad Request if no keyword is provided or if it's an empty string.
        """
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
        """
        View for sending friend requests.

        Allows authenticated users to send friend requests to other users. Implements rate limiting to prevent abuse,
        allowing a maximum of 3 friend request attempts per minute per user. It also checks for duplicate friend requests
        to ensure that a user cannot send more than one friend request to the same user.

        Authentication Classes:
        - TokenAuthentication: Requires users to be authenticated via token authentication.

        Permission Classes:
        - IsAuthenticated: Ensures only authenticated users can access this view.
        """
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
        """
        Handle POST request to update the status of a friend request.

        Based on the provided action, this method updates a friend request's status to either 'ACCEPTED'
        or 'REJECTED'. It validates the existence of the friend request and that the authenticated user
        is the intended receiver of the request.

        Parameters:
        - request: HttpRequest object containing the authenticated user's data.
        - request_id: The ID of the friend request to be updated.
        - action: The action to be performed on the friend request ('accept' or 'reject').

        Returns:
        - Response object with status code 200 OK and a success message if the action is successfully performed.
        - Response object with status code 400 Bad Request if an invalid action is provided.
        - Response object with status code 404 Not Found if the friend request is not found.
        """
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
        """
        View for listing the friends of the authenticated user.

        Retrieves a list of users who have mutually accepted friend requests with the authenticated user.
        This list includes users who have either sent a friend request to the authenticated user and had it accepted,
        or users to whom the authenticated user has sent a friend request that was accepted.

        Authentication Classes:
        - TokenAuthentication: Ensures users are authenticated via token authentication to access their list of friends.

        Permission Classes:
        - IsAuthenticated: Restricts access to authenticated users, ensuring privacy and security of user data.
        """
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
        """
        Handle GET request to list all pending friend requests directed to the authenticated user.

        Queries the FriendRequest model for all instances where the authenticated user is the receiver and the
        status is "PENDING". Serializes the query results to provide a clear representation of each pending friend request.

        Parameters:
        - request: HttpRequest object containing the authenticated user's data.

        Returns:
        - Response object with a serialized list of pending friend requests directed to the authenticated user.
        """
        pending_requests = FriendRequest.objects.filter(
            receiver=request.user, status="PENDING"
        )
        serializer = FriendRequestSerializer(pending_requests, many=True)
        return Response(serializer.data)
