#! /bin/bash

APPS="stars.apps.accounts stars.apps.api stars.apps.credits
      stars.apps.custom_forms stars.apps.helpers stars.apps.helpers.forms
      stars.apps.institutions stars.apps.institutions.data_displays
      stars.apps.migrations stars.apps.notifications stars.apps.registration
      stars.apps.submissions stars.apps.tasks stars.test_factories
      stars.apps.tool.credit_editor stars.apps.tool.manage
      stars.apps.tool.my_submission"

coverage run manage.py test ${APPS} --nomigrations --liveserver=
