#!/bin/bash

#echo STARTINGD RUN.SH FOR STARTING DJANGO SERVER PORT IS $PORT
#
#echo ENVIRONMENT VAIRABLES IN RUN.SH
#printenv

#Change this values for django superuser


if [ -z "$VCAP_APP_PORT" ];
  then SERVER_PORT=5000;
  else SERVER_PORT="$VCAP_APP_PORT";
fi


echo [$0] port is------------------- $SERVER_PORT
rm -rf chatbot/migrations/

python manage.py makemigrations chatblah
python manage.py migrate
# python manage.py populate_db
python manage.py collectstatic --no-input

# echo "from app import models; models.User.objects.create_superuser('${MAIL}', '${PASS}')" | python3 manage.py shell

echo [$0] Starting Django Server...
gunicorn -w 2  --preload desayunery.wsgi
