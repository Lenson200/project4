# Generated by Django 4.2.6 on 2024-06-09 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0005_alter_profileimage_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='profile_image',
        ),
    ]
