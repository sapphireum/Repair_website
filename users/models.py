from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password


class TypeProfiles(models.Model):
    name = models.CharField(max_length=60)

    class Meta:
        db_table = "type"
        verbose_name = "Тип профиля"
        verbose_name_plural = "Типы профилей"

    def __str__(self):
        return self.name


class User(AbstractUser):
    profile_img = models.ImageField(
        upload_to="users_images", blank=True, null=True, verbose_name="Аватар"
    )

    profile_type = models.ForeignKey(
        to=TypeProfiles, on_delete=models.PROTECT, verbose_name="Тип профиля", default=2
    )

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
