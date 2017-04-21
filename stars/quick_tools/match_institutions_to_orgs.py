from iss.models import Organization

from quick_tools.org_ids import org_ids
from apps.institutions.models import Institution, MemberSuiteInstitution


for i in Institution.objects.filter(ms_institution=None):
    try:
        org = Organization.objects.get(org_name=i.name)
    except Exception as exc:
        if i.name in org_ids.keys():
            try:
                org = Organization.objects.get(salesforce_id=org_ids[i.name])
            except Exception as exc2:
                Organization.DoesNotExist
                print i.name, exc2
        else:
            print i.name, exc
            continue

    assert(org.salesforce_id != None)

    i.salesforce_id = org.salesforce_id

    try:
        msi = MemberSuiteInstitution.objects.get(org_name=i.name)
    except MemberSuiteInstitution.DoesNotExist as exc:
        print exc
        pass
    except MemberSuiteInstitution.MultipleObjectsReturned as exc:
        print exc
        pass
    else:
        i.ms_institution = msi

    try:
        i.save()
    except Exception as exc:
        print "COULDN'T SAVE INSTITUTION: ", exc
