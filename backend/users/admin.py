from django.contrib import admin

from users.models import User


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
