from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Team, Happiness


# Register your models here.
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'
    fk_name = 'user'


class TeamUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_team')
    list_select_related = ('profile', )

    def get_team(self, instance):
        if instance.profile.team:
            return instance.profile.team.team_name
        else:
            return None

    get_team.short_description = 'Team'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(TeamUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, TeamUserAdmin)
admin.site.register(Team)
admin.site.register(Happiness)
