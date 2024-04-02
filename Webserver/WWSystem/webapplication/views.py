from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from time import sleep

from .models import Lagerliste, BestellListe, Investmittelplan, User, Lagerliste_ohne_Invest

# Create your views here.

def index(request):
    return render(request, "webapplication/login.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("lagerliste"))
        else:
            return render(request, "webapplication/login.html", {
                "message": "Invalid username and/or password.",
                "test": user
            })
    else:
        return render(request, "webapplication/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "webapplication/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, password)
            user.set_password(password)
            user.save()
        except IntegrityError:
            return render(request, "webapplication/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("lagerliste"))
    else:
        return render(request, "webapplication/register.html")

def lager(request):
    Menge =  Lagerliste.objects.values_list('zuweisung', 'inventarnummer')
    y = 0
    for _ in Menge:
        if str(Menge[y][0]) == "None":
            update = Lagerliste.objects.update_or_create(inventarnummer=Menge[y][1], defaults={'zuweisung': "Keine Zuweisung"})
            y = y + 1
        else:
            y = y + 1
    return render(request, "webapplication/lager.html", {
        "lagerliste": Lagerliste.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field"))
    })

def bestell(request):
    Menge =  BestellListe.objects.values_list('geliefert_anzahl', 'sap_bestell_nr_field')
    y = 0
    for _ in Menge:
        if str(Menge[y][0]) == "None":
            update = BestellListe.objects.update_or_create(sap_bestell_nr_field=Menge[y][1], defaults={'geliefert_anzahl': 0})
            y = y + 1
        else:
            y = y + 1
    return render(request, "webapplication/bestell.html", {
        "bestell_liste": BestellListe.objects.all(),
    })

def invest(request):
    investmittelplan = Investmittelplan.objects.all().order_by('klinik_ou')
    page = request.GET.get('page', 1)
    paginator = Paginator(investmittelplan, 50)
    try:
        invest = paginator.page(page)
    except PageNotAnInteger:
        invest = paginator.page(1)
    except EmptyPage:
        invest = paginator.page(paginator.num_pages)
    return render(request, "webapplication/invest.html", {
        "investmittelplan": invest
    })

def create_bestell(request):
    if request.method == "POST":
        bestell_nr = request.POST["sap_bestell_nr"]
        modell = request.POST["modell"]
        typ = request.POST["typ"]
        menge = request.POST["menge"]
        preis_pro_stück = request.POST["preis_pro_stück"]
        spezi = request.POST["spezifikation"]
        zuweisung = request.POST["zuweisung"]
        investmittel = request.POST["investmittel"]
        invnr_von_bis = ""
        geliefert = 0
        geliefert_anzahl = 0
        ersteller = request.user
        bearbeitet = timezone.now()

        if not zuweisung:
            zuweisung = "Keine Zuweisung"
        if int(menge) > 255:
            return render(request, "webapplication/create_bestell.html", {
            "alert": "Menge darf 255 nicht überschreiten"
        })
        if len(str(modell)) > 50:
            return render(request, "webapplication/create_bestell.html", {
            "alert": "Modell darf nicht länger als 50 Zeichen sein"
        })
        if len(str(typ)) > 50:
            return render(request, "webapplication/create_bestell.html", {
            "alert": "Typ darf nicht länger als 50 Zeichen sein"
        })
        if len(str(spezi)) > 255:
            return render(request, "webapplication/create_bestell.html", {
            "alert": "Spezifikation darf nicht länger als 255 Zeichen sein"
        })

        bestellung = BestellListe.objects.create(sap_bestell_nr_field=bestell_nr, modell=modell, typ=typ, menge=menge, preis_pro_stück=preis_pro_stück, spezifikation=spezi, zuweisung=zuweisung, inventarnummern_von_bis=invnr_von_bis, geliefert=geliefert, geliefert_anzahl=geliefert_anzahl, ersteller=ersteller, investmittel=investmittel, bearbeitet=bearbeitet)
        return render(request, "webapplication/create_bestell.html", {
            "message": "Einträge erfolgreich angelegt"
        })
    return render(request, "webapplication/create_bestell.html")

def create_lager(request):
    if request.method == "POST":
        x = int(0)
        y = int(0)
        c = 0
        list = []
        dupe = ""
        fail = ""
        entrys = BestellListe.objects.values_list('sap_bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung')
        try:
            bnr = BestellListe.objects.get(pk=str(request.POST["bestell_nr"]))
        except ValueError:
            return render(request, "webapplication/create_lager.html", {
                "message": "Bitte wähle eine Bestell_Nr. aus",
                "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")
            })

        ausgegeben = 0
        while True:
            check = request.POST.get(f"{x}", False)
            if check:
                list.append(request.POST[f"{x}"])
                x = x + 1
            else:
                x = x + 1
                c = c + 1
                if c == 50:
                    break
        for __ in entrys:
            if str(bnr) in str(entrys[y][0]):
                typ = entrys[y][1]
                modell = entrys[y][2]
                spezifikation = entrys[y][3]
                zuweisung = entrys[y][4]
            else:
                y = y + 1
        for _ in list:
            inventarnummer = _
            try:
                Lagerliste.objects.create(inventarnummer=inventarnummer, typ=typ, modell=modell, spezifikation=spezifikation, zuweisung=zuweisung, bestell_nr_field=bnr, ausgegeben=ausgegeben)
                obj = Lagerliste.objects.get(pk=inventarnummer)
                if obj is None:
                    fail = fail + inventarnummer + ", "
            except IntegrityError:
                dupe = dupe + inventarnummer + ", "
                continue
        if fail:
            fail = fail[:-2]
            return render(request, "webapplication/create_lager.html", {
                "dupe": dupe,
                "fail": fail,
                "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")
            })
        if dupe:
            dupe = dupe[:-2]
            return render(request, "webapplication/create_lager.html", {
                "dupe": dupe,
                "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")
            })
        return render(request, "webapplication/create_lager.html", {
            "message": "Eintrag/Einträge erfolgreich angelegt",
            "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")
        })
    return render(request, "webapplication/create_lager.html", {
        "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")
    })

