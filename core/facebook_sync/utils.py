from datetime import datetime
try:
    from urllib.urlparse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs

import facebook
from faker import Factory

from django.utils import timezone
from django.contrib.auth import get_user_model

from askbot.conf import settings as askbot_settings
from askbot.models import Tag
from askbot.deps.django_authopenid.models import UserAssociation


FEEDS_URL = '%s/feed?fields=full_picture,link,message,from,likes,reactions,type,created_time,updated_time,message_tags,permalink_url'
POST_URL = '%s?fields=type,message,from,likes,created_time,attachments,link,permalink_url,comments{message,from,like_count,created_time,comment_count,link,attachment}'
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
    User = get_user_model()

    fb_asso = UserAssociation.objects\
        .filter(provider_name='facebook', openid_url=fb_obj['from']['id'])

    # Create fake name to preserve anonymous
    fake = Factory.create('fr')
    fake.seed(fb_obj['from']['id'])
    fake_username = fake.user_name()

    if fb_asso.exists():
        user = fb_asso.first().user
    elif User.objects.filter(username=fake_username).exists():
        user = User.objects.filter(username=fake_username).first()
    else:
        user = User.objects.create(username=fake_username)
    return user


def guess_title(fb_obj):
    text = fb_obj['message']
    text = text.splitlines()[0][:300]
    return text.capitalize()


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
    def _guess_atta(fb_atta, base_text):
        text = ''
        if 'type' in fb_atta and fb_atta['type'].startswith('video'):
            parsed_url = urlparse(fb_atta['url'])
            parsed_qs = parse_qs(parsed_url.query)
            if not parsed_qs['u'][0] in base_text:
                text += '\n\n' + parsed_qs['u'][0]
        elif 'subattachments' in fb_atta:
            for fb_atta_ in fb_atta['subattachments']['data']:
                image_url = fb_atta_['media']['image']['src']
                text += "\n\n![](%s)" % image_url
        elif 'media' in fb_atta:
            if 'image' in fb_atta['media']:
                image_url = fb_atta['media']['image']['src']
                text += "\n![](%s)" % image_url
        return text

    text = fb_obj['message'].replace('\n', '\n\n')
    if 'attachments' in fb_obj:
        for fb_atta in fb_obj['attachments']['data']:
            text += _guess_atta(fb_atta, text)
    elif 'attachment' in fb_obj:
        text += _guess_atta(fb_obj['attachment'], text)
    return text


def guess_timestamp(fb_obj):
    current_tz = timezone.get_current_timezone()
    timestamp = datetime.strptime(fb_obj['created_time'],
                                  "%Y-%m-%dT%H:%M:%S+0000")
    timestamp = current_tz.localize(timestamp)
    return timestamp


def guess_url(fb_obj):
    return fb_obj['permalink_url']
