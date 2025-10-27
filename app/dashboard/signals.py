#type: ignore
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def post_migration_handler(sender, **kwargs):
    """Handle post-migration tasks"""
    if sender.name == 'dashboard':
        logger.info("Dashboard app migration completed")
        # Add any other post-migration tasks here if needed 