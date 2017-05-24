from django.dispatch import receiver
from django.utils.timezone import now
from bio.contribute import signals


@receiver([signals.vote_plus_answer, signals.unvote_minus_answer])
def voted_plus_answer(instance, user, **kwargs):
    user.receive_reputation(10)


@receiver([signals.vote_minus_answer, signals.unvote_plus_answer])
def voted_minus_answer(instance, user, **kwargs):
    user.receive_reputation(-10)


@receiver(signals.accepted_answer)
def accepted_answer(instance, user, **kwargs):
    from askbot.models.badges import award_badges_signal
    from bio.contribute import models as bio_models
    user.receive_reputation(25)
    if isinstance(instance, bio_models.NewPlant):
        award_badges_signal.send(None,
                                 event='accepted_new_plant',
                                 actor=user,
                                 context_object=instance,
                                 timestamp=now())
    elif isinstance(instance, bio_models.PlantQuestion):
        award_badges_signal.send(None,
                                 event='accepted_plant_attribute',
                                 actor=user,
                                 context_object=instance,
                                 timestamp=now())
    elif isinstance(instance, bio_models.PlantImage):
        award_badges_signal.send(None,
                                 event='accepted_plant_image',
                                 actor=user,
                                 context_object=instance,
                                 timestamp=now())


@receiver(signals.unaccepted_answer)
def unaccepted_answer(instance, user, **kwargs):
    user.receive_reputation(-25)
