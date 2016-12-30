import os
import celery
from django.conf import settings
from newsboard.periodic_tasks import UPDATE_STREAMS

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
app = celery.Celery('jardinfaq')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


if celery.VERSION >= (4, 0, 0):
    @app.on_after_configure.connect
    def setup_periodic_tasks(sender, **kwargs):
        sender.add_periodic_task(name='auto-update-streams' **UPDATE_STREAMS)
