from stars.apps.institutions.models import Institution

def run_update():
    print "RUNNING Update"

    for i in Institution.objects.all():
        # o = i.profile
        # if i.name != o.org_name:
        print i.name
        # print "%s\n" % o.org_name
        i.update_from_iss()
        i.save()

if __name__ == '__main__':
    run_update()
