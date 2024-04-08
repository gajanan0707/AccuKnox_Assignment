from django.urls import path

from accounts.views import UserLoginView, UserSearchView, UserSignupView

urlpatterns = [
    path("signup", UserSignupView.as_view()),
    path("login", UserLoginView.as_view()),
    path("search-users/", UserSearchView.as_view(), name="search_users"),
]
