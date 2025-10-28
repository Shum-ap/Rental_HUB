from django.apps import AppConfig

class FeedbacksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.feedbacks'

    def ready(self):
        import apps.feedbacks.signals