def handout_lager(request):
    if request.method == "POST":
        x = 0
        c = 0
        list = []
        ausgegeben = 1
        ausgabe = timezone.now
        klinik = request.POST["klinik"]
        herausgeber = request.user
        while True:
            check = request.POST.get(f"{x}", False)
            if check:
                list.append(request.POST[f"{x}"])
                x = x + 1
            else:
                x = x + 1
                c = c + 1
                if c == 50:
                    break
        for _ in list:
            inventarnummer = str(_)
            ausgabe_check = str(Lagerliste.objects.values_list('ausgegeben').filter(inventarnummer=inventarnummer)).replace(',', '')
            try:
                if ausgabe_check[13] in "0":
                    _ = Lagerliste.objects.values_list('bestell_nr_field').filter(inventarnummer=inventarnummer)
                    temp = BestellListe.objects.values_list('preis_pro_stück').filter(sap_bestell_nr_field=str(_[0]).replace("'", "").replace("(", "").replace(")", ""). replace(",", ""))
                    try:
                        __ = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').filter(klinik_ou=klinik)
                        abzug = float(str(__[0]).replace(',', '').replace('(', '').replace(')', '').replace("Decimal'", "").replace("'", "")) - float(str(temp[0]).replace('(', '').replace(')', ''). replace("Decimal", "").replace("'", "").replace(',', ''))
                    except ValueError:
                        return render(request, "webapplication/handout_lager.html", {
                            "alert": "Diese Klinik besitzt keine hinterlegten Investmittel!"
                        })
                    ausgeben = Lagerliste.objects.update_or_create(inventarnummer=inventarnummer, defaults={'ausgegeben': ausgegeben, 'klinik': klinik, 'ausgabe': ausgabe, 'herausgeber': herausgeber})
                    abrechnung = Investmittelplan.objects.update_or_create(klinik_ou=klinik, defaults={'investmittel_übrig_in_euro': abzug})
                else:
                    return render(request, "webapplication/handout_lager.html", {
                        "alert": "Gerät bereits ausgetragen"
                    })
            except IndexError:
                return render(request, "webapplication/handout_lager.html", {
                    "alert": "Inventarnummer im Lager nicht hinterlegt"
                })
        check = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').get(klinik_ou=klinik)
        if float(check[0]) < 0:
                return render(request, "webapplication/handout_lager.html", {
                "message": "Einträge erfolgreich ausgetragen",
                "alarm": klinik,
                "geld": float(check[0])
            })
        else:
            return render(request, "webapplication/handout_lager.html", {
                "message": "Einträge erfolgreich ausgetragen"
            })
    return render(request, "webapplication/handout_lager.html")

