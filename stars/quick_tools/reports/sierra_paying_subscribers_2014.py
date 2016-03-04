"""
    From Julian: It would really help if I could provide information about how
    what proportion of submissions to Sierra are from paying STARS users vs
    non-paying reporters/snapshot takers.
"""

from stars.apps.submissions.models import SubmissionSet
from stars.apps.third_parties.models import ThirdParty
import datetime

date_window = (
    datetime.date(year=2013, month=6, day=1),
    datetime.date(year=2014, month=6, day=1)
)
sierra = ThirdParty.objects.get(slug="sierra")

# get the list of insitutions with snapshots in the date window
i_list = []
for i in sierra.access_to_institutions.all():
    ss_qs = i.submissionset_set.filter(status='f')
    ss_qs = ss_qs.filter(date_submitted__gte=date_window[0])
    ss_qs = ss_qs.filter(date_submitted__lte=date_window[1])
    if ss_qs.count() > 0:
        i_list.append(i)

# of these insitutions which were participants and which weren't
participants = []
non_participants = []
for i in i_list:
    if i.was_participant_on_date(date_window[1]):
        participants.append(i)
    else:
        non_participants.append(i)

print "Participants: %d" % len(participants)
print "Non-participants: %d" % len(non_participants)

# get stars ratings
rating_count = 0
for i in i_list:
    ss = i.get_latest_rated_submission()
    if ss:
        rating_count += 1
print "Rated Institutions: %d" % rating_count
