# Fixed for RENTPLAY v7.5 — handles existing constraints gracefully.

from django.db import migrations, models
import django.core.validators


def add_constraint_if_not_exists(apps, schema_editor, model_name, fields, constraint_name):
    """Add a UniqueConstraint only if it doesn't already exist in PostgreSQL."""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT conname FROM pg_constraint
            WHERE conname = %s AND conrelid = (
                SELECT oid FROM pg_class WHERE relname = %s
            )
        """, [constraint_name, 'rentplay_' + model_name])
        if not cursor.fetchone():
            # Constraint doesn't exist — create it via SQL
            field_list = ', '.join(fields)
            cursor.execute(
                f'ALTER TABLE rentplay_{model_name} ADD CONSTRAINT {constraint_name} UNIQUE ({field_list})'
            )


def add_district_constraint(apps, schema_editor):
    add_constraint_if_not_exists(apps, schema_editor, 'district', ['city_id', 'name'], 'unique_district_per_city')


def add_property_constraint(apps, schema_editor):
    add_constraint_if_not_exists(apps, schema_editor, 'property', ['agency_id', 'title'], 'unique_property_title_per_agency')


def add_review_constraint(apps, schema_editor):
    add_constraint_if_not_exists(apps, schema_editor, 'review', ['user_id', 'property_unit_id'], 'unique_review_per_user_property')


def add_wishlist_constraint(apps, schema_editor):
    add_constraint_if_not_exists(apps, schema_editor, 'wishlist', ['user_id', 'property_unit_id'], 'unique_wishlist_per_user_property')


class Migration(migrations.Migration):

    dependencies = [
        ('rentplay', '0011_property_fields_models'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'get_latest_by': ['created_at'], 'ordering': ['-created_at'], 'verbose_name': 'booking', 'verbose_name_plural': 'bookings'},
        ),
        migrations.AlterModelOptions(
            name='property',
            options={'ordering': ['-is_featured', 'status', '-created_at'], 'verbose_name': '\u0648\u062d\u062f\u0629 \u0633\u0643\u0646\u064a\u0629', 'verbose_name_plural': '\u0648\u062d\u062f\u0627\u062a \u0633\u0643\u0646\u064a\u0629'},
        ),
        migrations.AlterField(
            model_name='banner',
            name='link',
            field=models.URLField(blank=True, help_text='Where users go when clicking the banner', verbose_name='link URL'),
        ),
        migrations.AlterField(
            model_name='property',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='\u0627\u0644\u0633\u0639\u0631 \u0627\u0644\u0634\u0647\u0631\u064a (\u0631\u064a\u0627\u0644)'),
        ),
        migrations.AlterField(
            model_name='property',
            name='price_annual',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='\u0627\u0644\u0633\u0639\u0631 \u0627\u0644\u0633\u0646\u0648\u064a (\u0631\u064a\u0627\u0644)'),
        ),
        migrations.AlterField(
            model_name='property',
            name='price_daily',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='\u0627\u0644\u0633\u0639\u0631 \u0627\u0644\u064a\u0648\u0645\u064a (\u0631\u064a\u0627\u0644)'),
        ),
        migrations.AlterField(
            model_name='property',
            name='price_weekly',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='\u0627\u0644\u0633\u0639\u0631 \u0627\u0644\u0623\u0633\u0628\u0648\u0639\u064a (\u0631\u064a\u0627\u0644)'),
        ),
        # Use RunPython with existence checks instead of raw AddConstraint
        # because the constraints may already exist from a previous partial run.
        migrations.RunPython(add_district_constraint, migrations.RunPython.noop),
        migrations.RunPython(add_property_constraint, migrations.RunPython.noop),
        migrations.RunPython(add_review_constraint, migrations.RunPython.noop),
        migrations.RunPython(add_wishlist_constraint, migrations.RunPython.noop),
    ]
