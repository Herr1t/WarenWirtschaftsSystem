from django.contrib import admin

from .models import Lagerliste, BestellListe, Investmittelplan, User, TempLagerliste
# Register your models here.

class Bestell_ListeAdmin(admin.ModelAdmin):
    list_display = ("sap_bestell_nr_field", "modell", "typ", "menge", "spezifikation", "inventarnummern_von_bis", "ersteller", "geliefert", "geliefert_anzahl")

class LagerlisteAdmin(admin.ModelAdmin):
    list_display = ("inventarnummer", "klinik", "typ", "modell", "spezifikation", "investmittel", "bestell_nr_field", "herausgeber", "ausgabe", "ausgegeben")

class TempLagerlisteAdmin(admin.ModelAdmin):
    list_display = ("inventarnummer", "klinik", "typ", "modell", "spezifikation", "investmittel", "herausgeber", "ausgabe", "ausgegeben")

class InvestmittelpanAdmin(admin.ModelAdmin):
    list_display = ("klinik_ou", "investmittel_jahresanfang_in_euro", "investmittel_übrig_in_euro")

admin.site.register(Lagerliste, LagerlisteAdmin)
admin.site.register(BestellListe, Bestell_ListeAdmin)
admin.site.register(Investmittelplan, InvestmittelpanAdmin)
admin.site.register(TempLagerliste, TempLagerlisteAdmin)
admin.site.register(User)