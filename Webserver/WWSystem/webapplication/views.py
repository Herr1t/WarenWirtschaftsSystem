from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.exceptions import ObjectDoesNotExist

from .models import Lagerliste, BestellListe, Investmittelplan, User, Lagerliste_ohne_Invest

# View Function if nothing of the below is loaded
def index(request):
    return render(request, "webapplication/login.html")

# View Function that processes the login of users
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

# View Function that processes the logout of users
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# View Function that handles the registering and creation of new users in User
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

# View Function that represents the content of the Lagerliste
def lager(request):
    Menge =  Lagerliste.objects.values_list('zuweisung', 'inventarnummer')
    y = 0
    # Set Column "Zuweisung" to "Keine Zuweisung" if Column is "None"
    for _ in Menge:
        if str(Menge[y][0]) == "None":
            update = Lagerliste.objects.update_or_create(inventarnummer=Menge[y][1], defaults={'zuweisung': "Keine Zuweisung"})
            y = y + 1
        else:
            y = y + 1
    return render(request, "webapplication/lager.html", {
        "lagerliste": Lagerliste.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field"))
    })

# View Function that represents the detailed list of items for a specific Bestell_Nr. inside the Lagerliste
def detail_lager(request, bestell_nr):
    nr = bestell_nr
    bestell = Lagerliste.objects.filter(bestell_nr_field=nr)
    return render(request, "webapplication/detail_lager.html", {
        "detail_lagerliste": bestell,
        "bestell_nr": bestell_nr
    })

# View Function that handles the creation of new entries for the Lagerliste
def create_lager(request):
    if request.method == "POST":
        x = int(0)
        y = int(0)
        c = 0
        list = []
        dupe = ""
        fail = ""
        entrys = BestellListe.objects.values_list('sap_bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung')
        # Checks if a Bestell_Nr. was selected
        try:
            bnr = BestellListe.objects.get(pk=str(request.POST["bestell_nr"]))
        except ValueError:
            return render(request, "webapplication/create_lager.html", {
                "message": "Bitte wähle eine Bestell_Nr. aus",
                "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")
            })

        ausgegeben = 0
        # Appends all entries in the obejct "list"
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
        # Assigning the values to their respective variable
        for __ in entrys:
            if str(bnr) in str(entrys[y][0]):
                typ = entrys[y][1]
                modell = entrys[y][2]
                spezifikation = entrys[y][3]
                zuweisung = entrys[y][4]
            else:
                y = y + 1
        # Creating the new entries in "list" for Lagerliste
        for _ in list:
            inventarnummer = _
            try:
                Lagerliste.objects.create(inventarnummer=inventarnummer, typ=typ, modell=modell, spezifikation=spezifikation, zuweisung=zuweisung, bestell_nr_field=bnr, ausgegeben=ausgegeben)
                obj = Lagerliste.objects.get(pk=inventarnummer)
                # Checking if creation of entry was succesfull
                if obj is None:
                    fail = fail + inventarnummer + ", "
            # Checking if entry already exists
            except IntegrityError:
                dupe = dupe + inventarnummer + ", "
                continue
        # Output if creation of at least one entry failed
        if fail:
            fail = fail[:-2]
            return render(request, "webapplication/create_lager.html", {
                "dupe": dupe,
                "fail": fail,
                "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")
            })
        # Output if at least one of the entries already existed
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

# View Function that handles the "austragung" of entries from the Lagerliste
def handout_lager(request):
    if request.method == "POST":
        x = 0
        c = 0
        list = []
        ausgegeben = 1
        ausgabe = timezone.now
        klinik = request.POST["klinik"]
        herausgeber = request.user
        dne = ""
        fail = ""
        # Appends all entries in the obejct "list"
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
        # "Austragung" of the entries in "list"
        for _ in list:
            inventarnummer = str(_)
            try:
                ausgabe_check = str(Lagerliste.objects.values_list('ausgegeben').get(pk=inventarnummer))
                # Checks if entry isnt already "ausgegeben"
                if ausgabe_check[0] in "('0',)":
                    ___ = Lagerliste.objects.values_list('bestell_nr_field').get(pk=inventarnummer)
                    temp = BestellListe.objects.values_list('preis_pro_stück').get(pk=___[0])
                    __ = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').get(pk=klinik)
                    # Subtracting the "preis_pro_stück" of the entries in "list" from the column "investmittel_übrig_in_euro" of the selected "ou" in Investmittelplan
                    abzug = __[0] - temp[0]
                    abrechnung = Investmittelplan.objects.update_or_create(klinik_ou=klinik, defaults={'investmittel_übrig_in_euro': abzug})
                    # "Austragung" of the entries in Lagerliste
                    ausgeben = Lagerliste.objects.update_or_create(inventarnummer=inventarnummer, defaults={'ausgegeben': ausgegeben, 'klinik': klinik, 'ausgabe': ausgabe, 'herausgeber': herausgeber})
                # Output if entry is already "ausgetragen"
                else:
                    fail = fail + inventarnummer + ", "
                    continue 
            # If entry does not exist in Lagerliste then it gets appended to the variable "dne"
            except ObjectDoesNotExist:
                dne = dne + inventarnummer + ", "
                continue
        # If there is at least one entry in "fail" then is uses this output
        if fail:
            fail = fail[:-2]
            return render(request, "webapplication/handout_lager.html", {
                "dne": dne,
                "fail": fail
            })
        # If there is at least one entry in "dne" then it uses this output
        if dne:
            dne = dne[:-2]
            return render(request, "webapplication/handout_lager.html", {
                "dne": dne
            })
        # Checks if column "investmittel_übrig_in_euro" from Investmittelplan is below 0
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

