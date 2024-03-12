from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count

from .models import Lagerliste, BestellListe, Investmittelplan, User

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
    Menge =  BestellListe.objects.values_list('geliefert_anzahl')
    return render(request, "webapplication/lager.html", {
        "lagerliste": Lagerliste.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field"))
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
        "bestell_liste": BestellListe.objects.all()
    })

def invest(request):
    return render(request, "webapplication/invest.html", {
        "investmittelplan": Investmittelplan.objects.all().order_by('klinik_ou')
    })

def create_bestell(request):
    if request.method == "POST":
        bestell_nr = request.POST["sap_bestell_nr"]
        modell = request.POST["modell"]
        typ = request.POST["typ"]
        menge = request.POST["menge"]
        preis_pro_stück = request.POST["preis_pro_stück"]
        spezi = request.POST["spezifikation"]
        invnr_von_bis = request.POST["inventarnummern_von_bis"]
        geliefert = 0
        geliefert_anzahl = 0
        ersteller = request.user

        if int(menge) > 255:
            return render(request, "webapplication/create_bestell.html", {
            "message": "Menge darf nicht 255 überschreiten"
        })
        if len(str(modell)) > 20:
            return render(request, "webapplication/create_bestell.html", {
            "message": "Modell darf nicht länger als 20 Zeichen sein"
        })
        if len(str(typ)) > 20:
            return render(request, "webapplication/create_bestell.html", {
            "message": "Typ darf nicht länger als 20 Zeichen sein"
        })
        if len(str(spezi)) > 255:
            return render(request, "webapplication/create_bestell.html", {
            "message": "Spezifikation darf nicht länger als 255 Zeichen sein"
        })
        if len(str(invnr_von_bis)) > 255:
            return render(request, "webapplication/create_bestell.html", {
            "message": "Inventarnummer Von-Bis darf nicht länger als 255 Zeichen sein"
        })

        bestellung = BestellListe.objects.create(sap_bestell_nr_field=bestell_nr, modell=modell, typ=typ, menge=menge, preis_pro_stück=preis_pro_stück, spezifikation=spezi, inventarnummern_von_bis=invnr_von_bis, geliefert=geliefert, geliefert_anzahl=geliefert_anzahl, ersteller=ersteller)
        bestellung.save()
        return render(request, "webapplication/create_bestell.html", {
            "message": "Eintrag erfolgreich angelegt!"
        })
    return render(request, "webapplication/create_bestell.html")

def create_lager(request):
    if request.method == "POST":
        x = 0
        y = 0
        list = []
        entrys = BestellListe.objects.values_list('sap_bestell_nr_field', 'typ', 'modell', 'spezifikation')
        try:
            bnr = BestellListe.objects.get(pk=int(request.POST["bestell_nr"]))
        except ValueError:
            return render(request, "webapplication/create_lager.html", {
                "message": "Bitte wähle eine Bestell_Nr. aus"
            })

        ausgegeben = 0
        investmittel = 'N.A.'
        try:
            while True:
                list.append(request.POST[f"{x}"])
                x = x + 1
        except:
            pass
        for __ in entrys:
            if str(bnr) in str(entrys[y][0]):
                typ = entrys[y][1]
                modell = entrys[y][2]
                spezifikation = entrys[y][3]
            else:
                y = y + 1
        for _ in list:
            inventarnummer = int(_)
            try:
                lagerung = Lagerliste.objects.create(inventarnummer=inventarnummer, typ=typ, modell=modell, spezifikation=spezifikation, bestell_nr_field=bnr, ausgegeben=ausgegeben, investmittel=investmittel)
                lagerung.save()
            except IntegrityError:
                return render(request, "webapplication/create_lager.html", {
                    "message": "Inventarnummer bereits eingetragen"
            })
            except ValueError:
                return render(request, "webapplicaiton/create_lager.html", {
                    "message": "Inventarnummer bitte im Bereich von 0 - 2147483647 eintragen"
                })
        return render(request, "webapplication/create_lager.html", {
            "message": "Eintrag/Einträge erfolgreich angelegt"
        })
    return render(request, "webapplication/create_lager.html", {
        "bestell_nr": BestellListe.objects.all().exclude(geliefert="1")
    })

def handout_lager(request):
    if request.method == "POST":
        val = ["Ja", "Nein"]
        x = 0
        list = []
        ausgegeben = 1
        ausgabe = timezone.now
        investmittel = request.POST["investmittel"]
        klinik = request.POST["klinik"]
        herausgeber = request.user
        if str(investmittel) not in val:
            return render(request, "webapplication/handout_lager.html", {
            "message": "Investmittel muss als Eintrag 'Ja' oder 'Nein' beinhalten"
        })
        try:
            while True:
                list.append(request.POST[f"{x}"])
                x = x + 1
        except:
            pass
        for _ in list:
            inventarnummer = int(_)
            ausgeben = Lagerliste.objects.update_or_create(inventarnummer=inventarnummer, defaults={'ausgegeben': ausgegeben, 'investmittel': investmittel, 'klinik': klinik, 'ausgabe': ausgabe, 'herausgeber': herausgeber})
            _ = Lagerliste.objects.values_list('bestell_nr_field').filter(inventarnummer=inventarnummer)
            temp = BestellListe.objects.values_list('preis_pro_stück').filter(sap_bestell_nr_field=_[0])
            __ = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').filter(klinik_ou=klinik)
            abzug = int(__[0]) - int(temp[0])
            abrechnung = Investmittelplan.objects.update_or_create(klinik_ou=klinik, defaults={'investmittel_übrig_in_euro': abzug})
        check = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').filter(klinik_ou=klinik)
        if int(check[0]) < 0:
                return render(request, "webapplication/handout_lager.html", {
                "message": "Einträge erfolgreich ausgetragen",
                "alarm": check
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
        "lagerliste": Lagerliste.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'herausgeber', 'ausgabe').exclude(ausgegeben="0").annotate(Menge=Count("bestell_nr_field"))
    })

def detail_lager_profile(request, user_id, bestell_nr):
    user_name = User.objects.values_list('username').get(pk=user_id)
    username = user_name[0]
    return render(request, "webapplication/detail_lager_profile.html", {
        "user_id": user_id,
        "user_name": username,
        "bestellung": bestell_nr,
        "lagerliste": Lagerliste.objects.all().values('inventarnummer', 'typ', 'modell', 'spezifikation', 'herausgeber', 'ausgabe', 'klinik', 'bestell_nr_field').exclude(ausgegeben="0").filter(bestell_nr_field=bestell_nr)
    })