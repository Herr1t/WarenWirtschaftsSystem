# Generated by Django 4.2.10 on 2024-02-28 06:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapplication', '0005_delete_upfile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BestellListe',
        ),
        migrations.DeleteModel(
            name='Investmittelplan',
        ),
        migrations.DeleteModel(
            name='Lagerliste',
        ),
    ]
