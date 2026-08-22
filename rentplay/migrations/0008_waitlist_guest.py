# Generated manually for RENTPLAY v7.2

from django.db import migrations, models
import django.db.models.deletion


def remove_constraint_if_exists(apps, schema_editor):
    """Remove the unique_waitlist_per_user_property constraint if it exists."""
    from django.db import connection
    with connection.cursor() as cursor:
        # Check if constraint exists in PostgreSQL
        cursor.execute("""
            SELECT conname FROM pg_constraint
            WHERE conname = 'unique_waitlist_per_user_property' AND conrelid = (
                SELECT oid FROM pg_class WHERE relname = 'rentplay_waitlist'
            )
        """)
        if cursor.fetchone():
            cursor.execute(
                "ALTER TABLE rentplay_waitlist DROP CONSTRAINT unique_waitlist_per_user_property"
            )


class Migration(migrations.Migration):
    dependencies = [
        ('rentplay', '0007_availability_panorama'),
    ]

    operations = [
        migrations.AddField(
            model_name='waitlist',
            name='name',
            field=models.CharField(blank=True, max_length=100, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='waitlist',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='waitlists', to='rentplay.user', verbose_name='user'),
        ),
        migrations.RunPython(remove_constraint_if_exists, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='waitlist',
            constraint=models.UniqueConstraint(condition=models.Q(('user__isnull', False)), fields=('user', 'property_unit'), name='unique_waitlist_per_user_property'),
        ),
    ]
