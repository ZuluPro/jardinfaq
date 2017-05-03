from favicon.templatetags.favicon import get_favicons as _get_favicons
from coffin import template as coffin_template

register = coffin_template.Library()


@register.tag
def get_favicons(prefix=''):
    return _get_favicons(prefix)
