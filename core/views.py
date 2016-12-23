from django.shortcuts import render, redirect
from askbot.models import Thread


def home(request):
    if request.user.is_authenticated():
        return redirect('questions')
    exclusion = []

    most_viewed_thread = Thread.objects.order_by('-view_count').first()
    if most_viewed_thread:
        exclusion.append(most_viewed_thread.id)

    most_answered_thread = Thread.objects.order_by('-answer_count')\
        .exclude(id__in=exclusion)\
        .first()
    if most_answered_thread:
        exclusion.append(most_answered_thread.id)

    most_favourited_thread = Thread.objects.order_by('-favourite_count')\
        .exclude(id__in=exclusion)\
        .first()
    if most_favourited_thread:
        exclusion.append(most_favourited_thread.id)

    most_scored_thread = Thread.objects.order_by('-points')\
        .exclude(id__in=exclusion)\
        .first()

    return render(request, 'home.html', {
        'most_viewed_thread': most_viewed_thread,
        'most_answered_thread': most_answered_thread,
        'most_favourited_thread': most_favourited_thread,
        'most_scored_thread': most_scored_thread,
    })
