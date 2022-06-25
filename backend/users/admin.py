from django.contrib import admin
from django.contrib.auth.admin import Group, UserAdmin

from users.models import Subscriptions, User


class MyUserAdmin(UserAdmin):
    '''Класс для вывода на странице админа
    информации о пользователе.'''

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff'
    )
    list_filter = ('username', 'email')


class SubscriptionsAdmin(admin.ModelAdmin):
    '''Класс для вывода на странице админа
    информации о подписчиках на автора.'''

    list_display = ('id', 'user', 'author')
    list_filter = ('user', 'author')


admin.site.register(User, MyUserAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
admin.site.unregister(Group)
