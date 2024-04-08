from django.urls import path
from accounts.views import (
    ListFriendsView,
    ListPendingFriendRequestsView,
    SendFriendRequestView,
    UpdateFriendRequestView,
    UserLoginView,
    UserSearchView,
    UserSignupView,
)

urlpatterns = [
    path("signup", UserSignupView.as_view()),
    path("login", UserLoginView.as_view()),
    path("search-users/", UserSearchView.as_view(), name="search_users"),
    path("send-friend-request/<int:receiver_id>/", SendFriendRequestView.as_view()),
    path(
        "update-friend-request/<int:request_id>/<str:action>/",
        UpdateFriendRequestView.as_view(),
    ),
    path("list-friends/", ListFriendsView.as_view()),
    path("list-pending-requests/", ListPendingFriendRequestsView.as_view()),
]
