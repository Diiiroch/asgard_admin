# Generated by Django 3.2.20 on 2024-05-28 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cra', '0006_structuredevent'),
    ]

    operations = [
        migrations.CreateModel(
            name='ValidationTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('validated', models.BooleanField(default=False)),
                ('events', models.ManyToManyField(to='cra.Events')),
            ],
        ),
        migrations.DeleteModel(
            name='StructuredEvent',
        ),
    ]