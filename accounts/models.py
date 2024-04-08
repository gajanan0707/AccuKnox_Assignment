from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

NULL_AND_BLANK = {"null": True, "blank": True}


# Create your models here.
class UserManager(BaseUserManager):
    """
    BaseUserManager provides:
        * normalize_email()
    Default implementation of UserManager works with username, since we user `email` as username field so we have custom implementation of _create_user() etc.
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("Users must have an email address")
        # normalize_email() does .lower() on domain_part, i.e converts Jane@Moveeasy.com to Jane@moveeasy.com
        email = self.normalize_email(email)
        user = self.model(email=email, is_active=True, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        return self._create_user(email, password, **extra_fields)


# Create your models here.
class User(AbstractBaseUser):
    email = models.EmailField(
        _("email address"), unique=True, db_index=True, null=False, blank=False
    )
    user_name = models.CharField(
        max_length=500,
        help_text=_("Unique to Identify the user in the system"),
        unique=False,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("staff"), default=False)
    is_superuser = models.BooleanField(_("staff"), default=False)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email or self.uid

    def get_short_name(self):
        return self.user_name

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class FriendRequest(models.Model):
    sender = models.ForeignKey(
        User, related_name="sent_requests", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="received_requests", on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=10,
        choices=(
            ("PENDING", "Pending"),
            ("ACCEPTED", "Accepted"),
            ("REJECTED", "Rejected"),
        ),
        default="PENDING",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("sender", "receiver")

    def __str__(self):
        return str(self.sender)
