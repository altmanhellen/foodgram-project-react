from django.contrib import admin

from .models import Follower, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    search_fields = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    ordering = ('username',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('username', 'email', 'first_name', 'last_name')
        }),
        ('Дополнительная информация', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    readonly_fields = ('last_login', 'date_joined')


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('id', 'user', 'author')
    ordering = ('user',)
    fieldsets = (
        ('Подписчик', {
            'fields': ('user',)
        }),
        ('Автор', {
            'fields': ('author',)
        }),
    )
