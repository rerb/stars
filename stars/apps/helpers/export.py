import csv

def export_to_file(model, filepath):
    writer = csv.writer(open('ta_app.csv', 'w'))
    # Write headers to CSV file
    headers = []
    for field in model._meta.fields:
        headers.append(field.name)
    for m in model._meta.many_to_many:
        headers.append(m.name)
    writer.writerow(headers)
    # Write data to CSV file
    for obj in model.objects.all().order_by("id"):
        row = []
        for field in model._meta.fields:
            row.append(getattr(obj, field.name))
        for m in model._meta.many_to_many:
            m_string = ""
            m2m = getattr(obj, m.name)
            for r in m2m.order_by('id'):
                m_string += "%s\n" % r
            row.append(m_string)
            
        writer.writerow(row)