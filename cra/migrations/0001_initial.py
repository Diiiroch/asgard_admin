# Generated by Django 3.2.25 on 2024-04-29 10:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('consultant', '0002_auto_20240429_1259'),
    ]

    operations = [
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.FloatField(choices=[(1, '1'), (0.5, '0.5'), (0.25, '0.25')], default=1)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('codeprojet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consultant.projet')),
            ],
        ),
    ]
