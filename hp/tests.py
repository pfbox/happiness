from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
import pandas as pd

from .models import Team, Profile
from .views import *

from datetime import timedelta
import random
import itertools
from django.contrib.auth.models import User
from rest_framework.test import force_authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token


# Unit tests
class HpAPITest(APITestCase):
    def setUp(self, no_of_users=20, no_of_teams=3, no_of_days=5):
        self.happiness_map = Happiness.HAPPINESS_MAP
        # Create Test DB
        self.users = ['TestUser{}'.format(i) for i in range(1, no_of_users + 1)]
        self.teams = ['TestTeam{}'.format(i) for i in range(1, no_of_teams + 1)]
        self.days = [(datetime.now().date() + timedelta(days=-i)).strftime('%Y-%m-%d') for i in range(0, no_of_days)]
        happiness = list(Happiness.HAPPINESS_MAP.keys())
        data = [(user, day, random.choice(happiness)) for user, day in itertools.product(self.users, self.days)]

        self.testdf = pd.DataFrame(columns=['user', 'entry_date', 'happiness'], data=data)
        self.userteam = {user: random.choice(self.teams) for user in self.users}
        self.testdf['team'] = self.testdf.user.apply(lambda x: self.userteam[x])
        self.testdf['happiness_level'] = self.testdf.happiness.apply(lambda x: self.happiness_map[x])

        self.unauth_res = self.testdf.groupby('entry_date').agg({'happiness': 'mean'})
        self.unauth_res['response'] = self.unauth_res.apply(lambda x: {'report_date': x.name,
                                                                       'request_authenticated': False,
                                                                       'avg_happiness': x.happiness}, axis=1)

        hp_avg = pd.pivot_table(self.testdf, index=['entry_date', 'team'], values='happiness', aggfunc='mean')\
            .rename(columns={'happiness': 'avg_team_happiness'})
        hp_levels = pd.pivot_table(self.testdf, index=['entry_date', 'team'], columns='happiness_level',
                                   values='happiness', aggfunc='count').fillna(0)

        self.auth_res = pd.concat([hp_avg, hp_levels], axis=1)
        self.auth_res['response'] = self.auth_res\
            .apply(lambda x: {'report_date': x.name[0], 'request_authenticated': True, 'team': x.name[1],
                              'avg_team_happiness': x.avg_team_happiness,
                              'people_by_level': {val: x[val] for val in Happiness.HAPPINESS_MAP.values()}
                              }, axis=1)

        # Create Teams
        for team in self.teams:
            Team.objects.get_or_create(team_name=team)

        # Create Users
        for user in self.users:
            urec = User.objects.get_or_create(username=user)
            prec = Profile.objects.get(user=urec[0])
            prec.team = Team.objects.get(team_name=self.userteam[user])
            prec.save()
            Token.objects.get_or_create(user=urec[0])

        # Build Happiness DB
        for i, rec in self.testdf.iterrows():
            user = User.objects.get(username=rec.user)
            Happiness.objects.get_or_create(user=user, entry_date=rec.entry_date, happiness_level=rec.happiness)

    def test_request(self):
        today = datetime.now().date().strftime('%Y-%m-%d')
        factory = APIRequestFactory()
        request = factory.get(reverse('hp:teams_happiness'))
        view = HappinessAPI.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.unauth_res.loc[today].response)

    def test_request_auth(self):
        today = datetime.now().date().strftime('%Y-%m-%d')
        factory = APIRequestFactory()
        request = factory.get(reverse('hp:teams_happiness'))
        for user_name in self.users:
            user = User.objects.get(username=user_name)
            token = Token.objects.get(user=user)
            force_authenticate(request, user=user, token=token.key)
            view = HappinessAPI.as_view()
            response = view(request)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data,
                             self.auth_res.loc[(today, user.profile.team.team_name)].response)

    def test_request_wdate(self):
        factory = APIRequestFactory()
        for day in self.days:
            request = factory.get(reverse('hp:teams_happiness_wdate', args=(day,)))
            view = HappinessAPI.as_view()
            response = view(request, date_str=day)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, self.unauth_res.loc[day].response)

    def test_request_wdate_auth(self):
        factory = APIRequestFactory()
        for day in self.days:
            for user_name in self.users:
                request = factory.get(reverse('hp:teams_happiness_wdate', args=(day,)))
                user = User.objects.get(username=user_name)
                token = Token.objects.get(user=user)
                force_authenticate(request, user=user, token=token.key)
                view = HappinessAPI.as_view()
                response = view(request, date_str=day)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data, self.auth_res.loc[(day, user.profile.team.team_name)].response)

    def test_bad_request(self):
        factory = APIRequestFactory()
        bad_date = '2021-0152'
        request = factory.get(reverse('hp:teams_happiness_wdate', args=(bad_date,)))
        view = HappinessAPI.as_view()
        response = view(request, date_str=bad_date)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bad_request_auth(self):
        factory = APIRequestFactory()
        bad_date = '2021-13-01'
        for user_name in self.users:
            request = factory.get(reverse('hp:teams_happiness_wdate', args=(bad_date,)))
            user = User.objects.get(username=user_name)
            token = Token.objects.get(user=user)
            force_authenticate(request, user=user, token=token.key)
            view = HappinessAPI.as_view()
            response = view(request, date_str=bad_date)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
