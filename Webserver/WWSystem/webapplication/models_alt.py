# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class BestellListe(models.Model):
    sap_bestell_nr_field = models.IntegerField(db_column='SAP_Bestell_Nr.', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    modell = models.CharField(db_column='Modell', max_length=20)  # Field name made lowercase.
    typ = models.CharField(db_column='Typ', max_length=20)  # Field name made lowercase.
    menge = models.IntegerField(db_column='Menge')  # Field name made lowercase.
    spezifikation = models.TextField(db_column='Spezifikation', blank=True, null=True)  # Field name made lowercase.
    inventarnummern_von_bis = models.TextField(db_column='Inventarnummern Von-Bis', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    ersteller = models.ForeignKey('WebapplicationUser', models.DO_NOTHING, db_column='Ersteller', to_field='username', blank=True, null=True)  # Field name made lowercase.
    geliefert = models.CharField(db_column='Geliefert', max_length=1)  # Field name made lowercase.
    geliefert_anzahl = models.IntegerField(db_column='Geliefert_Anzahl', blank=True, null=True)  # Field name made lowercase.
    preis_pro_stück = models.SmallIntegerField(db_column='Preis_pro_Stück')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Bestell_Liste'

    def __str__(self):
        return str(self.sap_bestell_nr_field)


class Investmittelplan(models.Model):
    klinik_ou = models.IntegerField(db_column='Klinik_OU', primary_key=True)  # Field name made lowercase.
    investmittel_jahresanfang_in_euro = models.DecimalField(db_column='Investmittel_Jahresanfang_in_Euro', max_digits=6, decimal_places=2)  # Field name made lowercase.
    investmittel_übrig_in_euro = models.DecimalField(db_column='Investmittel_übrig_in_Euro', max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Investmittelplan'


class Lagerliste(models.Model):
    inventarnummer = models.IntegerField(db_column='Inventarnummer', primary_key=True)  # Field name made lowercase.
    klinik = models.IntegerField(db_column='Klinik', blank=True, null=True)  # Field name made lowercase.
    typ = models.CharField(db_column='Typ', max_length=20)  # Field name made lowercase.
    modell = models.CharField(db_column='Modell', max_length=20)  # Field name made lowercase.
    spezifikation = models.TextField(db_column='Spezifikation', blank=True, null=True)  # Field name made lowercase.
    investmittel = models.CharField(db_column='Investmittel', max_length=4)  # Field name made lowercase.
    bestell_nr_field = models.ForeignKey(BestellListe, models.DO_NOTHING, db_column='Bestell_Nr.')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    herausgeber = models.ForeignKey('WebapplicationUser', models.DO_NOTHING, db_column='Herausgeber', to_field='username', blank=True, null=True)  # Field name made lowercase.
    ausgabe = models.DateTimeField(db_column='Ausgabe', blank=True, null=True)  # Field name made lowercase.
    ausgegeben = models.CharField(db_column='Ausgegeben', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Lagerliste'

    def __str__(self):
        return str(self.bestell_nr_field)


class TempLagerliste(models.Model):
    inventarnummer = models.IntegerField(db_column='Inventarnummer', primary_key=True)  # Field name made lowercase.
    klinik = models.IntegerField(db_column='Klinik', blank=True, null=True)  # Field name made lowercase.
    typ = models.CharField(db_column='Typ', max_length=20)  # Field name made lowercase.
    modell = models.CharField(db_column='Modell', max_length=20)  # Field name made lowercase.
    spezifikation = models.TextField(db_column='Spezifikation', blank=True, null=True)  # Field name made lowercase.
    investmittel = models.CharField(db_column='Investmittel', max_length=4)  # Field name made lowercase.
    herausgeber = models.ForeignKey('WebapplicationUser', models.DO_NOTHING, db_column='Herausgeber', to_field='username', blank=True, null=True)  # Field name made lowercase.
    ausgabe = models.DateTimeField(db_column='Ausgabe', blank=True, null=True)  # Field name made lowercase.
    ausgegeben = models.CharField(db_column='Ausgegeben', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Temp_Lagerliste'