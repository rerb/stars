"""Figures requested for the annual report.

   XX% of 2014 STARS Rated Institutions were AASHE Members

   XX% of 2014 STARS Current Participants were AASHE Members

   XX% of institutions that were using STARS at the beginning of 2014
   became full-access subscribers during that year
"""
import datetime

from stars.apps.institutions.models import Institution, Subscription
from stars.apps.submissions.models import SubmissionSet


start = datetime.date(2014, 1, 1)
end = datetime.date(2014, 12, 31)

print """
#############################################################
# XX% of 2014 STARS Current Participants were AASHE Members #
#############################################################

subscriber: an Institution that had a valid subscription in 2014.
"""
members = 0.0
subscribers = set()

for sub in Subscription.objects.filter(
        end_date__gte=start).filter(start_date__lt=end):

    subscribers.add(sub.institution)

for subscriber in subscribers:

    if subscriber.is_member:
        members += 1

print '2014 subscribers:', len(subscribers)
print '         members:', members,
print '(' + str((members / len(subscribers)) * 100) + '%)'


print """
###########################################################
# XX% of 2014 STARS Rated Institutions were AASHE Members #
###########################################################"""
rated = 0.0
members = 0.0
institutions = set()

for ss in SubmissionSet.objects.filter(
        date_submitted__gte=start).filter(date_submitted__lte=end):

    if not ss.rating:
        pass

    institutions.add(ss.institution)

for inst in institutions:

    rated += 1

    if inst.is_member:
        members += 1

print '2014 rated institutions:', rated
print '                members:', members,
print '(' + str((members / rated) * 100) + '%)'

print """
######################################################################
# XX% of institutions that were using STARS at the beginning of 2014 #
# became full-access subscribers during that year                    #
######################################################################"""
upgrades = 0.0

for inst in Institution.objects.filter(date_created__lte=start):

    for ss in Subscription.objects.filter(
            institution=inst).order_by('start_date'):
        # If this Inst had a subscription before this year, skip it:
        if ss.start_date < start:
            break
        elif ss.start_date <= end:
            upgrades += 1

print '2014 subscribers:', len(subscribers)
print '        upgrades:', upgrades,
print '(' + str((upgrades / len(subscribers)) * 100) + '%)'
