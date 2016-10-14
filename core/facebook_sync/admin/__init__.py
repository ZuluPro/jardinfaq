from django.contrib import admin
from core.facebook_sync import models
from core.facebook_sync.admin import modeladmins


admin.site.register(models.FacebookPost, modeladmins.FacebookPostAdmin)
