from django.apps import AppConfig
import logging

# Set up logger for the app
logger = logging.getLogger(__name__)

class SettlementsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settlements_app'

    # Optionally log when the app is ready
    def ready(self):
        logger.info(f"Settlements App ({self.name}) is ready!")

        # Import signals to ensure the signals are registered
        import settlements_app.signals

