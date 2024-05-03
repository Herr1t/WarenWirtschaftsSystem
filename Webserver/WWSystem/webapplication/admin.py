from django.contrib import admin

from .models import Lagerliste, BestellListe, Investmittelplan, User, Lagerliste_ohne_Invest
# Register your models here.

class Bestell_ListeAdmin(admin.ModelAdmin):
    list_display = ("sap_bestell_nr_field", "modell", "typ", "menge", "preis_pro_stück", "spezifikation", "zuweisung", "link", "investmittel", "bearbeitet", "ersteller", "geliefert", "geliefert_anzahl")
    list_filter = ("ersteller", "investmittel")
    search_fields = ("sap_bestell_nr_field", "typ")

class LagerlisteAdmin(admin.ModelAdmin):
    list_display = ("inventarnummer", "klinik", "typ", "modell", "spezifikation", "zuweisung", "bestell_nr_field", "herausgeber", "ausgabe", "ausgegeben")
    list_filter = ("herausgeber", )
    search_fields = ("inventarnummer", "bestell_nr_field__sap_bestell_nr_field")

class Lagerliste_ohne_InvestAdmin(admin.ModelAdmin):
    list_display = ("id", "typ", "modell", "spezifikation", "bestell_nr_field", "herausgeber", "ausgabe", "ausgegeben")
    list_filter = ("herausgeber", )
    search_fields = ("bestell_nr_field__sap_bestell_nr_field", "typ")

class InvestmittelpanAdmin(admin.ModelAdmin):
    list_display = ("klinik_ou", "investmittel_jahresanfang_in_euro", "investmittel_übrig_in_euro")
    search_fields = ("klinik_ou", )

admin.site.register(Lagerliste, LagerlisteAdmin)
admin.site.register(Lagerliste_ohne_Invest, Lagerliste_ohne_InvestAdmin)
admin.site.register(BestellListe, Bestell_ListeAdmin)
admin.site.register(Investmittelplan, InvestmittelpanAdmin)
admin.site.register(User)