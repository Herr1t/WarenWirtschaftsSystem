# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Achievements(models.Model):
    user = models.ForeignKey('WebapplicationUser', models.DO_NOTHING, db_column='User', to_field='username')  # Field name made lowercase.
    bestell_count = models.IntegerField(db_column='Bestell_Count', blank=True, null=True)  # Field name made lowercase.
    bestell_achievement = models.IntegerField(db_column='Bestell_Achievement', blank=True, null=True)  # Field name made lowercase.
    lager_count = models.IntegerField(db_column='Lager_Count', blank=True, null=True)  # Field name made lowercase.
    lager_achievement = models.IntegerField(db_column='Lager_Achievement', blank=True, null=True)  # Field name made lowercase.
    rueckgabe_count = models.IntegerField(db_column='Rueckgabe_Count', blank=True, null=True)  # Field name made lowercase.
    rueckgabe_achievement = models.IntegerField(db_column='Rueckgabe_Achievement', blank=True, null=True)  # Field name made lowercase.
    handout_count = models.IntegerField(db_column='Handout_Count', blank=True, null=True)  # Field name made lowercase.
    handout_achievement = models.IntegerField(db_column='Handout_Achievement', blank=True, null=True)  # Field name made lowercase.
    update_achievement = models.IntegerField(db_column='Update_Achievement', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Achievements'


class BestellListe(models.Model):
    sap_bestell_nr_field = models.CharField(db_column='SAP_Bestell_Nr.', primary_key=True, max_length=20)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    modell = models.CharField(db_column='Modell', max_length=50)  # Field name made lowercase.
    typ = models.CharField(db_column='Typ', max_length=50)  # Field name made lowercase.
    preis_pro_stück = models.DecimalField(db_column='Preis_pro_Stück', max_digits=6, decimal_places=2)  # Field name made lowercase.
    menge = models.PositiveIntegerField(db_column='Menge')  # Field name made lowercase.
    spezifikation = models.TextField(db_column='Spezifikation', blank=True, null=True)  # Field name made lowercase.
    inventarnummern_von_bis = models.TextField(db_column='Inventarnummern Von-Bis', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    ersteller = models.ForeignKey('WebapplicationUser', models.DO_NOTHING, db_column='Ersteller', to_field='username', blank=True, null=True)  # Field name made lowercase.
    geliefert = models.CharField(db_column='Geliefert', max_length=1)  # Field name made lowercase.
    geliefert_anzahl = models.SmallIntegerField(db_column='Geliefert_Anzahl', blank=True, null=True)  # Field name made lowercase.
    investmittel = models.CharField(db_column='Investmittel', max_length=4)  # Field name made lowercase.
    bearbeitet = models.DateTimeField(db_column='Bearbeitet', blank=True, null=True)  # Field name made lowercase.
    zuweisung = models.TextField(db_column='Zuweisung', blank=True, null=True)  # Field name made lowercase.
    link = models.CharField(db_column='Link', max_length=2083, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Bestell_Liste'


class DetailInvestmittelplanSoll(models.Model):
    ou_invsoll = models.ForeignKey('InvestmittelplanSoll', models.DO_NOTHING, db_column='OU_InvSoll')  # Field name made lowercase.
    typ = models.CharField(db_column='Typ', max_length=50)  # Field name made lowercase.
    modell = models.CharField(db_column='Modell', max_length=50)  # Field name made lowercase.
    spezifikation = models.TextField(db_column='Spezifikation', blank=True, null=True)  # Field name made lowercase.
    menge = models.PositiveIntegerField(db_column='Menge')  # Field name made lowercase.
    preis_pro_stück = models.DecimalField(db_column='Preis_pro_Stück', max_digits=8, decimal_places=2)  # Field name made lowercase.
    admin = models.CharField(db_column='Admin', max_length=35, blank=True, null=True)  # Field name made lowercase.
    ou = models.ForeignKey('Ou', models.DO_NOTHING, db_column='OU_id')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Detail_Investmittelplan_Soll'


class Invest(models.Model):
    ou = models.ForeignKey('Ou', models.DO_NOTHING)
    investmittel_übrig = models.DecimalField(max_digits=8, decimal_places=2)
    investmittel_gesamt = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    team = models.CharField(max_length=20, blank=True, null=True)
    bereich = models.CharField(max_length=40, blank=True, null=True)
    jahr = models.IntegerField()
    typ = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'Invest'


class Investmittelplan(models.Model):
    klinik_ou = models.IntegerField(db_column='Klinik_OU', primary_key=True)  # Field name made lowercase.
    investmittel_jahresanfang_in_euro = models.DecimalField(db_column='Investmittel_Jahresanfang_in_Euro', max_digits=10, decimal_places=2)  # Field name made lowercase.
    investmittel_übrig_in_euro = models.DecimalField(db_column='Investmittel_übrig_in_Euro', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bereich = models.CharField(db_column='Bereich', max_length=40, blank=True, null=True)  # Field name made lowercase.
    team = models.CharField(db_column='Team', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Investmittelplan'


class InvestmittelplanSoll(models.Model):
    ou = models.IntegerField(db_column='OU', primary_key=True)  # Field name made lowercase.
    investmittel_gesamt = models.DecimalField(db_column='Investmittel_Gesamt', max_digits=10, decimal_places=2)  # Field name made lowercase.
    bereich = models.CharField(db_column='Bereich', max_length=40, blank=True, null=True)  # Field name made lowercase.
    team = models.CharField(db_column='Team', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Investmittelplan_Soll'


class Lagerliste(models.Model):
    inventarnummer = models.CharField(db_column='Inventarnummer', primary_key=True, max_length=20)  # Field name made lowercase.
    klinik = models.IntegerField(db_column='Klinik', blank=True, null=True)  # Field name made lowercase.
    typ = models.CharField(db_column='Typ', max_length=50)  # Field name made lowercase.
    modell = models.CharField(db_column='Modell', max_length=50)  # Field name made lowercase.
    spezifikation = models.TextField(db_column='Spezifikation', blank=True, null=True)  # Field name made lowercase.
    bestell_nr_field = models.ForeignKey(BestellListe, models.DO_NOTHING, db_column='Bestell_Nr.')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    herausgeber = models.ForeignKey('WebapplicationUser', models.DO_NOTHING, db_column='Herausgeber', to_field='username', blank=True, null=True)  # Field name made lowercase.
    ausgabe = models.DateTimeField(db_column='Ausgabe', blank=True, null=True)  # Field name made lowercase.
    ausgegeben = models.CharField(db_column='Ausgegeben', max_length=1)  # Field name made lowercase.
    zuweisung = models.TextField(db_column='Zuweisung', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Lagerliste'


class LagerlisteOhneInvest(models.Model):
    typ = models.CharField(db_column='Typ', max_length=50)  # Field name made lowercase.
    modell = models.CharField(db_column='Modell', max_length=50)  # Field name made lowercase.
    spezifikation = models.TextField(db_column='Spezifikation', blank=True, null=True)  # Field name made lowercase.
    bestell_nr_field = models.ForeignKey(BestellListe, models.DO_NOTHING, db_column='Bestell_Nr.')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    herausgeber = models.ForeignKey('WebapplicationUser', models.DO_NOTHING, db_column='Herausgeber', to_field='username', blank=True, null=True)  # Field name made lowercase.
    ausgabe = models.DateTimeField(db_column='Ausgabe', blank=True, null=True)  # Field name made lowercase.
    ausgegeben = models.CharField(db_column='Ausgegeben', max_length=1)  # Field name made lowercase.
    zuweisung = models.TextField(db_column='Zuweisung', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Lagerliste_ohne_Invest'


class Ou(models.Model):
    ou_id = models.AutoField(db_column='OU_id', primary_key=True)  # Field name made lowercase.
    ou = models.IntegerField(db_column='OU')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'OU'


class Test(models.Model):
    klinik_ou = models.IntegerField(db_column='Klinik_OU', primary_key=True)  # Field name made lowercase.
    investmittel_jahresanfang_in_euro = models.DecimalField(db_column='Investmittel_Jahresanfang_in_Euro', max_digits=10, decimal_places=2)  # Field name made lowercase.
    investmittel_übrig_in_euro = models.DecimalField(db_column='Investmittel_übrig_in_Euro', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Test'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('WebapplicationUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class WebapplicationDownload(models.Model):
    id = models.BigAutoField(primary_key=True)
    titel = models.CharField(max_length=100)
    dateipfad = models.CharField(max_length=100)
    hochgeladen = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'webapplication_download'


class WebapplicationInvestmittelplanAlt(models.Model):
    id = models.BigAutoField(primary_key=True)
    klinik_ou = models.IntegerField()
    investmittel_jahresanfang_in_euro = models.DecimalField(max_digits=8, decimal_places=2)
    investmittel_übrig_in_euro = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    jahr = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'webapplication_investmittelplan_alt'


class WebapplicationUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'webapplication_user'


class WebapplicationUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(WebapplicationUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'webapplication_user_groups'
        unique_together = (('user', 'group'),)


class WebapplicationUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(WebapplicationUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'webapplication_user_user_permissions'
        unique_together = (('user', 'permission'),)
