from django.utils.translation import ugettext_lazy as _
from askbot.models.badges import Badge as BaseBadge
from askbot import const
from bio.contribute import models as bio_models


class Badge(BaseBadge):
    def __init__(self):
        super(Badge, self).__init__(
            name=self.name, description=self._description,
            level=self.level, multiple=self.multiple)

    def is_enabled(self):
        return True


class Sorter(Badge):
    key = 'sorter'
    name = _('Sorter')
    level = const.BRONZE_BADGE
    multiple = False
    count = 1

    def consider_award(self, actor=None, context_object=None, timestamp=None):
        count = bio_models.NewPlant.objects.filter(user=actor, validated=True).count()
        if count >= self.count:
            return self.award(actor, context_object, timestamp)

    @property
    def _description(self):
        return _("Added %(count)s plant(s)") % {'count': self.count}


class Classificator(Sorter):
    key = 'classificator'
    name = _('Classificator')
    level = const.SILVER_BADGE
    count = 5


class Systematician(Sorter):
    key = 'systematician'
    name = _('Systematician')
    level = const.GOLD_BADGE
    count = 10


class Witness(Badge):
    key = 'witness'
    name = _('Witness')
    level = const.BRONZE_BADGE
    multiple = False
    count = 3

    def consider_award(self, actor=None, context_object=None, timestamp=None):
        count = bio_models.PlantQuestion.objects.filter(user=actor, validated=True).count()
        if count >= self.count:
            return self.award(actor, context_object, timestamp)

    @property
    def _description(self):
        return _("Added %(count)s plant's attibute(s)") % {'count': self.count}


class Observer(Witness):
    key = 'observer'
    name = _('Observer')
    level = const.SILVER_BADGE
    count = 10


class Reporter(Witness):
    key = 'reporter'
    name = _('Reporter')
    level = const.GOLD_BADGE
    count = 25


class Illustrator(Badge):
    key = 'illustrator'
    name = _('Illustrator')
    level = const.BRONZE_BADGE
    multiple = False
    count = 1

    def consider_award(self, actor=None, context_object=None, timestamp=None):
        count = bio_models.PlantImage.objects.filter(user=actor, validated=True).count()
        if count >= self.count:
            return self.award(actor, context_object, timestamp)

    @property
    def _description(self):
        return _("Added %(count)s plant's image") % {'count': self.count}


class Displayer(Illustrator):
    key = 'displayer'
    name = _('Displayer')
    level = const.SILVER_BADGE
    count = 5


class Physionomist(Illustrator):
    key = 'physionomist'
    name = _('Physionomist')
    level = const.GOLD_BADGE
    count = 10


BADGES = {
    'accepted_new_plant': (Sorter, Classificator, Systematician),
    'accepted_plant_attribute': (Witness, Observer, Reporter),
    'accepted_plant_image': (Illustrator, Displayer, Physionomist),
}