def detail_lager(request, bestell_nr):
    nr = bestell_nr
    bestell = Lagerliste.objects.filter(bestell_nr_field=nr)
    return render(request, "webapplication/detail_lager.html", {
        "detail_lagerliste": bestell,
        "bestell_nr": bestell_nr
    })

def profile(request, user_id):
    user_name = User.objects.values_list('username').get(pk=user_id)
    username = user_name[0]
    return render(request, "webapplication/profile.html", {
        "user_id": user_id,
        "bestell_liste": BestellListe.objects.all(),
        "user_name": request.user,
        "username": username,
        "lagerliste": Lagerliste.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung', 'herausgeber', 'ausgabe').exclude(ausgegeben="0").annotate(Menge=Count("bestell_nr_field"))
    })

def detail_lager_profile(request, user_id, bestell_nr):
    user_name = User.objects.values_list('username').get(pk=user_id)
    username = user_name[0]
    return render(request, "webapplication/detail_lager_profile.html", {
        "user_id": user_id,
        "user_name": username,
        "bestellung": bestell_nr,
        "lagerliste": Lagerliste.objects.all().values('inventarnummer', 'typ', 'modell', 'spezifikation', 'zuweisung', 'herausgeber', 'ausgabe', 'klinik', 'bestell_nr_field').exclude(ausgegeben="0").filter(bestell_nr_field=bestell_nr)
    })

def update(request, bestell_nr):
    nr = bestell_nr
    if request.method == "POST":
        items = BestellListe.objects.values_list('sap_bestell_nr_field', 'modell', 'typ', 'menge', 'preis_pro_stück', 'spezifikation', 'geliefert_anzahl', 'zuweisung').get(pk=nr)
        sap_bestell_nr_field = request.POST["sap_bestell_nr_field"] or items[0]
        modell = request.POST["modell"] or items[1]
        typ = request.POST["typ"] or items[2]
        menge = request.POST["menge"] or items[3]
        preis_pro_stück = request.POST["preis_pro_stück"] or items[4]
        spezi = request.POST["spezifikation"] or items[5]
        geliefert_anzahl = request.POST["geliefert_anzahl"] or items[6]
        zuweisung = request.POST["zuweisung"] or items[7]
        geliefert = 1
        anzahl = int(BestellListe.objects.values_list('geliefert_anzahl').get(pk=bestell_nr)[0])

        if menge:
            if int(menge) > 255:
                return render(request, "webapplication/update_bestell.html", {
                "alert": "Menge darf nicht 255 überschreiten",
                "bestell_nr": bestell_nr,
                "bestell_liste": BestellListe.objects.all().filter(sap_bestell_nr_field=nr)
            })
        if modell:
            if len(str(modell)) > 50:
                return render(request, "webapplication/update_bestell.html", {
                "alert": "Modell darf nicht länger als 50 Zeichen sein",
                "bestell_nr": bestell_nr,
                "bestell_liste": BestellListe.objects.all().filter(sap_bestell_nr_field=nr)
            })
        if typ:
            if len(str(typ)) > 50:
                return render(request, "webapplication/update_bestell.html", {
                "alert": "Typ darf nicht länger als 50 Zeichen sein",
                "bestell_nr": bestell_nr,
                "bestell_liste": BestellListe.objects.all().filter(sap_bestell_nr_field=nr)
            })
        if spezi:
            if len(str(spezi)) > 255:
                return render(request, "webapplication/update_bestell.html", {
                "alert": "Spezifikation darf nicht länger als 255 Zeichen sein",
                "bestell_nr": bestell_nr,
                "bestell_liste": BestellListe.objects.all().filter(sap_bestell_nr_field=nr)
            })
        
        bestellung = BestellListe.objects.filter(sap_bestell_nr_field=bestell_nr).update(sap_bestell_nr_field = sap_bestell_nr_field, modell = modell, typ = typ, menge = menge, preis_pro_stück = preis_pro_stück, spezifikation = spezi, zuweisung = zuweisung, geliefert_anzahl = geliefert_anzahl, bearbeitet = timezone.now())
        bnr = BestellListe.objects.get(pk=sap_bestell_nr_field)
        if geliefert_anzahl:
            if int(geliefert_anzahl) == int(menge) :
                bestellung = BestellListe.objects.update_or_create(sap_bestell_nr_field=sap_bestell_nr_field, defaults={'geliefert': geliefert})
            if str(BestellListe.objects.values_list('investmittel').filter(sap_bestell_nr_field=sap_bestell_nr_field))[13:17] in "Nein":
                if int(geliefert_anzahl) > anzahl:
                    y = "test"
                    i = anzahl
                    while i < int(geliefert_anzahl):
                        Lagerliste_ohne_Invest.objects.create(typ=typ, modell=modell, spezifikation=spezi, bestell_nr_field=bnr, zuweisung=zuweisung, ausgegeben=0)
                        i = i + 1
        if str(bnr) != str(nr) or int(geliefert_anzahl) == int(menge):
            return render(request, "webapplication/bestell.html", {
                "bestell_liste": BestellListe.objects.all()
            })
        return render(request, "webapplication/update_bestell.html", {
            "message": "Einträge erflogreich aktualisiert",
            "bestell_nr": bestell_nr,
            "bestell_liste": BestellListe.objects.all().filter(sap_bestell_nr_field=nr)
        })
    return render(request, "webapplication/update_bestell.html", {
        "bestell_nr": bestell_nr,
        "bestell_liste": BestellListe.objects.all().filter(sap_bestell_nr_field=nr)
    })