# View Function that handles the "Rückgabe" of already "ausgegebenen" entries in Lagerliste
def rückgabe(request):
    if request.method == 'POST':
        x = 0
        c = 0
        list = []
        ausgegeben = 0
        ausgabe = ""
        herausgeber = User.objects.get(pk=1)
        fail = ""
        dne = ""
        # Appends all entries in the obejct "list"
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
        # "Rückgabe" of the entries in "list"
        for _ in list:
            inventarnummer = str(_)
            try:
                klinik_ou = Lagerliste.objects.values_list('klinik').get(pk=inventarnummer)[0]
                ausgabe_check = str(Lagerliste.objects.values_list('ausgegeben').get(pk=inventarnummer))
                # Checks if entry isnt already "zurückgegeben"
                if ausgabe_check[0] in "('1',)":
                    _ = Lagerliste.objects.values_list('bestell_nr_field').get(pk=inventarnummer)
                    temp = BestellListe.objects.values_list('preis_pro_stück').get(pk=_[0])
                    __ = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').get(pk=klinik_ou)
                    # Adding the "preis_pro_stück" of the entries in "list" to the column "investmittel_übrig_in_euro" of the previously selected "ou" in Investmittelplan
                    abzug = __[0] + temp[0]
                    abrechnung = Investmittelplan.objects.update_or_create(klinik_ou=klinik_ou, defaults={'investmittel_übrig_in_euro': abzug})
                    # Updating the information of the "zurückgegebenen" entries in Lagerliste
                    ausgeben = Lagerliste.objects.update_or_create(inventarnummer=inventarnummer, defaults={'ausgegeben': ausgegeben})
                    ausgeben2 = Lagerliste.objects.filter(inventarnummer=inventarnummer).update(herausgeber=None, klinik=None, ausgabe=None)
                # Output if entry is already "zurückgegeben"
                else:
                    fail = fail + inventarnummer + ", "
                    continue
            # If entry does not exist in Lagerliste then it gets appended to the variable "dne"
            except ObjectDoesNotExist:
                dne = dne + inventarnummer + ", "
                continue
        # Output if there is at least one entry in fail then it uses this output
        if fail:
            fail = fail[:-2]
            return render(request, "webapplication/rückgabe.html", {
                "fail": fail,
                "dne": dne
            })
        # If there is at least one entry in "dne" then it uses this output
        if dne:
            dne = dne[:-2]
            return render(request, "webapplication/rückgabe.html", {
                "dne": dne
            })
        return render(request, "webapplication/rückgabe.html", {
            "message": "Geräte erfolgreich zurückgegeben"
        }) 
    return render(request, "webapplication/rückgabe.html")

# View Function that proscesses the deletion of all entries with a specific Bestell_Nr. in Lagerliste
def löschen_lager(request, bestell_nr):
    if request.method == 'POST':
        # Double checking if the user really wants to delete the selected entries
        answer = request.POST["confirm"]
        # Deletion of entries if selected "yes"
        if answer in "yes":
            Lagerliste.objects.filter(bestell_nr_field=bestell_nr).delete()
            BestellListe.objects.update_or_create(sap_bestell_nr_field=bestell_nr, defaults={'geliefert': 0, 'geliefert_anzahl': 0})
            return HttpResponseRedirect(reverse('lagerliste'))
        # Cancelation of deletion if "no" is selected
        else:
            return HttpResponseRedirect(reverse('detail_lager', args=[bestell_nr]))
    return render(request, "webapplication/löschen_lager.html", {
        "bestell_nr": bestell_nr
    })

