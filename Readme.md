# Happiness Application

## API endpoint to access users statistics

## Running Locally

```bash
git clone https://github.com/pfbox/happiness.git
```
```bash
pip install -r requirements.txt
```
```bash
cd happiness
```
```bash
python manage.py migrate
```
```bash
python manage.py createsuperuser
```
```bash
python manage.py runserver
```
```bash
python manage.py test
```

Now you can:<br/>
a. Use the Django admin to change users and teams at 127.0.0.1:8000/admin/<br/>
b. Use API endpoint at 127.0.0.1:8000/hp/api/<br>

# Solution Description

## 1. General Assumptions
1.1. Django and virtual environment have been set up<br/>
1.2. Since it's not required for app to be reusable, I built a repo for the whole project - it can be easily cloned and ran locally.<br/>
1.3. API endpoint application "hp" is an application withing the project.<br/>
1.4. Request can be made only for one date.<br/>

## 2. Application Models
2.1. Profile, Team and Happiness.<br/>
2.2. Team - User connection is One-to-Many.<br/>
2.3. There are no Team neither Profile models exist.<br/>
2.4. Only current snapshot of user-team relation is supported (e. g. if user has been deleted all his/her records are deleted or if user changes a team the statistic goes to the new team)<br/>
2.5. The following levels of happiness used: {"Unhappy": -1, "Neutral": 0, "Happy": 1, "Ecstatic": 2} <br/>

## 3. Authentication
3.1. Token authentication method is used.<br/>

## 4. Other parameters
4.1. Time zone support is disabled.<br/>

## 5. Packages used
5.1. djangorestframework - easy to use, good for API tests.<br/>
5.2. Applications used from this package.<br/>
5.2.1. rest_framework - api support.<br/>
5.2.2. rest_framework.authtoken - token authentication support.<br/>

## 6. Application details
6.1. 3 models Profile (to save user additional info), Team and Happiness.<br/>
6.2. Support for User-->Profile-->Team relations is built into admin scheme.<br/>

## 7. Requesting data from API
7.1. Application uses single API endpoint for authenticated and unauthenticated requests.<br/>
7.1.1. if authenticated request is made it returns the number of people at each level of happiness and average happiness for the team.<br/>
7.1.2. if unauthenticated request is made it returns average happiness across all teams.<br/>

### 7.2. API Endpoint description

```bash
GET /hp/api - returns data for the current date
```
```bash
GET /hp/api/YYY-DD-MM - returns data for the specific date 
```

### 7.3 Examples
7.3.1. Unauthenticated request.
```bash
GET /hp/api/
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "report_date": "2021-06-26",
    "request_authenticated": false,
    "avg_happiness": 1.5
}
```
7.3.2. Authenticated request with valid date.
```bash
GET /hp/api/2021-06-26 {"Authentication : "Token 'need-token-key-here'"} 
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept
{
	"report_date": "2021-06-26", 
	"request_authenticated": True, 
	"team": "TestTeam2", 
	"avg_team_happiness": 0.375, 
	"people_by_level": 
		{
		"Unhappy": 2, 
		"Neutral": 2, 
		"Happy": 3, 
		"Ecstatic": 1
		}
}
```
7.3.3.example for wrong input.
```bash
GET /hp/api/2222/

HTTP 400 Bad Request
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "date": "Input 2222 is not a valid date, date must be in YYYY-MM-DD format"
}
```

## 8. Tests 
8.1. unauthenticated request returning todays average happiness.<br\>
8.2. authenticated request returning todays average team happiness.<br\>
8.3. unauthenticated request returning happiness by date.<br\>
8.4. authenticated request returning average team happiness for specific date.<br\>
8.5. unauthenticated request returning todays average happiness.<br\>

## 9. Changes to settings.py
9.1. Applications support.
```bash
INSTALLED_APPS = [
    ...
    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',

    # Local apps
    'hp',
	...
]
```
9.2. djanog-rest_framework support.
```bash
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # <-- And here
    ],
}
```
