# Generated by Django 5.1.1 on 2025-02-13 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapplication', '0021_investmittelplan_alt'),
    ]

    operations = [
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='Download/')),
                ('hochgeladen', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
