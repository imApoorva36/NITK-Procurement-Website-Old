# Generated by Django 4.2.3 on 2023-08-27 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0017_userdata_bus_add_userdata_curr_userdata_del_sched_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='date5',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userdata',
            name='refno5',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
