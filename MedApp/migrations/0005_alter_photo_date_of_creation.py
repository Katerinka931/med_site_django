# Generated by Django 4.1 on 2022-12-29 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MedApp', '0004_remove_patient_diagnosys_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='date_of_creation',
            field=models.DateTimeField(null=True),
        ),
    ]