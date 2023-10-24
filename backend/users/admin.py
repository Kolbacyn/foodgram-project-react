from django.contrib import admin

from users.models import User, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'username',
        'email',
    )
    search_fields = ('email', 'username',)
    list_filter = ('email', 'username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'author',)
    search_fields = ('subscriber__username',
                     'subscriber__email',
                     'author__username',
                     'author__email')
