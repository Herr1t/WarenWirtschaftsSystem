# Generated by Django 5.1.1 on 2025-02-11 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapplication', '0017_achievements'),
    ]

    operations = [
        migrations.CreateModel(
            name='Download',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titel', models.CharField(max_length=100)),
                ('dateipfad', models.FileField(upload_to='Download/')),
                ('hochgeladen', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
