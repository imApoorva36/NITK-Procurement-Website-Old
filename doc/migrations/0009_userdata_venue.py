# Generated by Django 4.2.3 on 2023-08-11 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0008_userdata_date2_userdata_refno2'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='venue',
            field=models.TextField(blank=True, null=True),
        ),
    ]