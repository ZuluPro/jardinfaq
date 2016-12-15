from __future__ import unicode_literals

from django.contrib import admin
from django.shortcuts import redirect, render
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
            question = models.FacebookPost.objects.import_question(request.POST['facebook_id'])
            return redirect("/admin/facebook_sync/facebookpost/")
            return render(request, '/admin/facebook_post_review.html', {
                'question': question,
                'answers': question.answers.all(),
            })
        except IOError as err:
            msg = 'Error: %s' % (err.message or str(err.args))
            self.message_user(request, msg, messages.ERROR)
            return redirect("/admin/facebook_sync/facebookpost/add/")
