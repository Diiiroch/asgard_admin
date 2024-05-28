# Generated by Django 3.2.20 on 2024-05-24 13:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('consultant', '0003_consultant_tjm'),
        ('cra', '0003_auto_20240522_1624'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_table_sum', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tjm', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price_ht', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price_ttc', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consultant.consultant')),
            ],
        ),
    ]
