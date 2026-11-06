from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=User)
def synchronize_user_groups(sender, instance, **kwargs):
    if instance.is_superuser:
        instance.groups.remove(
            *Group.objects.filter(name__in=['LPK Staff', 'LPK Managers'])
        )
        return

    if instance.role == User.Role.MANAGER:
        staff_group, _ = Group.objects.get_or_create(name='LPK Staff')
        manager_group, _ = Group.objects.get_or_create(name='LPK Managers')

        instance.groups.remove(staff_group)
        instance.groups.add(manager_group)

    elif instance.role == User.Role.STAFF:
        staff_group, _ = Group.objects.get_or_create(name='LPK Staff')
        manager_group = Group.objects.filter(name='LPK Managers').first()

        if manager_group:
            instance.groups.remove(manager_group)

        instance.groups.add(staff_group)

    else:
        instance.groups.remove(
            *Group.objects.filter(name__in=['LPK Staff', 'LPK Managers'])
        )