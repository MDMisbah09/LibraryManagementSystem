# Generated by Django 5.0.1 on 2024-05-28 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='library',
            name='returned_on',
            field=models.DateField(blank=True, null=True),
        ),
    ]
