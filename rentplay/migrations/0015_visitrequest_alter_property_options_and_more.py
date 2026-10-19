# Empty migration — replaced by 0016 for safety
# This ensures Django migration history stays clean

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rentplay', '0014_v8_sale_customers_requests'),
    ]

    operations = [
        # No operations — everything moved to 0016
    ]
