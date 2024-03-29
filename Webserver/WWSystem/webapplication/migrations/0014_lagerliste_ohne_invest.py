# Generated by Django 4.2.10 on 2024-03-13 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapplication', '0013_delete_templagerliste'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lagerliste_ohne_Invest',
            fields=[
                ('id', models.IntegerField(db_column='id', primary_key=True, serialize=False)),
                ('typ', models.CharField(db_column='Typ', max_length=20)),
                ('modell', models.CharField(db_column='Modell', max_length=20)),
                ('spezifikation', models.TextField(blank=True, db_column='Spezifikation', null=True)),
                ('ausgabe', models.DateTimeField(blank=True, db_column='Ausgabe', null=True)),
                ('ausgegeben', models.CharField(db_column='Ausgegeben', max_length=1)),
            ],
            options={
                'db_table': 'Lagerliste_ohne_Invest',
                'managed': False,
            },
        ),
    ]
