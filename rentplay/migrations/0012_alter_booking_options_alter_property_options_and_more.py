# This file mirrors the auto-generated migration created on the production server
# (makemigrations on server). Kept here so fresh deploys stay consistent.

from django.db import migrations, models
import django.core.validators


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
        migrations.AlterUniqueTogether(
            name='district',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='property',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='waitlist',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together=set(),
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
        migrations.AddConstraint(
            model_name='district',
            constraint=models.UniqueConstraint(fields=('city', 'name'), name='unique_district_per_city'),
        ),
        migrations.AddConstraint(
            model_name='property',
            constraint=models.UniqueConstraint(fields=('agency', 'title'), name='unique_property_title_per_agency'),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('user', 'property_unit'), name='unique_review_per_user_property'),
        ),
        migrations.AddConstraint(
            model_name='wishlist',
            constraint=models.UniqueConstraint(fields=('user', 'property_unit'), name='unique_wishlist_per_user_property'),
        ),
    ]
