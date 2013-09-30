import stars.apps.credits.models as credits_models
import stars.apps.submissions.models as submissions_models


def get_doc_field_history(documentation_field):
    """Returns the set of DocumentationFields made up of 
    `documentation_field` and all previous versions of
    `documentation_field`.
    """
    # could be get_versionsed_model_field_history.
    # or VersionedModel.get_history()
    history = [documentation_field]

    if documentation_field.previous_version:
        history += (get_doc_field_history(
            documentation_field.previous_version))
                       
    return history

def get_doc_field_submission_for_doc_field(documentation_field,
                                           institution):
    """Returns the DocumentationFieldSubmission for `documentation_field`
    and `institution`.

    Returns None if there is no matching DocumentationFieldSubmission.
    """
    doc_field_submission_class = (
        submissions_models.DocumentationFieldSubmission.get_field_class(
            documentation_field))

    all_doc_field_submissions = doc_field_submission_class.objects.filter(
        documentation_field=documentation_field)

    for doc_field_submission in all_doc_field_submissions:
        credit_submission = doc_field_submission.credit_submission
        # Skip tests:
        if credit_submission.is_test():
            continue
        credit_user_submission = credit_submission.creditusersubmission
        if (credit_user_submission.get_submissionset().institution ==
            institution):
            return doc_field_submission

    return None

def get_doc_field_submission_history(documentation_field,
                                     institution):
    history = set()

    # Candidates for display in history tab:
    documentation_field_history = get_doc_field_history(
        documentation_field=documentation_field)
    
    for historical_documentation_field in documentation_field_history:

        # Don't include this DocumentationField in the history:
        if historical_documentation_field is documentation_field:
            continue

        documentation_field_submission = (
            get_doc_field_submission_for_doc_field(
                historical_documentation_field,
                institution))

        if documentation_field_submission:
            submissionset = documentation_field_submission.get_submissionset()
        
            if (submissionset.status ==
                submissions_models.RATED_SUBMISSION_STATUS
                or submissionset.migrated_from):
                
                history.add(documentation_field_submission)

    return history

def get_doc_field_submission_history_for_credit(credit,
                                                institution):
    """Return the DocumentationFieldSubmission history for this
    `credit` and `institution`.

    History is represented as a dictionary; keys are DocumentationFields
    of `credit`, and values are data as returned by
    get_doc_field_submission_history().
    """
    history = {}
    
    for documentation_field in credit.documentationfield_set.all():
        history[documentation_field] = get_doc_field_submission_history(
            documentation_field=documentation_field,
            institution=institution)
    return history
            
                
            

    
                    
