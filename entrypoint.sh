#!/bin/sh

# Apply database migrations
python /app/polls/manage.py migrate

# Load initial data
python /app/polls/manage.py loaddata /app/polls/data/polls-v4.json /app/polls/data/votes-v4.json /app/polls/data/users.json

# Start the Django server
python /app/polls/manage.py runserver 0.0.0.0:8000