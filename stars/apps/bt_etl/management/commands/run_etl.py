import os
import requests
import shutil
import time
import uuid
from datetime import timedelta
from django.conf import settings

from django.core.management.base import BaseCommand

from stars.apps.bt_etl import (
    datapoints, institutions, reports, submissionvalues)


ETL_SCRIPTS = [
    (datapoints, "datapoint.json"),
    (institutions, "institution.json"),
    (reports, "report.json"),
    (submissionvalues, "submissionvalue.json")]

BT_HOST = os.environ.get('BT_HOST', "https://stars-bt-stage.herokuapp.com")


class Command(BaseCommand):
    help = """
        Extracts and transforms data for the STARS Benchamarking Tool
        and notifies the BT that the data is available.
    """

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.start_time = time.time()
        self.key = uuid.uuid4().get_hex()
        self.etl_dir = os.path.join(settings.MEDIA_ROOT, "etl")
        self.target_dir = os.path.join(self.etl_dir, self.key)
        print("making directory: %s" % self.target_dir)
        os.mkdir(self.target_dir)
        self.bt_host = "%s/api/etl/" % BT_HOST
        print self.bt_host

    def handle(self, *args, **options):

        self.run_etl_scripts()
        archive_name = self.package_files_for_bt()
        print("archived to: %s" % archive_name)

        response = self.trigger_bt_webworker()
        print response

        print("full export time: %s" % timedelta(
            seconds=int(time.time() - self.start_time)))

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
            base_name=self.target_dir,
            format="gztar",
            root_dir=self.etl_dir,
            base_dir=self.key)
        return archive_name

    def trigger_bt_webworker(self):

        post_data = {
            'key': self.key,
            'timestamp': '%d' % int(time.time()),
        }
        print("getting: %s" % self.bt_host)
        print(post_data)
        response = requests.post(self.bt_host, data=post_data)

        return response

    def cull_old_exports(self):
        pass

# runs the extract and transorm script
# stores the files under /media/etl/[key].tar.gz
# issues a GET request to /api/etl/?key=[key]&timestamp=[timestamp]
# exports should be deleted after some time period (a week?)
# key must be unique timestamp is the time of the export

# The tar archive must contain a directory named key. So,
# fk12jf.tar.gz should expand to a folder called fk12jf.

# It must also contain the following files:

# datapoint.json
# institution.json
# report.json
# submissionvalue.json