def lager_ohne_invest(request):
    Menge =  Lagerliste_ohne_Invest.objects.values_list('zuweisung', 'id')
    y = 0
    for _ in Menge:
        if str(Menge[y][0]) == "None":
            update = Lagerliste_ohne_Invest.objects.update_or_create(id=Menge[y][1], defaults={'zuweisung': "Keine Zuweisung"})
            y = y + 1
        else:
            y = y + 1
    return render(request, "webapplication/lager_ohne_invest.html", {
        "lagerliste": Lagerliste_ohne_Invest.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field"))
    })

def profile_lager_ohne(request, user_id):
    user_name = User.objects.values_list('username').get(pk=user_id)
    username = user_name[0]
    return render(request, "webapplication/profile_lager_ohne.html", {
        "user_id": user_id,
        "username": username,
        "lagerliste": Lagerliste_ohne_Invest.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'herausgeber', 'ausgabe').exclude(ausgegeben="0").annotate(Menge=Count("bestell_nr_field"))
    })

def handout_lager_ohne(request, bestell_nr):
    nr = bestell_nr
    if request.method == "POST":
        list =[]
        ausgabe_menge = request.POST["menge"]
        ausgegeben = 1
        herausgeber = request.user
        ausgabe = timezone.now
        i = 0
        x = 0
        id = Lagerliste_ohne_Invest.objects.values_list('id').filter(bestell_nr_field=bestell_nr).exclude(ausgegeben="1")
        __ = Lagerliste_ohne_Invest.objects.values_list('bestell_nr_field').filter(bestell_nr_field=bestell_nr).exclude(ausgegeben="1")
        try:
            while True:
                list.append(str(Lagerliste_ohne_Invest.objects.values_list('bestell_nr_field').filter(bestell_nr_field=bestell_nr).exclude(ausgegeben="1")[x]).replace(',', ''). replace("(", "").replace(")", ""))
                x = x + 1
        except:
            pass
        if int(ausgabe_menge) > len(list):
            return render(request, "webapplication/handout_lager_ohne.html", {
                "alert": "Menge zu hoch",
                "lagerliste": Lagerliste_ohne_Invest.objects.filter(bestell_nr_field=bestell_nr).values('bestell_nr_field', 'typ', 'modell', 'spezifikation').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field")),
                "bestell_nr": nr
            })
        while i < int(ausgabe_menge):
            Lagerliste_ohne_Invest.objects.filter(bestell_nr_field=bestell_nr).update_or_create(id=int(str((id)[0]).replace(',', ''). replace("(", "").replace(")", "")), defaults={'ausgegeben': ausgegeben, 'herausgeber': herausgeber, 'ausgabe': ausgabe})
            i = i + 1
        if Lagerliste_ohne_Invest.objects.filter(bestell_nr_field=bestell_nr).exclude(ausgegeben="1"):
            return render(request, "webapplication/handout_lager_ohne.html", {
                "message": "Einträge erfolgreich ausgetragen",
                "lagerliste": Lagerliste_ohne_Invest.objects.filter(bestell_nr_field=bestell_nr).values('bestell_nr_field', 'typ', 'modell', 'spezifikation').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field")),
                "bestell_nr": nr
            })
        else:
            Menge =  BestellListe.objects.values_list('geliefert_anzahl')
            return render(request, "webapplication/lager_ohne_invest.html", {
                "lagerliste": Lagerliste_ohne_Invest.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field")),
            })
    return render(request, "webapplication/handout_lager_ohne.html", {
        "lagerliste": Lagerliste_ohne_Invest.objects.filter(bestell_nr_field=bestell_nr).values('bestell_nr_field', 'typ', 'modell', 'spezifikation').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field")),
        "bestell_nr": nr
    })