# View Function that represents the content of Lagerliste_ohne_Invest
def lager_ohne_invest(request):
    Menge =  Lagerliste_ohne_Invest.objects.values_list('zuweisung', 'id')
    y = 0
    # Set column "Zuweisung" to "Keine Zuweisung" if column is "None"
    for _ in Menge:
        if str(Menge[y][0]) == "None":
            update = Lagerliste_ohne_Invest.objects.update_or_create(id=Menge[y][1], defaults={'zuweisung': "Keine Zuweisung"})
            y = y + 1
        else:
            y = y + 1
    return render(request, "webapplication/lager_ohne_invest.html", {
        "lagerliste": Lagerliste_ohne_Invest.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field"))
    })

# View Function that handles the "austragung" from entries in Lagerliste_ohne_Invest
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
        # Appending the entries to variable "list"
        try:
            while True:
                list.append(str(Lagerliste_ohne_Invest.objects.values_list('bestell_nr_field').filter(bestell_nr_field=bestell_nr).exclude(ausgegeben="1")[x]).replace(',', ''). replace("(", "").replace(")", ""))
                x = x + 1
        except:
            pass
        # Output if selected amount is bigger then entries available 
        if int(ausgabe_menge) > len(list):
            return render(request, "webapplication/handout_lager_ohne.html", {
                "alert": "Menge zu hoch",
                "lagerliste": Lagerliste_ohne_Invest.objects.filter(bestell_nr_field=bestell_nr).values('bestell_nr_field', 'typ', 'modell', 'spezifikation').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field")),
                "bestell_nr": nr
            })
        # "Austragung" of entries in "list"
        while i < int(ausgabe_menge):
            Lagerliste_ohne_Invest.objects.filter(bestell_nr_field=bestell_nr).update_or_create(id=int(str((id)[0]).replace(',', ''). replace("(", "").replace(")", "")), defaults={'ausgegeben': ausgegeben, 'herausgeber': herausgeber, 'ausgabe': ausgabe})
            i = i + 1
        # If there are still entries remaining for the selected item in Lagerliste_ohne_Invest then it uses this output
        if Lagerliste_ohne_Invest.objects.filter(bestell_nr_field=bestell_nr).exclude(ausgegeben="1"):
            return render(request, "webapplication/handout_lager_ohne.html", {
                "message": "Einträge erfolgreich ausgetragen",
                "lagerliste": Lagerliste_ohne_Invest.objects.filter(bestell_nr_field=bestell_nr).values('bestell_nr_field', 'typ', 'modell', 'spezifikation').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field")),
                "bestell_nr": nr
            })
        # If there are no entries remaining for the selected item in Lagerliste_ohne_Invest then it uses this output
        else:
            return render(request, "webapplication/lager_ohne_invest.html", {
                "lagerliste": Lagerliste_ohne_Invest.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field")),
            })
    return render(request, "webapplication/handout_lager_ohne.html", {
        "lagerliste": Lagerliste_ohne_Invest.objects.filter(bestell_nr_field=bestell_nr).values('bestell_nr_field', 'typ', 'modell', 'spezifikation').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field")),
        "bestell_nr": nr
    })

# View Function that proscesses the deletion of all entries with a specific Bestell_Nr. in Lagerliste_ohne_Invest
def löschen_lager_ohne(request, bestell_nr):
    if request.method == 'POST':
        # Double checking if the user really wants to delete the selected entries
        answer = request.POST["confirm"]
        # Deletion of entries if selected "yes"
        if answer in "yes":
            Lagerliste_ohne_Invest.objects.filter(bestell_nr_field=bestell_nr).delete()
            BestellListe.objects.update_or_create(sap_bestell_nr_field=bestell_nr, defaults={'geliefert': 0, 'geliefert_anzahl': 0})
            return HttpResponseRedirect(reverse('lager_ohne'))
        # Cancelation of deletion if "no" is selected
        else:
            return HttpResponseRedirect(reverse('detail_lager', args=[bestell_nr]))
    return render(request, "webapplication/löschen_lager_ohne.html", {
        "bestell_nr": bestell_nr
    })

