# Generated by Django 3.2.20 on 2024-04-30 09:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('consultant', '0002_auto_20240429_1259'),
        ('conge', '0002_auto_20240429_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventconge',
            name='consultant',
            field=models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='consultant.consultant'),
        ),
    ]
