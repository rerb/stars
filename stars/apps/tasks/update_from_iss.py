from stars.apps.institutions.models import Institution

for i in Institution.objects.all():
    o = i.profile
    if i.name != o.org_name:
        print i.name
        print "%s\n" % o.org_name
        i.name = o.org_name
        i.save()