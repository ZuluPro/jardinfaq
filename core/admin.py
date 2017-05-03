from django.contrib import admin
from askbot.admin import PostAdmin as BasePostAdmin
from askbot import models


class PostAdmin(BasePostAdmin):
    fieldsets = (
        (None, {
            'fields': (
                ('author', 'post_type', 'added_at'),
                ('old_question_id', 'old_answer_id', 'old_comment_id'),
                ('thread', 'current_revision'),
                ('endorsed', 'endorsed_by', 'endorsed_at'),
                'approved',
                ('deleted', 'deleted_at', 'deleted_by'),
                ('wiki', 'wikified_at'),
                ('locked', 'locked_by', 'locked_at'),
                ('points', 'vote_up_count', 'vote_down_count'),
                'comment_count',
                'offensive_flag_count',
                ('last_edited_at', 'last_edited_by'),
                'language_code',
                ('html', 'text'),
                'summary',
                'is_anonymous',
            )
        }),
    )
admin.site.unregister(models.Post)
admin.site.register(models.Post, PostAdmin)
