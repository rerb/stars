from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from stars.apps.bt_etl import (
    datapoints, institutions, reports, submissionvalues)

import datetime
import os
import requests
import shutil
import subprocess
import tarfile
import time
import uuid


ETL_SCRIPTS = [
    (datapoints, "datapoint.json"),
    (institutions,"institution.json"),
    (reports,"report.json"),
    (submissionvalues, "submissionvalue.json")]

# this should probably be an environment variable
BT_URL = os.environ.get('BT_URL', "https://stars-bt-stage.herokuapp.com")


class Command(BaseCommand):
    help = "Starts Benchmarking Tool ETL process."
    
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        
        self.key = uuid.uuid4().get_hex()
        self.etl_dir = os.path.join(settings.MEDIA_ROOT, "etl")
        self.target_dir = os.path.join(self.etl_dir, self.key)
        print("making directory: %s" % self.target_dir)
        os.mkdir(self.target_dir)
        self.bt_url = "%s/api/etl/" % BT_URL
        print self.bt_url

    def handle(self, *args, **options):

        self.run_etl_scripts()
        archive_name = self.package_files_for_bt()
        print("archived to: %s" % archive_name)

        response = self.trigger_bt_webworker()
        print response

        # cull_old_exports()

    def run_etl_scripts(self):
        """Runs ETL scripts, returns list of files generated."""
        for etl_script, outfile in ETL_SCRIPTS:
            print("running script: %s" % etl_script)
            out_path = os.path.join(self.target_dir, outfile)
            etl_script.extract_and_transform(out_path)
            
    def package_files_for_bt(self):
        """ Compresses the data and puts them in a special
        place.  Returns compressed file name."""
        archive_name = shutil.make_archive(
            base_name=os.path.join(self.etl_dir, self.key),
            format="gztar",
            root_dir=self.target_dir)
        return archive_name

    def trigger_bt_webworker(self):

        post_data = {
            'key': self.key,
            'timestamp': '%d' % int(time.time()),
        }
        print("getting: %s" % self.bt_url)
        print(post_data)
        response = requests.post(self.bt_url, data=post_data)

        return response

    def cull_old_exports(self):
        pass

# runs the extract and transorm script
# stores the files under /media/etl/[key].tar.gz
# issues a GET request to /api/etl/?key=[key]&time=[timestamp]
# exports should be deleted after some time period (a week?)
# key must be unique timestamp is the time of the export

# The tar archive must contain a director named key. So, fk12jf.tar.gz should expand to a folder called fk12jf.

# It must also contain the following files:

# datapoint.json
# institution.json
# report.json
# submissionvalue.json
