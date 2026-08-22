# Generated manually for RENTPLAY v7.2

from django.db import migrations, models
import django.db.models.deletion


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
        migrations.RemoveConstraint(
            model_name='waitlist',
            name='unique_waitlist_per_user_property',
        ),
        migrations.AddConstraint(
            model_name='waitlist',
            constraint=models.UniqueConstraint(condition=models.Q(('user__isnull', False)), fields=('user', 'property_unit'), name='unique_waitlist_per_user_property'),
        ),
    ]
