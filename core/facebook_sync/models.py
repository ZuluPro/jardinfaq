from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from askbot.models.post import Post, PostManager
from askbot import signals
from core.facebook_sync import conf
from askbot.conf import settings as askbot_settings

from core.facebook_sync import utils

LANGUAGE = 'fr'


class FacebookPostManager(PostManager):
    def create_question(self, fb_obj):
        user = utils.guess_user(fb_obj)
        timestamp = utils.guess_timestamp(fb_obj)
        question = user.post_question(
            title=utils.guess_title(fb_obj),
            body_text=utils.guess_text(fb_obj),
            tags=utils.guess_tags(fb_obj),
            timestamp=timestamp,
            wiki=False,
            is_anonymous=False,
            is_private=False,
            group_id=None,
            language=LANGUAGE,
            ip_addr="0.0.0.0"
        )
        fb_question_data = dict([(f.attname, getattr(question, f.attname))
                                 for f in question._meta.fields])
        fb_question_data.update({
            'facebook_id': fb_obj['id'],
            'picture_url': fb_obj.get('full_picture', 'https://foo'),
            'facebook_url': fb_obj.get('link', 'https://foo'),
            'facebook_author_id': fb_obj['from']['id'],
            'likes': len(fb_obj.get('likes', {'data': []})),
        })
        fb_question = self.create(**fb_question_data)
        signals.new_question_posted.send(None,
                                         question=fb_question,
                                         user=user)
        return fb_question

    def create_answer(self, question_id, fb_obj):
        user = utils.guess_user(fb_obj)
        question = self.get(facebook_id=question_id)
        answer = user.post_answer(
            question=question,
            body_text=utils.guess_text(fb_obj),
            follow=False,
            wiki=False,
            is_private=False,
            timestamp=utils.guess_timestamp(fb_obj),
            by_email=False,
            ip_addr='0.0.0.0',
        )
        fb_answer_data = dict([(f.attname, getattr(answer, f.attname))
                               for f in answer._meta.fields])
        fb_answer_data.update({
            'facebook_id': fb_obj['id'],
            'picture_url': fb_obj.get('full_picture', 'https://foo'),
            'facebook_url': fb_obj.get('link', 'https://foo'),
            'facebook_author_id': fb_obj['from']['id'],
            'likes': len(fb_obj.get('likes', {'data': []})),
        })
        fb_answer = self.create(**fb_answer_data)
        signals.new_answer_posted.send(None,
                                       answer=fb_answer,
                                       user=user)
        return fb_answer

    def create_comment(self, parent_id, fb_obj):
        user = utils.guess_user(fb_obj)
        parent_post = self.get(facebook_id=parent_id)
        comment = user.post_comment(
            parent_post=parent_post,
            body_text=fb_obj['message'],
            timestamp=utils.guess_timestamp(fb_obj),
            by_email=False,
            ip_addr='0.0.0.0',
        )
        fb_comment_data = dict([(f.attname, getattr(comment, f.attname))
                                for f in comment._meta.fields])
        fb_comment_data.update({
            'facebook_id': fb_obj['id'],
            'picture_url': fb_obj.get('full_picture', 'https://foo'),
            'facebook_url': fb_obj.get('link', 'https://foo'),
            'facebook_author_id': fb_obj['from']['id'],
            'likes': len(fb_obj.get('likes', {'data': []})),
        })
        fb_comment = self.create(**fb_comment_data)
        signals.new_comment_posted.send(None,
                                        comment=fb_comment,
                                        user=user)
        return fb_comment

    def sync(self):
        fb_api = utils.get_facebook_api()
        facebook_posts = fb_api.get_object(utils.get_feeds_url())
        fb_questions = facebook_posts['data']
        for fb_question in fb_questions:
            if self.filter(facebook_id=fb_question['id']).exists():
                question = self.get(facebook_id=fb_question['id'])
            else:
                if fb_question['type'] in ('status', 'photo') and 'message' in fb_question:
                    question = self.create_question(fb_question)
                else:
                    continue
            question.sync()

    def import_question(self, post_id):
        fb_api = utils.get_facebook_api()
        fb_question = fb_api.get_object(utils.POST_URL % post_id)
        if self.filter(facebook_id=fb_question['id']).exists():
            question = self.get(facebook_id=fb_question['id'])
        else:
            if not(fb_question['type'] in ('status', 'photo') and
                   'message' in fb_question):
                return
            question = self.create_question(fb_question)
        question.sync()


class FacebookPost(Post):
    facebook_id = models.CharField(max_length=64)
    picture_url = models.URLField()
    facebook_url = models.URLField()
    facebook_author_id = models.PositiveIntegerField()
    likes = models.PositiveIntegerField()

    objects = FacebookPostManager()

    class Meta:
        app_label = 'facebook_sync'
        verbose_name = _("Facebook post")
        verbose_name_plural = _("Facebook posts")

    def sync(self):
        if self.post_type != 'question':
            return False
        fb_api = utils.get_facebook_api()
        fb_obj = fb_api.get_object(utils.POST_URL % self.facebook_id)
        # Create answers
        for fb_answer in fb_obj.get('comments', {'data': []})['data']:
            if FacebookPost.objects.filter(facebook_id=fb_answer['id']).exists():
                answer = FacebookPost.objects.get(facebook_id=fb_answer['id'])
            else:
                answer = FacebookPost.objects.create_answer(self.facebook_id, fb_answer)
            # Create comments
            fb_comments = fb_answer.get('comments', {'data': []})['data']
            fb_comments = fb_answer['comments']['data']\
                if fb_answer.get('comments', {'data': []})['data']\
                else fb_api.get_object(utils.COMMENT_URL % fb_answer['id']).get('comments', {'data': []})['data']
            for fb_comment in fb_comments:
                if FacebookPost.objects.filter(facebook_id=fb_comment['id']).exists():
                    comment = FacebookPost.objects.get(facebook_id=fb_comment['id'])
                else:
                    comment = FacebookPost.objects.create_comment(answer.facebook_id,
                                                                  fb_comment)
