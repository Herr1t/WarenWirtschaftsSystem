from django.contrib import admin

from .models import Lagerliste, BestellListe, Investmittelplan, User, Lagerliste_ohne_Invest, Detail_Investmittelplan_Soll, Investmittelplan_Soll, Achievements, Download, Investmittelplan_Alt, Invest
# Register your models here.

class Achievements_SollAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "bestell_count", "bestell_achievement", "lager_count", "lager_achievement", "rueckgabe_count", "rueckgabe_achievement", "handout_count", "handout_achievement", "update_achievement")
    list_filter = ("user", )
    search_fields = ("user", "id")

class Investmittelplan_SollAdmin(admin.ModelAdmin):
    list_display = ("ou", "investmittel_gesamt", "bereich", "team")
    list_filter = ("team", )
    search_fields = ("ou", "bereich")

class Detail_Investmittelplan_SollAdmin(admin.ModelAdmin):
    list_display = ("id", "ou_id", "typ", "modell", "menge", "preis_pro_stück", "admin", "spezifikation")
    list_filter = ("typ", "modell")
    search_fields = ("id", )

class Bestell_ListeAdmin(admin.ModelAdmin):
    list_display = ("sap_bestell_nr_field", "modell", "typ", "menge", "preis_pro_stück", "spezifikation", "zuweisung", "link", "investmittel", "bearbeitet", "ersteller", "geliefert", "geliefert_anzahl")
    list_filter = ("ersteller", "investmittel")
    search_fields = ("sap_bestell_nr_field", "typ")

class LagerlisteAdmin(admin.ModelAdmin):
    list_display = ("inventarnummer", "klinik", "typ", "modell", "spezifikation", "zuweisung", "bestell_nr_field", "herausgeber", "ausgabe", "ausgegeben")
    list_filter = ("herausgeber", "klinik")
    search_fields = ("inventarnummer", "bestell_nr_field__sap_bestell_nr_field")

class Lagerliste_ohne_InvestAdmin(admin.ModelAdmin):
    list_display = ("id", "typ", "modell", "spezifikation", "bestell_nr_field", "herausgeber", "ausgabe", "ausgegeben")
    list_filter = ("herausgeber", )
    search_fields = ("bestell_nr_field__sap_bestell_nr_field", "typ")

class InvestmittelpanAdmin(admin.ModelAdmin):
    list_display = ("klinik_ou", "investmittel_jahresanfang_in_euro", "investmittel_übrig_in_euro")
    search_fields = ("klinik_ou", )
    
class InvestAdmin(admin.ModelAdmin):
    list_display = ("ou_id", "investmittel_übrig", "investmittel_gesamt", "jahr", "typ")
    search_fields = ("ou_id", "jahr", "typ")

class Investmittelpan_AltAdmin(admin.ModelAdmin):
    list_display = ("klinik_ou", "investmittel_jahresanfang_in_euro", "investmittel_übrig_in_euro", "jahr")
    search_fields = ("klinik_ou", )

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "is_staff")

admin.site.register(Lagerliste, LagerlisteAdmin)
admin.site.register(Lagerliste_ohne_Invest, Lagerliste_ohne_InvestAdmin)
admin.site.register(BestellListe, Bestell_ListeAdmin)
admin.site.register(Investmittelplan, InvestmittelpanAdmin)
admin.site.register(Invest, InvestAdmin)
admin.site.register(Investmittelplan_Soll, Investmittelplan_SollAdmin)
admin.site.register(Detail_Investmittelplan_Soll, Detail_Investmittelplan_SollAdmin)
admin.site.register(Achievements, Achievements_SollAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Download)
admin.site.register(Investmittelplan_Alt, Investmittelpan_AltAdmin)