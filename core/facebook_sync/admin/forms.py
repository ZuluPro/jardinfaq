from django import forms
from core.facebook_sync import models


class FacebookPostForm(forms.ModelForm):
    class Meta:
        model = models.FacebookPost
        exclude = ()


class FacebookThreadSynchronize(forms.ModelForm):
    class Meta:
        model = models.FacebookPost
        fields = ('facebook_id',)