# View Function that represents the content of BestellListe
def bestell(request):
    Menge =  BestellListe.objects.values_list('geliefert_anzahl', 'sap_bestell_nr_field')
    y = 0
    # Sets column "geliefert_anzahl" to "0" if column is "None"
    for _ in Menge:
        if str(Menge[y][0]) == "None":
            update = BestellListe.objects.update_or_create(sap_bestell_nr_field=Menge[y][1], defaults={'geliefert_anzahl': 0})
            y = y + 1
        else:
            y = y + 1
    return render(request, "webapplication/bestell.html", {
        "bestell_liste": BestellListe.objects.all(),
    })

# View Function that handles the creation of new entries in BestellListe
def create_bestell(request):
    if request.method == "POST":
        bestell_nr = request.POST["sap_bestell_nr"]
        modell = request.POST["modell"]
        typ = request.POST["typ"]
        menge = request.POST["menge"]
        preis_pro_stück = str(request.POST["preis_pro_stück"]).replace(",", ".")
        spezi = request.POST["spezifikation"]
        zuweisung = request.POST["zuweisung"]
        investmittel = request.POST["investmittel"]
        invnr_von_bis = ""
        geliefert = 0
        geliefert_anzahl = 0
        ersteller = request.user
        bearbeitet = timezone.now()
        link = request.POST["link"] or ' '
        
        # Creation of the new entry for BestellListe
        bestellung = BestellListe.objects.create(sap_bestell_nr_field=bestell_nr, modell=modell, typ=typ, menge=menge, preis_pro_stück=preis_pro_stück, spezifikation=spezi, zuweisung=zuweisung, inventarnummern_von_bis=invnr_von_bis, geliefert=geliefert, geliefert_anzahl=geliefert_anzahl, ersteller=ersteller, investmittel=investmittel, bearbeitet=bearbeitet, link=link)
        return render(request, "webapplication/create_bestell.html", {
            "message": "Einträge erfolgreich angelegt"
        })
    return render(request, "webapplication/create_bestell.html")

