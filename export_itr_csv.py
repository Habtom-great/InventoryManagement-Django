import os
import django
import csv
# Replace 'core.settings' with the path to your settings.py module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # change 'core.settings' if your settings module is different
django.setup()

# Import your model (adjust to your actual model name and app)
from transactions.models import ITRRecord  # match the actual model name
 # replace with your model name

# Export CSV
with open('ITR_records.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write header
    writer.writerow([
        'id', 'project', 'area', 'system', 'discipline', 'itr_id', 'description',
        'status', 'completion_date', 'punch_item', 'punch_status',
        'responsible_person', 'priority', 'remarks'
    ])
    
    # Write data rows
    for record in ITRRecord.objects.all():
        writer.writerow([
            record.id,
            record.project,
            record.area,
            record.system,
            record.discipline,
            record.itr_id,
            record.description,
            record.status,
            record.completion_date,
            record.punch_item,
            record.punch_status,
            record.responsible_person,
            record.priority,
            record.remarks,
        ])

print("✅ Export completed: ITR_records.csv")
