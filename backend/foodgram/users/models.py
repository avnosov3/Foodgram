from django.contrib.auth.models import AbstractUser
from django.db import models

from .settings import EMAIL_MAX_LENGHT, MAIN_MAX_LENGHT


class CustomUser(AbstractUser):
    username = models.CharField(
        verbose_name='Юзернейм',
        unique=True,
        blank=True,
        max_length=MAIN_MAX_LENGHT
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта',
        max_length=EMAIL_MAX_LENGHT
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAIN_MAX_LENGHT
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAIN_MAX_LENGHT
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name='Проверка повторной подписки',
                fields=['user', 'author'],
            ),
            models.CheckConstraint(
                name='Проверка самоподписки',
                check=~models.Q(user=models.F('author')),
            ),
        ]
