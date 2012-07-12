#!/bin/sh
#
# Runs all tests (listed below) for API.
# Runs 'em through coverage, and spits html report into ./api-coverage-report.
#
# Assumes it's run from the root of a STARS checkout.

SUBMISSIONS_API_TESTS="submissions.SubmissionSetResourceTestCase
                       submissions.CategorySubmissionResourceTestCase
                       submissions.SubcategorySubmissionResourceTestCase
                       submissions.CreditSubmissionResourceTestCase
                       submissions.DocumentationFieldSubmissionResourceTestCase"

CREDITS_API_TESTS="credits.CreditSetResourceTestCase credits.CategoryResourceTestCase credits.SubcategoryResourceTestCase credits.CreditResourceTestCase credits.DocumentationFieldResourceTestCase"

INSTITUTIONS_API_TESTS="institutions.InstitutionResourceTestCase"

coverage run --source=stars/apps/submissions/newapi,stars/apps/credits/api,stars/apps/institutions/api bin/django test ${SUBMISSIONS_API_TESTS} ${CREDITS_API_TESTS} ${INSTITUTIONS_API_TESTS}

coverage html --omit="*/test.py" -d api-coverage-report
