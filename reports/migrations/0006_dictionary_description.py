# Generated by Django 5.2.1 on 2025-05-26 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_templatefield_field_type_templatefield_max_value_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dictionary',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
