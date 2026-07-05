"""
RENTPLAY Signals v1.0
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Agency, User


@receiver(post_save, sender=Agency)
def create_agency_slug(sender, instance, created, **kwargs):
    if created and not instance.slug:
        base = slugify(instance.name) or 'agency'
        slug, counter = base, 1
        while Agency.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
            slug = f"{base}-{counter}"
            counter += 1
        instance.slug = slug
        instance.save(update_fields=['slug'])


@receiver(post_save, sender=User)
def ensure_agency_link(sender, instance, created, **kwargs):
    if instance.role == User.Role.AGENCY_ADMIN and instance.agency and instance.agency.admin is None:
        instance.agency.admin = instance
        instance.agency.save(update_fields=['admin'])
