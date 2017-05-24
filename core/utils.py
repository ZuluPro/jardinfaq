from django.db.models import Q
from askbot.models import Thread


def get_plant_related_threads(plant):
    threads = Thread.objects\
        .exclude(Q(closed=True) | Q(deleted=True))\
        .filter(tags__icontains=plant.get_slug())
    return threads
