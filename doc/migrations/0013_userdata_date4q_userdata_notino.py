# Generated by Django 4.2.3 on 2023-08-16 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0012_userdata_addsheet'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='date4q',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userdata',
            name='notino',
            field=models.TextField(blank=True, null=True),
        ),
    ]
