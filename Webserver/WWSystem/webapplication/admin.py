from django.contrib import admin

from .models import Lagerliste, BestellListe, Investmittelplan, User, Lagerliste_ohne_Invest
# Register your models here.

class Bestell_ListeAdmin(admin.ModelAdmin):
    list_display = ("sap_bestell_nr_field", "modell", "typ", "menge", "preis_pro_stück", "spezifikation", "investmittel", "bearbeitet", "ersteller", "geliefert", "geliefert_anzahl")

class LagerlisteAdmin(admin.ModelAdmin):
    list_display = ("inventarnummer", "klinik", "typ", "modell", "spezifikation", "bestell_nr_field", "herausgeber", "ausgabe", "ausgegeben")

class Lagerliste_ohne_InvestAdmin(admin.ModelAdmin):
    list_display = ("id", "typ", "modell", "spezifikation", "bestell_nr_field", "herausgeber", "ausgabe", "ausgegeben")

class InvestmittelpanAdmin(admin.ModelAdmin):
    list_display = ("klinik_ou", "investmittel_jahresanfang_in_euro", "investmittel_übrig_in_euro")

admin.site.register(Lagerliste, LagerlisteAdmin)
admin.site.register(Lagerliste_ohne_Invest, Lagerliste_ohne_InvestAdmin)
admin.site.register(BestellListe, Bestell_ListeAdmin)
admin.site.register(Investmittelplan, InvestmittelpanAdmin)
admin.site.register(User)