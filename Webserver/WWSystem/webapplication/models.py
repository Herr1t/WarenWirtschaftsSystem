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
    sap_bestell_nr_field = models.CharField(db_column='SAP_Bestell_Nr.', max_length=20, primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    modell = models.CharField(db_column='Modell', max_length=50)  # Field name made lowercase.
    typ = models.CharField(db_column='Typ', max_length=50)  # Field name made lowercase.
    preis_pro_stück = models.DecimalField(db_column='Preis_pro_Stück', max_digits=6, decimal_places=2)  # Field name made lowercase.
    menge = models.IntegerField(db_column='Menge')  # Field name made lowercase.
    spezifikation = models.TextField(db_column='Spezifikation', blank=True, null=True)  # Field name made lowercase.
    zuweisung = models.TextField(db_column='Zuweisung', blank=True, null=True)  # Field name made lowercase.
    inventarnummern_von_bis = models.TextField(db_column='Inventarnummern Von-Bis', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    ersteller = models.ForeignKey(User, models.DO_NOTHING, db_column='Ersteller', to_field='username', blank=True, null=True)  # Field name made lowercase.
    bearbeitet = models.DateTimeField(db_column='Bearbeitet', blank=True, null=True)  # Field name made lowercase.
    geliefert = models.CharField(db_column='Geliefert', max_length=1)  # Field name made lowercase.
    geliefert_anzahl = models.IntegerField(db_column='Geliefert_Anzahl', blank=True, null=True)  # Field name made lowercase.
    investmittel = models.CharField(db_column='Investmittel', max_length=4)  # Field name made lowercase.
    link = models.URLField(db_column='Link', max_length=250, default='')

    class Meta:
        managed = False
        db_table = 'Bestell_Liste'

    def __str__(self):
        return str(self.sap_bestell_nr_field)


class Investmittelplan(models.Model):
    klinik_ou = models.IntegerField(db_column='Klinik_OU', primary_key=True)  # Field name made lowercase.
    investmittel_jahresanfang_in_euro = models.DecimalField(db_column='Investmittel_Jahresanfang_in_Euro', max_digits=8, decimal_places=2)  # Field name made lowercase.
    investmittel_übrig_in_euro = models.DecimalField(db_column='Investmittel_übrig_in_Euro', max_digits=8, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bereich = models.CharField(db_column='Bereich', max_length=40)
    team = models.CharField(db_column='Team', max_length=20)

    class Meta:
        managed = False
        db_table = 'Investmittelplan'


class Lagerliste(models.Model):
    inventarnummer = models.CharField(db_column='Inventarnummer', max_length=20, primary_key=True)  # Field name made lowercase.
    klinik = models.IntegerField(db_column='Klinik', blank=True, null=True)  # Field name made lowercase.
    typ = models.CharField(db_column='Typ', max_length=50)  # Field name made lowercase.
    modell = models.CharField(db_column='Modell', max_length=50)  # Field name made lowercase.
    spezifikation = models.TextField(db_column='Spezifikation', blank=True, null=True)  # Field name made lowercase.
    zuweisung = models.TextField(db_column='Zuweisung', blank=True, null=True)  # Field name made lowercase.
    bestell_nr_field = models.ForeignKey(BestellListe, models.DO_NOTHING, db_column='Bestell_Nr.', to_field="sap_bestell_nr_field")  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    herausgeber = models.ForeignKey(User, models.DO_NOTHING, db_column='Herausgeber', to_field='username', blank=True, null=True)  # Field name made lowercase.
    ausgabe = models.DateTimeField(db_column='Ausgabe', blank=True, null=True)  # Field name made lowercase.
    ausgegeben = models.CharField(db_column='Ausgegeben', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Lagerliste'

    def __str__(self):
        return str(self.bestell_nr_field)
    
class Lagerliste_ohne_Invest(models.Model):
    id = models.IntegerField(db_column='id', primary_key=True)  # Field name made lowercase.
    typ = models.CharField(db_column='Typ', max_length=50)  # Field name made lowercase.
    modell = models.CharField(db_column='Modell', max_length=50)  # Field name made lowercase.
    spezifikation = models.TextField(db_column='Spezifikation', blank=True, null=True)  # Field name made lowercase.
    zuweisung = models.TextField(db_column='Zuweisung', blank=True, null=True)  # Field name made lowercase.
    bestell_nr_field = models.ForeignKey(BestellListe, models.DO_NOTHING, db_column='Bestell_Nr.')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    herausgeber = models.ForeignKey(User, models.DO_NOTHING, db_column='Herausgeber', to_field='username', blank=True, null=True)  # Field name made lowercase.
    ausgabe = models.DateTimeField(db_column='Ausgabe', blank=True, null=True)  # Field name made lowercase.
    ausgegeben = models.CharField(db_column='Ausgegeben', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Lagerliste_ohne_Invest'

    def __str__(self):
        return str(self.bestell_nr_field)
    
class Investmittelplan_Soll(models.Model):
    ou = models.IntegerField(db_column='OU', primary_key=True)  # Field name made lowercase.
    investmittel_gesamt = models.DecimalField(db_column='Investmittel_gesamt', max_digits=9, decimal_places=2)  # Field name made lowercase.
    bereich = models.CharField(db_column='Bereich', max_length=40)
    team = models.CharField(db_column='Team', max_length=20)

    class Meta:
        managed = False
        db_table = 'Investmittelplan_Soll'

    def __str__(self):
        return str(self.ou)
    
class Detail_Investmittelplan_Soll(models.Model):
    id = models.IntegerField(db_column='id', primary_key=True)
    ou_invsoll = models.ForeignKey(Investmittelplan_Soll, models.DO_NOTHING, db_column='OU_InvSoll')
    typ = models.CharField(db_column='Typ', max_length=50)
    modell = models.CharField(db_column='Modell', max_length=50)
    menge = models.IntegerField(db_column='Menge')
    preis_pro_stück = models.DecimalField(db_column='Preis_pro_Stück', max_digits=6, decimal_places=2)
    admin = models.ForeignKey(User, models.DO_NOTHING, db_column='Admin', to_field='username', blank=True, null=True)
    spezifikation = models.TextField(db_column='Spezifikation', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Detail_Investmittelplan_Soll'

    def __str__(self):
        return str(self.ou_invsoll)