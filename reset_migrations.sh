#!/bin/sh
APPS="migrations custom_forms helpers third_parties notifications old_cms registration tasks submissions institutions credits data_displays"

for APP in $APPS
do
    echo "\n** $APP ** "
    read _
    ./manage.py migrate $APP 0001 --fake --delete-ghost-migrations
done
