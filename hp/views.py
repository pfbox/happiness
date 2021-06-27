from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Happiness
from django.db.models import Count, Avg
from rest_framework import status


class Index(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'content': "Hello, this is happiness api application."})


class HappinessAPI(APIView):
    # Since it wasn't specified I assume any of authentication methods
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        data = {}
        # I added single report date since there's no guidance how to treat multiple dates
        # Checking if the Report Date is provided
        date_str = kwargs.get('date_str')
        if not date_str:
            report_date = datetime.now().date()
        else:
            try:
                report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                data['Error'] = 'Input {} is not a valid date, date must be in YYYY-MM-DD format'.format(date_str)
                return Response({'date': 'Input {} is not a valid date, date must be in YYYY-MM-DD format'
                                .format(date_str)},
                                status=status.HTTP_400_BAD_REQUEST)

        if report_date:
            data['report_date'] = report_date.strftime('%Y-%m-%d')
            # Preparering dictionary for happiness levels within each team
            hp_levels = {}
            for i in Happiness.HAPPINESS_LEVELS:
                hp_levels[i[1]] = 0

            if request.auth:
                data['request_authenticated'] = True
                user = request.user
                team = user.profile.team
                items = Happiness.objects.select_related('user')\
                    .filter(user__profile__team=team, entry_date=report_date)\
                    .values('happiness_level')\
                    .annotate(count=Count('id'))

                data['team'] = team.team_name
                data['avg_team_happiness'] = Happiness.objects.select_related('user')\
                    .filter(entry_date=report_date, user__profile__team=team)\
                    .aggregate(avg_happiness=Avg('happiness_level'))['avg_happiness']

                for rec in items:
                    hp_levels[Happiness.HAPPINESS_MAP[rec['happiness_level']]] += rec['count']

                data['people_by_level'] = hp_levels
            else:
                data['request_authenticated'] = False
                data['avg_happiness'] = Happiness.objects.filter(entry_date=report_date)\
                    .aggregate(avg_happiness=Avg('happiness_level'))['avg_happiness']

        return Response(data)
