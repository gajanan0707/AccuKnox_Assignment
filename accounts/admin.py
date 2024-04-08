from django.contrib import admin
from accounts.models import FriendRequest, User

# Register your models here.
admin.site.register(User)
admin.site.register(FriendRequest)
