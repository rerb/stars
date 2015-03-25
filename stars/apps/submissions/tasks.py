"""
    Celery tasks
"""
from logging import getLogger
import sys

from stars.apps.submissions.export.pdf import build_certificate_pdf
from stars.apps.submissions.export.excel import build_report_export
from stars.apps.submissions.models import SubmissionSet
from stars.apps.migrations.utils import (migrate_ss_version,
                                         migrate_submission,
                                         create_ss_mirror)
from stars.apps.notifications.models import EmailTemplate
from stars.apps.credits.models import CreditSet
from stars.apps.submissions.api import (SummaryPieChart,
                                        CategoryPieChart,
                                        SubategoryPieChart)
from stars.apps.institutions.models import MigrationHistory

from django.core.cache import cache

from celery.decorators import task

import datetime

logger = getLogger('stars.user')

@task()
def hello_world():
    " A simple test task so I can test celery "
    print >> sys.stdout, "Hello World"

@task()
def build_pdf_export(ss):
    print "starting pdf export(ss: %d)" % ss.id
#     s = False
#     if ss.pdf_report:
#         print "existing report %s" % ss.pdf_report)
#         return str(ss.pdf_report)
#     s = True
    pdf = ss.get_pdf()
#     pdf = build_certificate_pdf(ss)
#     from django.core.files.temp import NamedTemporaryFile
#     tempfile = NamedTemporaryFile(suffix='.pdf', delete=False)
#     tempfile.write(pdf.getvalue())
#     tempfile.close()
#
#     print tempfile.name
    print "pdf export done(ss: %d)" % ss.id
    return str(pdf)

@task()
def build_excel_export(ss):
    print "starting excel export(ss: %d)" % ss.id
    report = build_report_export(ss)
    print "excel export done(ss: %d)" % ss.id
    return report

@task()
def build_certificate_export(ss):
    print "starting certificate export(ss: %d)" % ss.id
    # cert_pdf = build_certificate_pdf(ss)
    pdf = build_certificate_pdf(ss)
    from django.core.files.temp import NamedTemporaryFile
    tempfile = NamedTemporaryFile(suffix='.pdf', delete=False)
    tempfile.write(pdf.getvalue())
    tempfile.close()
    print "cert export done(ss: %d)" % ss.id
    return tempfile.name

@task()
def send_certificate_pdf(ss):

    pdf = build_certificate_pdf(ss)

    et = EmailTemplate.objects.get(slug='certificate_to_staff')
    email_context = {"ss": ss}
    et.send_email(
                    mail_to=['monika.urbanski@aashe.org'],
                    context=email_context,
                    attachments=((ss.institution.slug, pdf.getvalue(), 'application/pdf'),),
                    title="New Certificate: %s" % ss)


@task()
def perform_migration(old_ss, new_cs, user):
    """
        Run the migration and then
        email the Liaison, copying the user
        (if the emails are different)
    """

    new_ss = migrate_ss_version(old_ss, new_cs)

    email_to = [old_ss.institution.contact_email]
    if user.email not in email_to:
        email_to.append(user.email)

    try:
        et = EmailTemplate.objects.get(slug='migration_success')
        email_context = {"old_ss": old_ss, "new_ss": new_ss}
        et.send_email(email_to, email_context)

    except EmailTemplate.DoesNotExist:
        logger.error('Migration email template missing',
                     extra={'user': user}, exc_info=True)

    mh = MigrationHistory(institution=new_ss.institution,
                          source_ss=old_ss,
                          target_ss=new_ss)
    mh.save()


@task()
def perform_data_migration(old_ss, user):
    """
        Just duplicates a submission and archives the old one

        A data migration pulls in data but doesn't use the latest creditset,
        it simply keeps the current creditset.
    """
    new_ss = create_ss_mirror(
        old_ss,
        new_cs=old_ss.institution.current_submission.creditset,
        registering_user=user)
    new_ss.is_locked = False
    new_ss.save()

    old_ss.institution.current_submission = new_ss
    old_ss.institution.save()

    mh = MigrationHistory(institution=new_ss.institution,
                          source_ss=old_ss,
                          target_ss=new_ss)
    mh.save()


@task()
def migrate_purchased_submission(old_ss, new_ss):
    """
        Hide the submission, move the data from the old_ss
        and then unhide it
    """
    new_ss.is_visible = False
    new_ss.is_locked = True
    new_ss.save()

    migrate_submission(old_ss, new_ss)

    new_ss.is_visible = True
    new_ss.is_locked = False
    new_ss.save()

@task()
def rollover_submission(old_ss):
    new_ss = create_ss_mirror(old_ss)
    new_ss.is_locked = False
    new_ss.is_visible = True
    new_ss.save()
    new_ss.institution.current_submission = new_ss
    new_ss.institution.save()


def update_pie_api_cache():
    """
        Clear each endpoint's cache and then re-fetch it
    """
    cs = CreditSet.objects.get(pk=5)

    from tastypie.api import Api

    v1_api = Api(api_name='v1')
    v1_api.register(SummaryPieChart())
    v1_api.register(CategoryPieChart())
    v1_api.register(SubategoryPieChart())

    summary_view = SummaryPieChart()
    cat_view = CategoryPieChart()
    s_view = SubategoryPieChart()

    key = "v1:summary-pie-chart:detail:"
    print key
    cache.delete(key)

    summary = summary_view.obj_get_list()

    # summary
    for cat in cs.category_set.filter(include_in_score=True):
        print cat
        kwargs = {"pk": cat.id,}
        c_key = cat_view.generate_cache_key('detail', **kwargs)
#        c_key = 'v1:category-pie-chart:detail:pk=%d' % cat.id
        print c_key
        cache.delete(c_key)
        cat_view.obj_get(**kwargs)

        for sub in cat.subcategory_set.all():
            print sub
            kwargs = {"pk": sub.id}
            s_key = s_view.generate_cache_key('detail', **kwargs)
#            s_key = "v1:subcategory-pie-chart:detail:pk=%d" % sub.id
            print s_key
            cache.delete(s_key)

            s_view.obj_get(**kwargs)


def expireRatings():
    """
        Mark submissions as expired if they are over 3 years old
        and adjust the institution's current rating appropriately
    """

    today = datetime.date.today()
    td = datetime.timedelta(days=365 * 3)  # 3 years

    # all rated submissions that haven't already expired
    for ss in SubmissionSet.objects.filter(status="r").exclude(expired=True):

        if ss.date_submitted + td < today:
            print ""  # newline
            print "Expired: %s" % ss
            print "Date Submitted: %s" % ss.date_submitted
            ss.expired = True
            ss.save()

            # update the institution if this is still their latest rated submission
            i = ss.institution
            if i.rated_submission == ss:
                print "**Only Rating (dropping current rating)"
                i.rated_submission = None
                i.current_rating = None
                i.latest_expired_submission = ss
                i.save()
