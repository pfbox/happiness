from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.utils import OperationalError


class Team(models.Model):
    team_name = models.CharField(max_length=50, unique=True, blank=False, null=False)

    def __str__(self):
        return self.team_name


# Need this table to store Team for User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(to=Team, on_delete=models.PROTECT, null=True, blank=True)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    try:
        profile, pr_created = Profile.objects.get_or_create(user=instance)
        instance.profile = profile
        instance.profile.save()
    except OperationalError:
        # No error if table Profile does not exists yet, e.g. if you're trying to create superuser on empty db
        pass


class Happiness(models.Model):
    UNHAPPY = -1
    NEUTRAL = 0
    HAPPY = 1
    ECSTATIC = 2
    HAPPINESS_MAP = {UNHAPPY: 'Unhappy', NEUTRAL: 'Neutral', HAPPY: 'Happy', ECSTATIC: 'Ecstatic'}
    HAPPINESS_LEVELS = [(key, value) for key, value in HAPPINESS_MAP.items()]
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    happiness_level = models.IntegerField(choices=HAPPINESS_LEVELS)
    entry_date = models.DateField(null=False)

    class Meta:
        unique_together = ('user', 'entry_date')
