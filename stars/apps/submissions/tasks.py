"""
    Celery tasks
"""
from logging import getLogger
import sys

from stars.apps.submissions.pdf.export import build_certificate_pdf
from stars.apps.migrations.utils import migrate_ss_version, migrate_submission, create_ss_mirror
from stars.apps.notifications.models import EmailTemplate
from stars.apps.credits.models import CreditSet
from stars.apps.submissions.api import SummaryPieChart, CategoryPieChart, SubategoryPieChart

from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from django.core.cache import cache

from celery.decorators import task

logger = getLogger('stars.user')

@task()
def hello_world():
    " A simple test task so I can test celery "
    print >> sys.stdout, "Hello World"

@task()
def send_certificate_pdf(ss):

    pdf = build_certificate_pdf(ss)

    et = EmailTemplate.objects.get(slug='certificate_to_marnie')
    email_context = {"ss": ss}
    et.send_email(
                    mail_to=['marnie@aashe.org',],
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

@task()
def perform_data_migration(old_ss, user):
    """
        Just duplicates a submission and archives the old one
    """
    new_ss = create_ss_mirror(old_ss, registering_user=user)
    new_ss.is_locked = False
    new_ss.save()

    old_ss.institution.current_submission = new_ss
    old_ss.institution.save()


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
    cs = CreditSet.objects.get_latest()

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
