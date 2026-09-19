from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from .models import User
from django.contrib.auth.admin import UserAdmin
# Register custom User first
admin.site.register(User, UserAdmin)
# admin.site.register(User)

app = apps.get_app_config('application1')

for model in app.get_models():
    if model is User:
        continue  # already registered
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass