# Generated by Django 4.2.3 on 2023-08-16 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0011_userdata_listnadd_userdata_suppliers'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='addsheet',
            field=models.FileField(blank=True, null=True, upload_to='users/addsheets/'),
        ),
    ]
