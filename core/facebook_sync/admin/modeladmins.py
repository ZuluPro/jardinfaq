from __future__ import unicode_literals

from django.contrib import admin
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from django.contrib import messages

from askbot import signals

from core.facebook_sync import models
from core.facebook_sync import utils
from core.facebook_sync.admin import forms

PostAdmin = admin.site._registry[models.Post]


def create_answer(request, answer_id, question):
    comments = []
    ans_timestamp = utils.guess_timestamp({'created_time': request.POST['answer_%s_timestamp' % answer_id]})
    answer_author = utils.guess_user({'from': {'name': request.POST['answer_%s_author_name' % answer_id], 'id': request.POST['answer_%s_author_id' % answer_id]}})
    if models.FacebookPost.objects.filter(facebook_id=answer_id).exists():
        answer = models.FacebookPost.objects.filter(facebook_id=request.POST['id']).first()
    else:
        answer = answer_author.post_answer(
            question=question,
            body_text=request.POST['answer_%s_text' % answer_id],
            follow=False,
            wiki=False,
            is_private=False,
            timestamp=ans_timestamp,
            by_email=False,
            ip_addr='0.0.0.0',
        )
        fb_answer_data = dict([(f.attname, getattr(answer, f.attname))
                               for f in answer._meta.fields])
        fb_answer = models.FacebookPost.objects.create(
            facebook_id=answer_id,
            picture_url=request.POST.get('full_picture', ''),
            facebook_url=request.POST['answer_%s_url' % answer_id],
            facebook_author_id=request.POST['answer_%s_author_id' % answer_id],
            likes=request.POST['answer_%s_likes' % answer_id],
            **fb_answer_data
        )
        signals.new_answer_posted.send(None, answer=fb_answer, user=answer_author)
    for comment_id in request.POST.getlist('answer_%s_comment_ids' % answer_id):
        if ('comment_%s_import' % comment_id) not in request.POST:
            continue
        if models.FacebookPost.objects.filter(facebook_id=comment_id).exists():
            comment = models.FacebookPost.objects.filter(facebook_id=request.POST['id']).first()
        else:
            com_timestamp = utils.guess_timestamp({'created_time': request.POST['comment_%s_timestamp' % comment_id]})
            comment_author = utils.guess_user({'from': {'name': request.POST['comment_%s_author_name' % comment_id], 'id': request.POST['comment_%s_author_id' % comment_id]}})
            comment = comment_author.post_comment(
                parent_post=answer,
                body_text=request.POST['comment_%s_text' % comment_id],
                timestamp=com_timestamp,
                by_email=False,
                ip_addr='0.0.0.0',
            )
            fb_comment_data = dict([(f.attname, getattr(comment, f.attname))
                                   for f in comment._meta.fields])
            fb_comment = models.FacebookPost.objects.create(
                facebook_id=comment_id,
                picture_url=request.POST.get('full_picture', ''),
                facebook_url=request.POST['comment_%s_url' % comment_id],
                facebook_author_id=request.POST['comment_%s_author_id' % comment_id],
                likes=request.POST['comment_%s_likes' % comment_id],
                **fb_comment_data
            )
            signals.new_comment_posted.send(None, comment=fb_comment, user=comment_author)
        comments.append(comment)
    return answer, comments


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
        if '_import' in request.POST:
            if self.model.objects.filter(facebook_id=request.POST['id']).exists():
                question = self.model.objects.filter(facebook_id=request.POST['id']).first()
            else:
                author = utils.guess_user({'from': {'name': request.POST['author_name'], 'id': request.POST['author_id']}})
                timestamp = utils.guess_timestamp({'created_time': request.POST['timestamp']})
                question = author.post_question(
                    title=request.POST['title'],
                    body_text=request.POST['question_text'],
                    tags=request.POST['tags'],
                    timestamp=timestamp,
                    wiki=False,
                    is_anonymous=False,
                    is_private=False,
                    group_id=None,
                    language='fr',
                    ip_addr="0.0.0.0"
                )
                fb_question_data = dict([(f.attname, getattr(question, f.attname))
                                         for f in question._meta.fields])
                fb_question = models.FacebookPost.objects.create(
                    facebook_id=request.POST['id'],
                    picture_url=request.POST.get('full_picture', ''),
                    facebook_url=request.POST['url'],
                    facebook_author_id=request.POST['author_id'],
                    likes=request.POST['likes'],
                    **fb_question_data
                )
                signals.new_question_posted.send(None, question=fb_question, user=author)
            for answer_id in request.POST.getlist('answer_ids'):
                if ('answer_%s_import' % answer_id) not in request.POST:
                    continue
                answer, comments = create_answer(request, answer_id, question)
            return redirect("/admin/facebook_sync/facebookpost/")
        try:
            post_id = request.POST['facebook_id'] if request.POST['facebook_id'].isdigit() else utils.POST_ID_REG.match(request.POST['facebook_id']).groups()[0]
            fb_api = utils.get_facebook_api()
            fb_question = fb_api.get_object(utils.POST_URL % post_id)
            return render(request, 'admin/facebook_thread_review.html', {
                'question': fb_question,
                'opts': self.model._meta,
                'title': utils.guess_title(fb_question),
                'text': utils.guess_text(fb_question),
                'tags': utils.guess_tags(fb_question),
                'url': utils.guess_url(fb_question),
                'likes': len(fb_question.get('likes', {'data': []})['data']),
            })
            # question = models.FacebookPost.objects.import_question(request.POST['facebook_id'])
            # return redirect("/admin/facebook_sync/facebookpost/")
        except IOError as err:
            msg = 'Error: %s' % (err.message or str(err.args))
            self.message_user(request, msg, messages.ERROR)
            return redirect("/admin/facebook_sync/facebookpost/add/")
