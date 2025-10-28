from django.apps import AppConfig

class LogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.log"

    def ready(self):
        import apps.log.signals.view_log_signal
