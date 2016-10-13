from datetime import datetime

import facebook

from django.utils import timezone
from django.contrib.auth import get_user_model

from askbot.conf import settings as askbot_settings
from askbot.models import Tag
from askbot.deps.django_authopenid.models import UserAssociation


FEEDS_URL = '%s/feed?fields=full_picture,link,message,from,likes,reactions,type,created_time,updated_time,message_tags'
POST_URL = '%s?fields=type,message,from,likes,created_time,attachments,comments{message,from,like_count,created_time,comment_count}'
COMMENT_URL = '%s?fields=message,from,likes,created_time,comments{message,from,like_count,created_time,comment_count}'


def get_facebook_api(token=None):
    token = token or askbot_settings.FACEBOOK_TOKEN
    return facebook.GraphAPI(token)


def get_feeds_url(page_name=None):
    page_name = askbot_settings.FACEBOOK_PAGE
    return FEEDS_URL % page_name


def get_facebook_user():
    User = get_user_model()
    return User.objects.get(username='facebook')


def guess_user(fb_obj):
    fb_user = UserAssociation.objects\
        .filter(provider_name='facebook', openid_url=fb_obj['from']['id'])
    if fb_user.exists():
        user = fb_user.first().user
    else:
        User = get_user_model()
        user = User.objects.get(username='Facebook')
    return user


def guess_title(fb_obj):
    return fb_obj['message'].splitlines()[0]


def guess_tags(fb_obj):
    tags = []
    existing_tags = Tag.objects.filter(deleted=False).order_by('-used_count')
    for tag in existing_tags:
        if tag.name in fb_obj['message'].lower():
            tags.append(tag.name)
        if len(tags) == 5:
            break
    return ' '.join(tags)


def guess_text(fb_obj):
    text = fb_obj['message'].replace('\n', '\n\n')
    if fb_obj.get('type') == 'photo' and 'attachments' in fb_obj:
        for fb_image in fb_obj['attachments']['data']:
            if 'subattachments' in fb_image:
                for fb_image_ in fb_image['subattachments']['data']:
                    image_url = fb_image_['media']['image']['src']
                    text += "\n![](%s)" % image_url
            else:
                image_url = fb_image['media']['image']['src']
                text += "\n![](%s)" % image_url
    return text


def guess_timestamp(fb_obj):
    current_tz = timezone.get_current_timezone()
    timestamp = datetime.strptime(fb_obj['created_time'],
                                  "%Y-%m-%dT%H:%M:%S+0000")
    timestamp = current_tz.localize(timestamp)
    return timestamp