def detail_profile_lager_ohne(request, user_id, bestell_nr):
    user_name = User.objects.values_list('username').get(pk=user_id)
    username = user_name[0]
    return render(request, "webapplication/detail_profile_lager_ohne.html", {
        "user_id": user_id,
        "user_name": username,
        "bestellung": bestell_nr,
        "lagerliste": Lagerliste_ohne_Invest.objects.all().values('id', 'typ', 'modell', 'spezifikation', 'herausgeber', 'ausgabe', 'bestell_nr_field').exclude(ausgegeben="0").filter(bestell_nr_field=bestell_nr)
    })

def rückgabe(request):
    if request.method == 'POST':
        x = 0
        list = []
        ausgegeben = 0
        ausgabe = ""
        herausgeber = User.objects.get(pk=1)
        try:
            while True:
                list.append(request.POST[f"{x}"])
                x = x + 1
        except:
            pass
        for _ in list:
            inventarnummer = str(_)
            klinik_ou = Lagerliste.objects.values_list('klinik').get(pk=inventarnummer)[0]
            ausgabe_check = str(Lagerliste.objects.values_list('ausgegeben').filter(inventarnummer=inventarnummer)).replace(',', '')
            if ausgabe_check[13] in "1":
                _ = Lagerliste.objects.values_list('bestell_nr_field').filter(inventarnummer=inventarnummer)
                temp = BestellListe.objects.values_list('preis_pro_stück').filter(sap_bestell_nr_field=str(_[0]).replace("'", "").replace("(", "").replace(")", ""). replace(",", ""))
                try:
                    __ = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').filter(klinik_ou=klinik_ou)
                    abzug = float(str(__[0]).replace(',', '').replace('(', '').replace(')', '').replace("Decimal'", "").replace("'", "")) + float(str(temp[0]).replace('(', '').replace(')', ''). replace("Decimal", "").replace("'", "").replace(',', ''))
                except ValueError:
                    return render(request, "webapplication/handout_lager.html", {
                        "alert": "Diese Klinik besitzt keine hinterlegten Investmittel!"
                    })
                ausgeben = Lagerliste.objects.update_or_create(inventarnummer=inventarnummer, defaults={'ausgegeben': ausgegeben})
                ausgeben2 = Lagerliste.objects.filter(inventarnummer=inventarnummer).update(herausgeber=None, klinik=None, ausgabe=None)
                abrechnung = Investmittelplan.objects.update_or_create(klinik_ou=klinik_ou, defaults={'investmittel_übrig_in_euro': abzug})
            else:
                return render(request, "webapplication/handout_lager.html", {
                    "alert": "Gerät bereits im Lager"
                })
        return render(request, "webapplication/rückgabe.html", {
            "message": "Geräte erfolgreich zurückgegeben"
        }) 
    return render(request, "webapplication/rückgabe.html")

def löschen(request, bestell_nr):
    if request.method == 'POST':
        answer = request.POST["confirm"]
        if answer in "yes":
            Lagerliste.objects.filter(bestell_nr_field=bestell_nr).delete()
            BestellListe.objects.update_or_create(sap_bestell_nr_field=bestell_nr, defaults={'geliefert': 0, 'geliefert_anzahl': 0})
            return HttpResponseRedirect(reverse('lagerliste'))
        else:
            return HttpResponseRedirect(reverse('detail_lager', args=[bestell_nr]))
    return render(request, "webapplication/löschen.html", {
        "bestell_nr": bestell_nr
    })