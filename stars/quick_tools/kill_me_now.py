import datetime

from stars.apps.institutions.management.commands import restore_institution
from stars.apps.submissions.models import CreditUserSubmission


def check_match(left, right):

    left_submissionset, right_submissionset = (
        left.get_submissionset(), right.get_submissionset())

    if left_submissionset.pk == right_submissionset.pk:
        return (True, None)
    else:
        return (False, "get_submissionset().pk values differ")


matched = []
unmatched = []
updated = live_is_more_recent = 0


def update_all_credit_user_submissions():

    global matched, unmatched, updated, live_is_more_recent

    for cus in CreditUserSubmission.objects.using("stars-backup").filter(
            last_updated__gt=datetime.date(2019, 04, 01)):

        try:
            live_match = CreditUserSubmission.objects.using("default").get(
                pk=cus.pk)
        except CreditUserSubmission.DoesNotExist:
            unmatched.append(cus)
        else:
            matches, error_message = check_match(cus, live_match)
            if matches:
                matched.append(cus)
            else:
                print cus.pk, "check_match error:", error_message
                unmatched.append(cus)

        if live_match.last_updated < cus.last_updated:
            try:
                restore_institution.restore_credit_user_submission(
                    credit_user_submission=cus,
                    source_db="stars-backup",
                    target_db="default")
            except Exception as exc:
                print live_match.pk, " not updated:", exc
            else:
                updated += 1

        else:
            live_is_more_recent += 1


def report():
    print(len(matched), "matched")
    print(len(unmatched), "unmatched")
    print("updated: " + str(updated))
    print("live_is_more_recent: " + str(live_is_more_recent))


def handle_unmatched():

    import ipdb; ipdb.set_trace()

    for nomatch in unmatched:
        # No CreditUserSubmission with same pk.  How can that
        # happen?  Shouldn't all CreditUserSubmissions extant
        # on 4/4/2019 still be in the live system?
        print nomatch
