from django.utils.translation import ugettext_lazy as _
from askbot.conf.super_groups import EXTERNAL_SERVICES
from askbot.conf import settings as askbot_settings
from askbot.deps import livesettings


FACEBOOK_SETTINGS = livesettings.ConfigurationGroup(
    'FACEBOOK',
    _("Facebook integration"),
    super_group=EXTERNAL_SERVICES
)

askbot_settings.register(
    livesettings.StringValue(
        FACEBOOK_SETTINGS,
        'FACEBOOK_TOKEN',
        default='',
        description=_("Facebook token to access to API.")
    )
)

askbot_settings.register(
    livesettings.StringValue(
        FACEBOOK_SETTINGS,
        'FACEBOOK_PAGE',
        default='',
        description=_("Facebook page synchronized.")
    )
)
