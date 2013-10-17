import collections
import itertools
import functools

import ordered_set

from stars.apps.submissions.models import (RATED_SUBMISSION_STATUS,
                                           SubmissionSet)

"""
Ben's psuedocode:

previousSubmissionGroup = Rated submissions and MigratedFromSubmission

for each documentationFieldSubmission in currentSubmissionSet:
	for each previousSubmissionSet in previousSubmissionGroup:
		follow documentationFieldSubmission.documentation_field.previous_version tree to an olddocumentationfield that is in previousSubmissionSet.creditset
		find oldDocumentationFieldSubmission with previousSubmissionSet as parent and olddocumentationfield as documentation_field:
			print oldDocumentationField value
"""

def get_submissionsets_to_include_in_history(institution):
    """Returns the list of SubmissionSets for `institution` that
    should be included in CreditUserSubmission history reports.

    SubmissionSets are included if 

      1. they're rated, or 

      2. they were migrated to a new SubmissionSet, or

      3. they are the current SubmissionSet for `institution`.
    """
    submissionsets = ordered_set.OrderedSet()
    for submissionset in SubmissionSet.objects.filter(
            institution=institution):
        if ((submissionset.status ==
             RATED_SUBMISSION_STATUS)
            or
            submissionset.migrated_from):
            submissionsets.add(submissionset)
    submissionsets.add(institution.current_submission)
    return submissionsets

def get_all_doc_field_versions(doc_field):
    """Returns all versions of a DocumentationField in a 
    dictionary keyed by CreditSet.
    """
    versions = {}
    for version in doc_field.get_all_versions():
        versions[version.get_creditset()] = version
    return versions

# memoize from https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize:
def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer

@memoize
def get_all_doc_field_subs_in_submissionset(submissionset):
    """Returns all DocumentationFieldSubmissions for `submissionset`
    as a dictionary keyed by related DocumentationFields.
    """
    doc_field_subs = {}
    
    for cat_sub in submissionset.categorysubmission_set.all():
        for subcat_sub in cat_sub.subcategorysubmission_set.all():
            for credituser_sub in subcat_sub.creditusersubmission_set.all():
                for doc_field_sub in credituser_sub.get_submission_fields():
                    doc_field_subs[doc_field_sub.documentation_field] = (
                        doc_field_sub)
    return doc_field_subs

def get_credit_submission_history(credit_submission):
    """Returns historical DocumentationFieldSubmissions for
    `credit_submission` as a dictionary, keyed by the related
    DocumentationField.

    Only DocumentationFieldSubmissions in SubmissionSets that
    pass the get_submissionsets_to_include_in_history() filter
    are included.
    """
    history = collections.OrderedDict()
    
    historical_submissionsets = get_submissionsets_to_include_in_history(
        institution=credit_submission.get_submissionset().institution)

    for doc_field_submission in credit_submission.get_submission_fields():

        # All versions of the DocumentationField for this
        # DocumentationFieldSubmission:
        all_doc_fields = get_all_doc_field_versions(
            doc_field_submission.documentation_field)
        
        if all_doc_fields:
            
            for submissionset in historical_submissionsets:
                # A version of the DocumentationField for this
                # DocumentationFieldSubmission in this submissionset:
                try:
                    all_doc_field = (
                        all_doc_fields[submissionset.creditset])
                except KeyError:
                    continue

                # Find DocumentationFieldSubmission in submissionset,
                # for all_doc_field:
                all_doc_field_subs_in_submissionset = (
                    get_all_doc_field_subs_in_submissionset(submissionset))

                if all_doc_field in all_doc_field_subs_in_submissionset:
                    try:
                        history[
                            doc_field_submission.documentation_field].append(
                                all_doc_field_subs_in_submissionset[
                                    all_doc_field])
                    except KeyError:
                        history[doc_field_submission.documentation_field] = [
                            all_doc_field_subs_in_submissionset[
                                all_doc_field]]

    return history

