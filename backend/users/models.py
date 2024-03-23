from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LENGTH_BASE = 150
MAX_LENGTH_EMAIL = 254


class User(AbstractUser):
    email = models.EmailField(max_length=MAX_LENGTH_EMAIL, unique=True,
                              verbose_name='Адрес электронной почты')
    username = models.CharField(max_length=MAX_LENGTH_BASE, unique=True,
                                verbose_name='Ник пользователя')
    first_name = models.CharField(max_length=MAX_LENGTH_BASE,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=MAX_LENGTH_BASE,
                                 verbose_name='Фамилия')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='Проверка на уникальность подписки'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='Проверка на подписку на самого себя'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
