from django.shortcuts import render, redirect
from django.db.models import Q

from askbot.models import Thread, BadgeData
from askbot.models import badges as badge_data
from askbot.context import application_settings


def home(request):
    if request.user.is_authenticated():
        return redirect('questions')

    exclusion = []
    threads = Thread.objects.exclude(Q(closed=True) | Q(deleted=True))

    most_viewed_thread = threads.order_by('-view_count').first()
    if most_viewed_thread:
        exclusion.append(most_viewed_thread.id)

    most_answered_thread = threads.order_by('-answer_count')\
        .exclude(id__in=exclusion)\
        .first()
    if most_answered_thread:
        exclusion.append(most_answered_thread.id)

    most_favourited_thread = threads.order_by('-favourite_count')\
        .exclude(id__in=exclusion)\
        .first()
    if most_favourited_thread:
        exclusion.append(most_favourited_thread.id)

    most_scored_thread = threads.order_by('-points')\
        .exclude(id__in=exclusion)\
        .first()

    known_badges = badge_data.BADGES.keys()
    badges = BadgeData.objects.filter(slug__in=known_badges)\
        .order_by('?')[:5]

    return render(request, 'jardinfaq/home.html', {
        'settings': application_settings,
        'most_viewed_thread': most_viewed_thread,
        'most_answered_thread': most_answered_thread,
        'most_favourited_thread': most_favourited_thread,
        'most_scored_thread': most_scored_thread,
        'badges': badges
    })
