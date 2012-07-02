from stars.tests.export_credit_content import export_credit_content

from stars.apps.credits.models import CreditSet

cs = CreditSet.objects.get(pk=4)

for cat in cs.category_set.all():
    for sub in cat.subcategory_set.all():
        for c in sub.credit_set.all():
            export_credit_content(c)