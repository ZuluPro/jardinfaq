from django.contrib import admin
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.contrib import messages

from core.facebook_sync import models
from core.facebook_sync.admin import forms

PostAdmin = admin.site._registry[models.Post]


class FacebookPostAdmin(PostAdmin.__class__):
    list_display = list(PostAdmin.list_display) + ['get_facebook_link']

    add_form = forms.FacebookThreadSynchronize
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('facebook_id',)
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return self.add_form
        return super(FacebookPostAdmin, self).get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        return super(FacebookPostAdmin, self).get_fieldsets(request, obj)

    def add_view(self, request, form_url='', extra_context=None):
        if request.method == 'GET':
            return super(FacebookPostAdmin, self).add_view(request, form_url, extra_context)
        try:
            models.FacebookPost.objects.import_question(request.POST['facebook_id'])
            return redirect("/admin/facebook_sync/facebookpost/")
        except Exception as err:
            raise
            self.message_user(request, str(err), messages.ERROR)
            return redirect("/admin/facebook_sync/facebookpost/add/")
