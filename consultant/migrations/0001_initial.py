# Generated by Django 3.2.20 on 2024-02-26 14:17

import consultant.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_client', models.CharField(max_length=255)),
                ('domaine', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': 'client',
                'verbose_name_plural': 'clients',
            },
        ),
        migrations.CreateModel(
            name='consultant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clients', models.ManyToManyField(to='consultant.client')),
                ('utilisateur', models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'consultant',
                'verbose_name_plural': 'consultants',
            },
        ),
        migrations.CreateModel(
            name='mission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_de_debut', models.DateField()),
                ('date_de_fin', models.DateField()),
                ('intitule', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default=None, null=True)),
                ('client_concerne', models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='consultant.client')),
                ('consultant', models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='consultant.consultant')),
            ],
            options={
                'verbose_name': 'mission',
                'verbose_name_plural': 'missions',
            },
        ),
        migrations.CreateModel(
            name='contrat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debut_contrat', models.DateField()),
                ('fin_contrat', models.DateField()),
                ('fichier', models.FileField(upload_to='')),
                ('titulaire', models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='consultant.consultant')),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nom', models.CharField(blank=True, default=None, max_length=20)),
                ('Prenom', models.CharField(blank=True, default=None, max_length=20)),
                ('date_de_naissance', models.DateField(blank=True, default=None, null=True)),
                ('genre', models.CharField(choices=[('HOMME', 'HOMME'), ('FEMALE', 'FEMALE')], max_length=6)),
                ('email', models.EmailField(blank=True, default=None, max_length=254, null=True)),
                ('tel', models.CharField(blank=True, default=None, max_length=20, validators=[consultant.models.validate_phone_number])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]