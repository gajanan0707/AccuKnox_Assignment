from django.contrib import admin
from accounts.models import FriendRequest, User


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
    )
    search_fields = ("id", "user_name", "email")
    list_per_page = 10
    exclude = ("password",)


class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "status")
    search_fields = ("id", "sender", "receiver", "status")
    list_per_page = 10


admin.site.register(User, UserAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
