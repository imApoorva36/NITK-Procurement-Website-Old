# Generated by Django 4.2.3 on 2023-08-12 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0009_userdata_venue'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='warranty',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
