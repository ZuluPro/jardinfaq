from coffin import template as coffin_template
from django.db import models
from django import template
from askbot import models

register = template.Library()
coffin_register = coffin_template.Library()


@register.filter
@coffin_register.filter
def get_facebook_post(post):
    try:
        if isinstance(post, models.Thread):
            return post.question.facebookpost
        return post.facebookpost
    except models.fields.related.ReverseSingleRelatedObjectDescriptor.RelatedObjectDoesNotExist:
        return