# View Function that handles the updating of existing entries in BestellListe
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
        link = request.POST["link"] or ' '
        
        # Updating the entry in BestellListe
        bestellung = BestellListe.objects.filter(sap_bestell_nr_field=bestell_nr).update(sap_bestell_nr_field = sap_bestell_nr_field, modell = modell, typ = typ, menge = menge, preis_pro_stück = preis_pro_stück, spezifikation = spezi, zuweisung = zuweisung, geliefert_anzahl = geliefert_anzahl, bearbeitet = timezone.now(), link=link)
        bnr = BestellListe.objects.get(pk=sap_bestell_nr_field)
        # If the column "geliefert_anzahl" was updated
        if geliefert_anzahl:
            # If the column "geliefert_anzahl" is equal to the column "Menge" then set the column "geliefert" to "1"
            if int(geliefert_anzahl) == int(menge) :
                bestellung = BestellListe.objects.update_or_create(sap_bestell_nr_field=sap_bestell_nr_field, defaults={'geliefert': geliefert})
            # Checks if the updated entry has the value "Nein" for the column "Investmittel"
            if str(BestellListe.objects.values_list('investmittel').filter(sap_bestell_nr_field=sap_bestell_nr_field))[13:17] in "Nein":
                if int(geliefert_anzahl) > anzahl:
                    y = "test"
                    i = anzahl
                    # Creation of entries for Lagerliste_ohne_Invest until the number of new entries is equal to the value in column "Menge"
                    while i < int(geliefert_anzahl):
                        Lagerliste_ohne_Invest.objects.create(typ=typ, modell=modell, spezifikation=spezi, bestell_nr_field=bnr, zuweisung=zuweisung, ausgegeben=0)
                        i = i + 1
        # If the column "Menge" is equal to "geliefert_anzahl" it uses this output
        if int(geliefert_anzahl) == int(menge):
            return render(request, "webapplication/bestell.html", {
                "bestell_nr": bestell_nr,
                "bestell_liste": BestellListe.objects.all()
            })
        # If the column "sap_bestell_nr_field" was changed it uses this output
        if str(bnr) != str(nr):
            return render(request, "webapplication/update_bestell.html", {
                "message": "Einträge erflogreich aktualisiert",
                "bestell_liste": BestellListe.objects.all().filter(sap_bestell_nr_field=bnr),
                "bestell_nr": str(bnr)
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

# View Function that handles the deletion of a selected entry in BestellListe
def löschen_bestell(request, bestell_nr):
    if request.method == 'POST':
        # Double Checking if the user really wants to delete the entry
        answer = request.POST["confirm"]
        # Deletion of entries if selected "yes"
        if answer in "yes":
            try:
                BestellListe.objects.filter(sap_bestell_nr_field=bestell_nr).delete()
                return HttpResponseRedirect(reverse('bestell_liste'))
            # If there already are entries in Lagerliste which are connected to this entry in BestellListe it uses this output
            except IntegrityError:
                return render(request, "webapplication/update_bestell.html", {
                    "bestell_nr": bestell_nr,
                    "bestell_liste": BestellListe.objects.all().filter(sap_bestell_nr_field=bestell_nr),
                    "alert": "Bestellung kann nicht gelöscht werden, Grund: Lagereinträge für diese Bestellung vorhanden!"
                })
        # Cancelation of the deletion
        else:
            return HttpResponseRedirect(reverse('update_bestell', args=[bestell_nr]))
    return render(request, "webapplication/löschen_bestell.html", {
        "sap_bestell_nr": bestell_nr
    })

# View Function that represents the content of Lagerliste and BestellListe that is related to the logged in user
def profile(request, user_id):
    user_name = User.objects.values_list('username').get(pk=user_id)
    user = User.objects.values('username').exclude(pk=user_id)
    username = user_name[0]
    return render(request, "webapplication/profile.html", {
        "user_id": user_id,
        "bestell_liste": BestellListe.objects.all(),
        "user_name": request.user,
        "username": username,
        "users": user,
       "lagerliste": Lagerliste.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung', 'herausgeber', 'ausgabe').exclude(ausgegeben="0").annotate(Menge=Count("bestell_nr_field"))
    })

# View Function that represents the content of Lagerliste_ohne_Invest that is related to the logged in user
def profile_lager_ohne(request, user_id):
    user_name = User.objects.values_list('username').get(pk=user_id)
    username = user_name[0]
    return render(request, "webapplication/profile_lager_ohne.html", {
        "user_id": user_id,
        "username": username,
        "lagerliste": Lagerliste_ohne_Invest.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'herausgeber', 'ausgabe').exclude(ausgegeben="0").annotate(Menge=Count("bestell_nr_field"))
    })

# View Function that represents the detailed content of entries with the same Bestell_Nr. in Lagerliste that are related to the logged in user
def detail_lager_profile(request, user_id, bestell_nr):
    user_name = User.objects.values_list('username').get(pk=user_id)
    username = user_name[0]
    return render(request, "webapplication/detail_lager_profile.html", {
        "user_id": user_id,
        "bestellung": bestell_nr,
        "lagerliste": Lagerliste.objects.all().values('inventarnummer', 'typ', 'modell', 'spezifikation', 'zuweisung', 'herausgeber', 'ausgabe', 'klinik', 'bestell_nr_field').exclude(ausgegeben="0").filter(bestell_nr_field=bestell_nr)
    })

# View Function that represents the detailed content of entries with the same Bestell_Nr. in Lagerliste_ohne_Invest that are related to the logged in user
def detail_profile_lager_ohne(request, user_id, bestell_nr):
    user_name = User.objects.values_list('username').get(pk=user_id)
    username = user_name[0]
    return render(request, "webapplication/detail_profile_lager_ohne.html", {
        "user_id": user_id,
        "user_name": username,
        "bestellung": bestell_nr,
        "lagerliste": Lagerliste_ohne_Invest.objects.all().values('id', 'typ', 'modell', 'spezifikation', 'herausgeber', 'ausgabe', 'bestell_nr_field').exclude(ausgegeben="0").filter(bestell_nr_field=bestell_nr)
    })

# View Function that represents the content of Investmittelplan
def invest(request):
    investmittelplan = Investmittelplan.objects.all().order_by('klinik_ou')
    # Values for the pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(investmittelplan, 50)
    # Pagination failsaves
    try:
        invest = paginator.page(page)
    except PageNotAnInteger:
        invest = paginator.page(1)
    except EmptyPage:
        invest = paginator.page(paginator.num_pages)
    return render(request, "webapplication/invest.html", {
        "investmittelplan": invest
    })

# View Function that represents the detailed content of a selected "ou" which shows the entries that are related to said "ou" in Investmittelplan
def detail_invest(request, klinik_ou):
    ou = klinik_ou
    nr = Lagerliste.objects.values_list('bestell_nr_field').filter(klinik=ou)
    detail_invest = Lagerliste.objects.select_related().values('klinik', 'bestell_nr_field', 'modell', 'typ', 'spezifikation', 'bestell_nr_field__preis_pro_stück').filter(bestell_nr_field__in=nr[0:]).filter(klinik=ou).annotate(Menge=Count("bestell_nr_field"))
    return render(request, "webapplication/detail_invest.html", {
        "detail_invest": detail_invest,
        "klinik_ou": ou
    })