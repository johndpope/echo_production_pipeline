# Generated by Django 3.0 on 2019-12-31 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EchoAnalyzer', '0009_auto_20191231_0034'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='processing_time',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='visit',
            name='processing_time',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
