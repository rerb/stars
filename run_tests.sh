#! /bin/bash

APPS="accounts credit_editor credits custom_forms data_displays forms
      helpers institutions manage migrations my_submission notifications
      old_cms registration staff_tool submissions tasks test_factories
      third_parties api download_async_task"

coverage run manage.py test ${APPS} --liveserver=
