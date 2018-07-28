import datetime
import os
import os.path
import shutil
import subprocess
import tarfile
import uuid

import requests
from django.core.management.base import BaseCommand, CommandError

ETL_SCRIPTS = ["datapoints.py",
               "institutions.py",
               "reports.py",
               "submission_data.py"]

ETL_EXTRACTS = ["datapoints.json",
                "institutions.json",
                "reports.json",
                "submission_data.json"]


class Command(BaseCommand):
    help = "Starts Benchmarking Tool ETL process."

    def handle(self, *args, **options):

        self.run_etl_scripts()

        key = uuid.uuid4().get_hex()

        target_subdirectory = os.path.sep.join(["/media/etl", key])

        os.mkdir(target_subdirectory)

        for etl_extract in ETL_EXTRACTS:
            shutil.move(etl_extract, target_subdirectory)

        archive_name = self.package_files_for_bt(
            key=key,
            subdirectory=target_subdirectory

        response = trigger_bt_webworker(archive_name)

        cull_old_exports()

    def run_etl_scripts(self, subdirectory):
        """Runs ETL scripts, returns list of files generated."""
        for etl_script in ETL_SCRIPTS:
            subprocess.call(os.path.sep.join(["bt/bt_etl", etl_script]))

    def package_files_for_bt(self, key, subdirectory):
        """Takes `files` and compresses them and puts them in a special
        place.  Returns compressed file."""
        archive_name = os.path.sep.join([subdirectory, key])
        shutil.make_archive(base_name=archive_name,
                            format=gztar,
                            root_dir=subdirectory)
        return archive_name

    def trigger_bt_webworker(self, key):
        timestamp = datetime.datetime.isoformat(datetime.datetime.now())

        url = "{host}:{port}//api/etl/?key={key}&time={timestamp}".format(
            host="localhost", port="8080", key=key, timestamp=timestamp)

        response = requests.get(url)

        return response

    def cull_old_exports():
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
