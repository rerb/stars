from django.core.management.base import BaseCommand
from django.core.serializers import serialize

from stars.apps.credits.models import CreditSet, Unit

import re

IND = 2
NK = True

class Command(BaseCommand):
    args = '<creditset_id>'
    help = 'Exports a specific Creditset as JSON'
    
    def handle(self, *args, **options):
        try:
            cs = CreditSet.objects.get(pk=args[0])
        except CreditSet.DoesNotExist:
            raise CommandError('CreditSet "%s" does not exist' % args[0])
            
        json = "["
        json += serialize("json", Unit.objects.all(), use_natural_keys=NK, indent=IND)[1:-1] + ","
        json += serialize("json", [cs], use_natural_keys=NK, indent=IND)[1:-1] + ","
        json += serialize("json", cs.category_set.all(), use_natural_keys=NK, indent=IND)[1:-1] + ","
        for cat in cs.category_set.all():
            json += serialize("json", cat.subcategory_set.all(), use_natural_keys=NK, indent=IND)[1:-1] + ","
            for sub in cat.subcategory_set.all():
                json += serialize("json", sub.credit_set.all(), use_natural_keys=NK, indent=IND)[1:-1] + ","
                for credit in sub.credit_set.all():
                    json += serialize("json", credit.documentationfield_set.all(), use_natural_keys=NK, indent=IND)[1:-1] + ","
                    for df in credit.documentationfield_set.all():
                        if df.choice_set.count() > 0:
                            json += serialize("json", df.choice_set.all(), use_natural_keys=NK, indent=IND)[1:-1] + ","
                    json += serialize("json", credit.applicabilityreason_set.all(), use_natural_keys=NK, indent=IND)[1:-1] + ","
        json = re.sub(r', \n', ',\n', json)
        json = json.replace(',,', ',')
        if json.endswith(','):
            json = json[:-1]
        json += "]"
        return json