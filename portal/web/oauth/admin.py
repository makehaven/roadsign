from django.contrib import admin

from . import models

@admin.register(models.OAuthUser)
class OAuthUserAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'provider', 'uid', 'email', 'user']
