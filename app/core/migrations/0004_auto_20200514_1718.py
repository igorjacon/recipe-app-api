# Generated by Django 3.0.6 on 2020-05-14 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_tag'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tag',
            new_name='Tags',
        ),
    ]