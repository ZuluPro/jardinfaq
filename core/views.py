from django.shortcuts import render
from askbot.models import Thread


def home(request):
    most_viewed_thread = Thread.objects.order_by('-view_count').first()
    most_answered_thread = Thread.objects.order_by('-answer_count')\
        .exclude(id=most_viewed_thread.id)\
        .first()
    most_favourited_thread = Thread.objects.order_by('-favourite_count')\
        .exclude(id__in=[most_viewed_thread.id, most_answered_thread.id])\
        .first()
    most_scored_thread = Thread.objects.order_by('-points')\
        .exclude(id__in=[most_viewed_thread.id, most_answered_thread.id,
                         most_favourited_thread.id])\
        .first()
    return render(request, 'home.html', {
        'most_viewed_thread': most_viewed_thread,
        'most_answered_thread': most_answered_thread,
        'most_favourited_thread': most_favourited_thread,
        'most_scored_thread': most_scored_thread,
    })
