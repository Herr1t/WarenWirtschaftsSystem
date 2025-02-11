from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group
from django.core.files import File
import csv

from .models import Lagerliste, BestellListe, Investmittelplan, User, Lagerliste_ohne_Invest, Investmittelplan_Soll, Detail_Investmittelplan_Soll, Achievements, Download

def group_check(user):
    username = user
    if username.groups.filter(name='Klinik-Admin').exists():
        return("1")
    else:
        return("0")

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
        group = Group.objects.get(name='Servicedesk')

        # Check if authentication successful
        if user is not None:
            if user.groups.filter(name='Klinik-Admin').exists() or user.groups.filter(name='Admin').exists() or user.groups.filter(name='Servicedesk').exists():
                pass
            else:
                group.user_set.add(user)
            if user.groups.filter(name='Servicedesk').exists():
                staff = User.objects.update_or_create(username=username, defaults={'is_staff': "1"})
            if user.groups.filter(name='Klinik-Admin').exists():
                login(request, user)
                return HttpResponseRedirect(reverse("investmittel_soll"))
            else:
                login(request, user)
                return HttpResponseRedirect(reverse("lagerliste"))
        else:
            return render(request, "webapplication/login.html", {
                "message": "Ungültiger Nutzername und/oder Passwort."
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
        group = Group.objects.get(name='Klinik-Admin')

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "webapplication/register.html", {
                "message": "Passwörter müssen sich gleichen."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, password=password)
            user.set_password(password)
            user.save()
            group.user_set.add(user)
            confirm = User.objects.update_or_create(username=username, defaults={'is_active': "0"})
        except IntegrityError:
            return render(request, "webapplication/register.html", {
                "message": "Nutzername bereits vergeben."
            })
        return render(request, "webapplication/register.html", {
            "confirm": "1"
        }) 
    else:
        return render(request, "webapplication/register.html")

def pw_reset(request):
    if request.method == "POST":
        uname = request.POST["username"]
        new_pw = request.POST["new_password"]
        confirm_pw = request.POST["confirm_password"]
        if new_pw != confirm_pw:
            return render(request, "webapplication/pw_reset.html", {
                "message": "Passwörter müssen sich gleichen."
            })
        else:
            u = User.objects.get(username=uname)
            u.set_password(new_pw)
            u.save()
            return render(request, "webapplication/pw_reset.html", {
                "confirm": "1"
            })
    else:
        return render(request, "webapplication/pw_reset.html")

# View Function that represents the content of the Lagerliste
def lager(request):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        x = 0
        files = Download.objects.all()

        if request.method == "POST":
            Liste = Lagerliste.objects.values_list('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung').filter(Q(bestell_nr_field__sap_bestell_nr_field__icontains=request.POST["input"]) | Q(modell__icontains=request.POST["input"]) | Q(typ__icontains=request.POST["input"]) | Q(spezifikation__icontains=request.POST["input"]) | Q(zuweisung__icontains=request.POST["input"])).exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field"))
            
            f = csv.writer(open("/Users/voigttim/Documents/Programming/WarenWirtschaftsSystem/Webserver/WWSystem/media/Download/lagerliste.csv", "w"))        
            f.writerow(["Bestell-Nr.", "Modell", "Typ", "Spezifikation", "Zuweisung", "Menge"])

            for _ in Liste:
                f.writerow([Liste[x][0], Liste[x][1], Liste[x][2], Liste[x][3], Liste[x][4], Liste[x][5]])
                x = x + 1
            Menge =  Lagerliste.objects.values_list('zuweisung', 'inventarnummer')
            y = 0
            x = 0
            monitor = 0
            notebook = 0
            pc = 0
            drucker = 0
            scanner = 0
            dock = 0
            dik = 0
            trans = 0
            # Set Column "Zuweisung" to "Keine Zuweisung" if Column is "None"
            for _ in Menge:
                if str(Menge[y][0]) == "None":
                    update = Lagerliste.objects.update_or_create(inventarnummer=Menge[y][1], defaults={'zuweisung': "Keine Zuweisung"})
                    y = y + 1
                else:
                    y = y + 1
            mengen = Lagerliste.objects.values_list('bestell_nr_field', 'typ').annotate(Menge=Count("bestell_nr_field")).exclude(ausgegeben="1")
            for __ in mengen:
                if __[1] == "Monitor":
                    monitor = monitor + __[2]
                    x = x + 1
                elif __[1] == "Notebook":
                    notebook = notebook + __[2]
                    x = x + 1
                elif __[1]== "Desktop-PC":
                    pc = pc + __[2]
                    x = x + 1
                elif __[1] == "Drucker":
                    drucker = drucker + __[2]
                    x = x + 1
                elif __[1] == "Scanner":
                    scanner = scanner + __[2]
                    x = x + 1
                elif __[1] == "Dockingstation":
                    dock = dock + __[2]
                    x = x + 1
                elif __[1] == "Diktiergerät":
                    dik = dik + __[2]
                    x = x + 1
                elif __[1] == "Transkription":
                    trans = trans + __[2]
                    x = x + 1
                else:
                    x = x + 1
            return render(request, "webapplication/lager.html", {
                "lagerliste": Lagerliste.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field")),
                "monitor": monitor,
                "notebook": notebook,
                "pc": pc,
                "drucker": drucker,
                "scanner": scanner,
                "dock": dock,
                "dik": dik,
                "trans": trans,
                "files" : files,
                "confirm": "1"
            })
        else:
            Menge =  Lagerliste.objects.values_list('zuweisung', 'inventarnummer')
            y = 0
            x = 0
            monitor = 0
            notebook = 0
            pc = 0
            drucker = 0
            scanner = 0
            dock = 0
            dik = 0
            trans = 0
            # Set Column "Zuweisung" to "Keine Zuweisung" if Column is "None"
            for _ in Menge:
                if str(Menge[y][0]) == "None":
                    update = Lagerliste.objects.update_or_create(inventarnummer=Menge[y][1], defaults={'zuweisung': "Keine Zuweisung"})
                    y = y + 1
                else:
                    y = y + 1
            mengen = Lagerliste.objects.values_list('bestell_nr_field', 'typ').annotate(Menge=Count("bestell_nr_field")).exclude(ausgegeben="1")
            for __ in mengen:
                if __[1] == "Monitor":
                    monitor = monitor + __[2]
                    x = x + 1
                elif __[1] == "Notebook":
                    notebook = notebook + __[2]
                    x = x + 1
                elif __[1]== "Desktop-PC":
                    pc = pc + __[2]
                    x = x + 1
                elif __[1] == "Drucker":
                    drucker = drucker + __[2]
                    x = x + 1
                elif __[1] == "Scanner":
                    scanner = scanner + __[2]
                    x = x + 1
                elif __[1] == "Dockingstation":
                    dock = dock + __[2]
                    x = x + 1
                elif __[1] == "Diktiergerät":
                    dik = dik + __[2]
                    x = x + 1
                elif __[1] == "Transkription":
                    trans = trans + __[2]
                    x = x + 1
                else:
                    x = x + 1
            return render(request, "webapplication/lager.html", {
                "lagerliste": Lagerliste.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung').exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field")),
                "monitor": monitor,
                "notebook": notebook,
                "pc": pc,
                "drucker": drucker,
                "scanner": scanner,
                "dock": dock,
                "dik": dik,
                "trans": trans,
                "files": files
            })

# View Function that represents the detailed list of items for a specific Bestell_Nr. inside the Lagerliste
def detail_lager(request, bestell_nr):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        nr = bestell_nr
        bestell = Lagerliste.objects.filter(bestell_nr_field=nr)
        return render(request, "webapplication/detail_lager.html", {
            "detail_lagerliste": bestell,
            "bestell_nr": bestell_nr
        })

# View Function that handles the creation of new entries for the Lagerliste
def create_lager(request):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        if request.method == "POST":
            x = int(0)
            y = int(0)
            c = 0
            ach = 0
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
                    lager_count = Achievements.objects.filter(user=request.user).values_list('lager_count')
                    Lagerliste.objects.create(inventarnummer=inventarnummer, typ=typ, modell=modell, spezifikation=spezifikation, zuweisung=zuweisung, bestell_nr_field=bnr, ausgegeben=ausgegeben)
                    obj = Lagerliste.objects.get(pk=inventarnummer)
                    # Checking if creation of entry was succesfull
                    if obj is None:
                        fail = fail + inventarnummer + ", "
                    # Achievement check
                    if lager_count:
                        temp = str(lager_count[0]).replace('(', '').replace(',)', '')
                        if temp == "None":
                            new = 0
                            achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 1, 'lager_achievement': 0, 'bestell_count': 0, 'bestell_achievement': 0, 'handout_count': 0, 'handout_achievement': 0, 'rueckgabe_count': 0, 'rueckgabe_achievement': 0})
                        else:
                            new = int(str(lager_count[0]).replace('(', '').replace(',)', '')) + 1
                            achievement_count = Achievements.objects.filter(user=request.user).update(lager_count=new)
                    else:
                        new = 0
                        achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 1, 'lager_achievement': 0, 'bestell_count': 0, 'bestell_achievement': 0, 'handout_count': 0, 'handout_achievement': 0, 'rueckgabe_count': 0, 'rueckgabe_achievement': 0})
                    # If count 100 for Lagereinträge then Achievement unlock
                    if new == 50:
                        ach = 1
                    if new == 200:
                        ach = 2
                    if new == 500:
                        ach = 3
                # Checking if entry already exists
                except IntegrityError:
                    dupe = dupe + inventarnummer + ", "
                    continue
                except ValueError:
                    return render(request, "webapplication/login.html", {
                        "message": "Sie sind nicht angemeldet!"
                    })
            # Check if achievement unlocked
            if ach == 1:
                achievement_unlock = Achievements.objects.filter(user=request.user).update(lager_achievement=1)
            if ach == 2:
                achievement_unlock = Achievements.objects.filter(user=request.user).update(lager_achievement=2)
            if ach == 3:
                achievement_unlock = Achievements.objects.filter(user=request.user).update(lager_achievement=3)
            # Output if creation of at least one entry failed
            if fail:
                fail = fail[:-2]
                return render(request, "webapplication/create_lager.html", {
                    "dupe": dupe,
                    "fail": fail,
                    "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein"),
                    "unlock": ach
                })
            # Output if at least one of the entries already existed
            if dupe:
                dupe = dupe[:-2]
                return render(request, "webapplication/create_lager.html", {
                    "dupe": dupe,
                    "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein"),
                    "unlock": ach
                })
            return render(request, "webapplication/create_lager.html", {
                "message": "Einträge erfolgreich angelegt",
                "unlock": ach,
                "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")
            })
        return render(request, "webapplication/create_lager.html", {
            "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")
        })

# View Function that handles the "austragung" of entries from the Lagerliste
def handout_lager(request):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        if request.method == "POST":
            x = 0
            c = 0
            ach = 0
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
                    handout_count = Achievements.objects.filter(user=request.user).values_list('handout_count')
                    ausgabe_check = str(Lagerliste.objects.values_list('ausgegeben').get(pk=inventarnummer))
                    # Checks if entry isnt already "ausgegeben"
                    if ausgabe_check in "('0',)":
                        ___ = Lagerliste.objects.values_list('bestell_nr_field').get(pk=inventarnummer)
                        temp = BestellListe.objects.values_list('preis_pro_stück').get(pk=___[0])
                        __ = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').get(pk=klinik)
                        # Subtracting the "preis_pro_stück" of the entries in "list" from the column "investmittel_übrig_in_euro" of the selected "ou" in Investmittelplan
                        abzug = __[0] - temp[0]
                        abrechnung = Investmittelplan.objects.update_or_create(klinik_ou=klinik, defaults={'investmittel_übrig_in_euro': abzug})
                        # "Austragung" of the entries in Lagerliste
                        ausgeben = Lagerliste.objects.update_or_create(inventarnummer=inventarnummer, defaults={'ausgegeben': ausgegeben, 'klinik': klinik, 'ausgabe': ausgabe, 'herausgeber': herausgeber})
                        if handout_count:
                            temp = str(handout_count[0]).replace('(', '').replace(',)', '')
                            if temp == "None":
                                new = 0
                                achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 0, 'lager_achievement': 0, 'bestell_count': 0, 'bestell_achievement': 0, 'handout_count': 1, 'handout_achievement': 0, 'rueckgabe_count': 0, 'rueckgabe_achievement': 0})
                            else:
                                new = int(str(handout_count[0]).replace('(', '').replace(',)', '')) + 1
                                achievement_count = Achievements.objects.filter(user=request.user).update(handout_count=new)
                        else:
                            new = 0
                            achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 0, 'lager_achievement': 0, 'bestell_count': 0, 'bestell_achievement': 0, 'handout_count': 1, 'handout_achievement': 0, 'rueckgabe_count': 0, 'rueckgabe_achievement': 0})
                        if new == 50:
                            ach = 1
                        if new == 200:
                            ach = 2
                        if new == 500:
                            ach = 3
                    # Output if entry is already "ausgetragen"
                    else:
                        fail = fail + inventarnummer + ", "
                        continue 
                # If entry does not exist in Lagerliste then it gets appended to the variable "dne"
                except ObjectDoesNotExist:
                    dne = dne + inventarnummer + ", "
                    continue
                except ValueError:
                    return render(request, "webapplication/login.html", {
                        "message": "Sie sind nicht angemeldet!"
                    })
            if ach == 1:
                achievement_unlock = Achievements.objects.filter(user=request.user).update(handout_achievement=1)
            if ach == 2:
                achievement_unlock = Achievements.objects.filter(user=request.user).update(handout_achievement=2)
            if ach == 3:
                achievement_unlock = Achievements.objects.filter(user=request.user).update(handout_achievement=3)
            # If there is at least one entry in "fail" then is uses this output
            if fail:
                fail = fail[:-2]
                return render(request, "webapplication/handout_lager.html", {
                    "dne": dne,
                    "fail": fail,
                    "unlock": ach
                })
            # If there is at least one entry in "dne" then it uses this output
            if dne:
                dne = dne[:-2]
                return render(request, "webapplication/handout_lager.html", {
                    "dne": dne,
                    "unlock": ach
                })
            # Checks if column "investmittel_übrig_in_euro" from Investmittelplan is below 0
            check = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').get(klinik_ou=klinik)
            if float(check[0]) < 0:
                    return render(request, "webapplication/handout_lager.html", {
                    "message": "Einträge erfolgreich ausgetragen",
                    "alarm": klinik,
                    "geld": float(check[0]),
                    "unlock": ach
                })
            else:
                return render(request, "webapplication/handout_lager.html", {
                    "message": "Einträge erfolgreich ausgetragen",
                    "unlock": ach
                })
        return render(request, "webapplication/handout_lager.html")

def handout_lager_all(request, bestell_nr):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        if request.method == 'POST':
            x = 0
            c = 0
            ach = 0
            klinik = request.POST["klinik"]
            bestellung = Lagerliste.objects.values_list('inventarnummer').filter(bestell_nr_field=bestell_nr)
            ausgegeben = 1
            ausgabe = timezone.now
            herausgeber = request.user
            dne = ""
            fail = ""

            for _ in bestellung:
                inventarnummer = str(_).replace("('", "").replace("',)", "")
                try:
                    handout_count = Achievements.objects.filter(user=request.user).values_list('handout_count')
                    ausgabe_check = str(Lagerliste.objects.values_list('ausgegeben').get(pk=inventarnummer))
                    # Checks if entry isnt already "ausgegeben"
                    if ausgabe_check in "('0',)":
                        ___ = Lagerliste.objects.values_list('bestell_nr_field').get(pk=inventarnummer)
                        temp = BestellListe.objects.values_list('preis_pro_stück').get(pk=___[0])
                        __ = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').get(pk=klinik)
                        # Subtracting the "preis_pro_stück" of the entries in "list" from the column "investmittel_übrig_in_euro" of the selected "ou" in Investmittelplan
                        abzug = __[0] - temp[0]
                        abrechnung = Investmittelplan.objects.update_or_create(klinik_ou=klinik, defaults={'investmittel_übrig_in_euro': abzug})
                        # "Austragung" of the entries in Lagerliste
                        ausgeben = Lagerliste.objects.update_or_create(inventarnummer=inventarnummer, defaults={'ausgegeben': ausgegeben, 'klinik': klinik, 'ausgabe': ausgabe, 'herausgeber': herausgeber})
                        if handout_count:
                            temp = str(handout_count[0]).replace('(', '').replace(',)', '')
                            if temp == "None":
                                new = 0
                                achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 0, 'lager_achievement': 0, 'bestell_count': 0, 'bestell_achievement': 0, 'handout_count': 1, 'handout_achievement': 0, 'rueckgabe_count': 0, 'rueckgabe_achievement': 0})
                            else:
                                new = int(str(handout_count[0]).replace('(', '').replace(',)', '')) + 1
                                achievement_count = Achievements.objects.filter(user=request.user).update(handout_count=new)
                        else:
                            new = 0
                            achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 0, 'lager_achievement': 0, 'bestell_count': 0, 'bestell_achievement': 0, 'handout_count': 1, 'handout_achievement': 0, 'rueckgabe_count': 0, 'rueckgabe_achievement': 0})
                        if new == 50:
                            ach = 1
                        if new == 200:
                            ach = 2
                        if new == 500:
                            ach = 3
                    # Output if entry is already "ausgetragen"
                    else:
                        fail = fail + inventarnummer + ", "
                        continue 
                # If entry does not exist in Lagerliste then it gets appended to the variable "dne"
                except ObjectDoesNotExist:
                    dne = dne + inventarnummer + ", "
                    continue
                except ValueError:
                    return render(request, "webapplication/login.html", {
                        "message": "Sie sind nicht angemeldet!"
                    })
            # If there is at least one entry in "fail" then is uses this output
            if fail:
                fail = fail[:-2]
                return render(request, "webapplication/handout_lager_all.html", {
                    "bestell_nr": bestell_nr,
                    "dne": dne,
                    "fail": fail,
                    "unlock": ach
                })
            # If there is at least one entry in "dne" then it uses this output
            if dne:
                dne = dne[:-2]
                return render(request, "webapplication/handout_lager_all.html", {
                    "bestell_nr": bestell_nr,
                    "dne": dne,
                    "unlock": ach
                })
            # Checks if column "investmittel_übrig_in_euro" from Investmittelplan is below 0
            check = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').get(klinik_ou=klinik)
            if float(check[0]) < 0:
                    return render(request, "webapplication/handout_lager_all.html", {
                    "bestell_nr": bestell_nr,
                    "message": "Einträge erfolgreich ausgetragen",
                    "alarm": klinik,
                    "geld": float(check[0]),
                    "unlock": ach
                })
            else:    
                return render(request, "webapplication/handout_lager_all.html", {
                    "bestell_nr": bestell_nr,
                    "message": "Einträge erfolgreich ausgetragen",
                    "unlock": ach
                })
        return render(request, "webapplication/handout_lager_all.html", {
            "bestell_nr": bestell_nr
        })

# View Function that handles the "Rückgabe" of already "ausgegebenen" entries in Lagerliste
def rückgabe(request):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        if request.method == 'POST':
            x = 0
            c = 0
            ach = 0
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
                    rueckgabe_count = Achievements.objects.filter(user=request.user).values_list('rueckgabe_count')
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
                        if rueckgabe_count:
                            temp = str(rueckgabe_count[0]).replace('(', '').replace(',)', '')
                            if temp == "None":
                                new = 0
                                achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 0, 'lager_achievement': 0, 'bestell_count': 0, 'bestell_achievement': 0, 'handout_count': 0, 'handout_achievement': 0, 'rueckgabe_count': 1, 'rueckgabe_achievement': 0})
                            else:
                                new = int(str(rueckgabe_count[0]).replace('(', '').replace(',)', '')) + 1
                                achievement_count = Achievements.objects.filter(user=request.user).update(rueckgabe_count=new)
                        else:
                            new = 0
                            achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 0, 'lager_achievement': 0, 'bestell_count': 0, 'bestell_achievement': 0, 'handout_count': 0, 'handout_achievement': 0, 'rueckgabe_count': 1, 'rueckgabe_achievement': 0})
                        if new == 10:
                            ach = 1
                        if new == 50:
                            ach = 2
                        if new == 150:
                            ach = 3
                    # Output if entry is already "zurückgegeben"
                    else:
                        fail = fail + inventarnummer + ", "
                        continue
                # If entry does not exist in Lagerliste then it gets appended to the variable "dne"
                except ObjectDoesNotExist:
                    dne = dne + inventarnummer + ", "
                    continue
                except ValueError:
                    return render(request, "webapplication/login.html", {
                        "message": "Sie sind nicht angemeldet!"
                    })
            if ach == 1:
                achievement_unlock = Achievements.objects.filter(user=request.user).update(rueckgabe_achievement=1)
            if ach == 2:
                achievement_unlock = Achievements.objects.filter(user=request.user).update(rueckgabe_achievement=2)
            if ach == 3:
                achievement_unlock = Achievements.objects.filter(user=request.user).update(rueckgabe_achievement=3)
            # Output if there is at least one entry in fail then it uses this output
            if fail:
                fail = fail[:-2]
                return render(request, "webapplication/rückgabe.html", {
                    "fail": fail,
                    "dne": dne,
                    "unlock": ach
                })
            # If there is at least one entry in "dne" then it uses this output
            if dne:
                dne = dne[:-2]
                return render(request, "webapplication/rückgabe.html", {
                    "dne": dne,
                    "unlock": ach
                })
            return render(request, "webapplication/rückgabe.html", {
                "message": "Geräte erfolgreich zurückgegeben",
                "unlock": ach
            }) 
        return render(request, "webapplication/rückgabe.html")

# View Function that proscesses the deletion of all entries with a specific Bestell_Nr. in Lagerliste
def löschen_lager(request, bestell_nr):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
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
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
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
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
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
            try:
                while i < int(ausgabe_menge):
                    Lagerliste_ohne_Invest.objects.filter(bestell_nr_field=bestell_nr).update_or_create(id=int(str((id)[0]).replace(',', ''). replace("(", "").replace(")", "")), defaults={'ausgegeben': ausgegeben, 'herausgeber': herausgeber, 'ausgabe': ausgabe})
                    i = i + 1
            except ValueError:
                    return render(request, "webapplication/login.html", {
                        "message": "Sie sind nicht angemeldet!"
                    })
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
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
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
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        x = 0
        files = Download.objects.all()

        if request.method == "POST":
            Liste = BestellListe.objects.values_list('sap_bestell_nr_field', 'modell', 'typ', 'spezifikation', 'zuweisung', 'ersteller', 'investmittel', 'preis_pro_stück', 'menge', 'geliefert_anzahl').filter(Q(sap_bestell_nr_field__icontains=request.POST["input"]) | Q(modell__icontains=request.POST["input"]) | Q(typ__icontains=request.POST["input"]) | Q(spezifikation__icontains=request.POST["input"]) | Q(zuweisung__icontains=request.POST["input"]) | Q(ersteller__username__icontains=request.POST["input"]) | Q(investmittel__icontains=request.POST["input"]) | Q(preis_pro_stück__icontains=request.POST["input"]) | Q(menge__icontains=request.POST["input"]) | Q(geliefert_anzahl__icontains=request.POST["input"])).exclude(geliefert="1")
            
            f = csv.writer(open("/Users/voigttim/Documents/Programming/WarenWirtschaftsSystem/Webserver/WWSystem/media/Download/bestellliste.csv", "w"))        
            f.writerow(["SAP Bestell-Nr.", "Modell", "Typ", "Spezifikation", "Zuweisung", "Ersteller", "Invest", "Preis pro Stück", "Menge", "Anzahl Geliefert"])

            for _ in Liste:
                f.writerow([Liste[x][0], Liste[x][1], Liste[x][2], Liste[x][3], Liste[x][4], Liste[x][5], Liste[x][6], Liste[x][7], Liste[x][8], Liste[x][9]])
                #f.writerow([Test[x][0], Test[x][1], Test[x][2], Test[x][3], Test[x][4], Test[x][5], Test[x][6], Test[x][7], Test[x][8], Test[x][9], Test[x][10], Test[x][11]])
                x = x + 1
            
            return render(request, "webapplication/bestell.html", {
                "bestell_liste": BestellListe.objects.all(),
                "files" : files,
                "confirm": "1"
            })
        else:
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
                "files": files
            })

def some_view(request):
    x = 0
    files = Download.objects.all()

    if request.method == "POST":
        Test = BestellListe.objects.values_list('sap_bestell_nr_field', 'modell', 'typ', 'spezifikation', 'zuweisung', 'link', 'ersteller', 'bearbeitet', 'investmittel', 'preis_pro_stück', 'menge', 'geliefert_anzahl').filter(Q(sap_bestell_nr_field__icontains=request.POST["input"]) | Q(modell__icontains=request.POST["input"]) | Q(typ__icontains=request.POST["input"]) | Q(spezifikation__icontains=request.POST["input"]) | Q(zuweisung__icontains=request.POST["input"]) | Q(investmittel__icontains=request.POST["input"]) | Q(preis_pro_stück__icontains=request.POST["input"]) | Q(menge__icontains=request.POST["input"]) | Q(geliefert_anzahl__icontains=request.POST["input"])).exclude(geliefert="1")
        #Test = BestellListe.objects.values_list('sap_bestell_nr_field', 'modell', 'typ', 'spezifikation', 'zuweisung', 'link', 'ersteller', 'bearbeitet', 'investmittel', 'preis_pro_stück', 'menge', 'geliefert_anzahl').filter(bearbeitet__icontains=request.POST["input"])
        f = csv.writer(open("/Users/voigttim/Documents/Programming/WarenWirtschaftsSystem/Webserver/WWSystem/media/Download/bestellliste.csv", "w"))        
        f.writerow(["SAP Bestell-Nr.", "Modell", "Typ", "Spezifikation", "Zuweisung", "Link", "Ersteller", "Bearbeitet", "Invest", "Preis pro Stück", "Menge", "Anzahl Geliefert"])

        for _ in Test:
            #writer.writerow([Liste[x][0], Liste[x][1], Liste[x][2], Liste[x][3], Liste[x][4], Liste[x][5], Liste[x][6], Liste[x][7], Liste[x][8], Liste[x][9], Liste[x][10], Liste[x][11]])
            f.writerow([Test[x][0], Test[x][1], Test[x][2], Test[x][3], Test[x][4], Test[x][5], Test[x][6], Test[x][7], Test[x][8], Test[x][9], Test[x][10], Test[x][11]])
            x = x + 1
        
        return render(request, "webapplication/csv.html", {
            "bestell_liste": BestellListe.objects.all(),
            "files" : files,
            "confirm": "1",
            "message": Test
        })
    else:
        return render(request, "webapplication/csv.html", {
            "bestell_liste": BestellListe.objects.all(),
            "files": files,
        })
    
def download(request, download_id):
    datei = get_object_or_404(Download, pk=download_id)
    dateipfad = datei.dateipfad.path
    response = FileResponse(open(dateipfad, 'rb'))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = f'attachment; filename="{datei.titel}"'
    return response

# View Function that handles the creation of new entries in BestellListe
def create_bestell(request):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
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
            bestell_count = Achievements.objects.filter(user=ersteller).values_list('bestell_count')
            ach = 0
            
            try:
                # Creation of the new entry for BestellListe
                bestellung = BestellListe.objects.create(sap_bestell_nr_field=bestell_nr, modell=modell, typ=typ, menge=menge, preis_pro_stück=preis_pro_stück, spezifikation=spezi, zuweisung=zuweisung, inventarnummern_von_bis=invnr_von_bis, geliefert=geliefert, geliefert_anzahl=geliefert_anzahl, ersteller=ersteller, investmittel=investmittel, bearbeitet=bearbeitet, link=link)
                # Achievement check
                if bestell_count:
                    temp = str(bestell_count[0]).replace('(', '').replace(',)', '')
                    if temp == "None":
                        new = 0
                        achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 0, 'lager_achievement': 0, 'bestell_count': 1, 'bestell_achievement': 0, 'handout_count': 0, 'handout_achievement': 0, 'rueckgabe_count': 0, 'rueckgabe_achievement': 0})
                    else:
                        new = int(str(bestell_count[0]).replace('(', '').replace(',)', '')) + 1
                        achievement_count = Achievements.objects.filter(user=ersteller).update(bestell_count=new)
                else:
                    new = 0
                    achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 0, 'lager_achievement': 0, 'bestell_count': 1, 'bestell_achievement': 0, 'handout_count': 0, 'handout_achievement': 0, 'rueckgabe_count': 0, 'rueckgabe_achievement': 0})
                # If count equals threshold achievement
                if new == 10:
                    ach = 1
                if new == 50:
                    ach = 2
                if new == 150:
                    ach = 3
            except ValueError:
                    return render(request, "webapplication/login.html", {
                        "alert": "Sie sind nicht angemeldet!"
                    })
            except IntegrityError:
                    return render(request, "webapplication/create_bestell.html", {
                        "alert": "Bestellnummer bereits vergeben!"
                    })
            if ach == 1:
                achievement_unlock = Achievements.objects.filter(user=request.user).update(bestell_achievement=1)
            if ach == 2:
                achievement_unlock = Achievements.objects.filter(user=request.user).update(bestell_achievement=2)
            if ach == 3:
                achievement_unlock = Achievements.objects.filter(user=request.user).update(bestell_achievement=3)
            return render(request, "webapplication/create_bestell.html", {
                "message": "Einträge erfolgreich angelegt",
                "unlock": ach
            })
        return render(request, "webapplication/create_bestell.html")

# View Function that handles the updating of existing entries in BestellListe
def update(request, bestell_nr):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
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
            update_ach = Achievements.objects.filter(user=request.user).values_list('update_achievement')
            ach = 0
            
            # Updating the entry in BestellListe
            try:
                bestellung = BestellListe.objects.filter(sap_bestell_nr_field=bestell_nr).update(sap_bestell_nr_field = sap_bestell_nr_field, modell = modell, typ = typ, menge = menge, preis_pro_stück = preis_pro_stück, spezifikation = spezi, zuweisung = zuweisung, geliefert_anzahl = geliefert_anzahl, bearbeitet = timezone.now(), link=link)
                if update_ach:
                    temp = str(update_ach[0]).replace('(', '').replace(',)', '')
                    if temp == "0":
                        ach = 1
                        achievement_unlock = Achievements.objects.update_or_create(user=request.user, defaults={'update_achievement': 1})
                else:
                    ach = 1
                    achievement_unlock = Achievements.objects.update_or_create(user=request.user, defaults={'update_achievement': 1})
            except IntegrityError:
                return render(request, "webapplication/update_bestell.html", {
                    "alert": "Bestellnummer konnte nicht bearbeitet werden, da dieser Bestellung bereits Lagereinträge zugewiesen wurden.",
                    "bestell_nr": bestell_nr,
                    "bestell_liste": BestellListe.objects.all().filter(sap_bestell_nr_field=nr),
                    "unlock": ach
            })
            except ValueError:
                    return render(request, "webapplication/login.html", {
                        "message": "Sie sind nicht angemeldet!"
                    })
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
                    "bestell_liste": BestellListe.objects.all(),
                    "unlock": ach
                })
            # If the column "sap_bestell_nr_field" was changed it uses this output
            if str(bnr) != str(nr):
                return render(request, "webapplication/update_bestell.html", {
                    "message": "Einträge erflogreich aktualisiert",
                    "bestell_liste": BestellListe.objects.all().filter(sap_bestell_nr_field=bnr),
                    "bestell_nr": str(bnr),
                    "unlock": ach
                })
            return render(request, "webapplication/update_bestell.html", {
                "message": "Einträge erflogreich aktualisiert",
                "bestell_nr": bestell_nr,
                "bestell_liste": BestellListe.objects.all().filter(sap_bestell_nr_field=nr),
                "unlock": ach
            })
        return render(request, "webapplication/update_bestell.html", {
            "bestell_nr": bestell_nr,
            "bestell_liste": BestellListe.objects.all().filter(sap_bestell_nr_field=nr)
        })

# View Function that handles the deletion of a selected entry in BestellListe
def löschen_bestell(request, bestell_nr):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
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
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        user_name = User.objects.values_list('username').get(pk=user_id)
        user = User.objects.values('username').exclude(pk=user_id).exclude(is_staff="0")
        username = user_name[0]
        return render(request, "webapplication/profile.html", {
            "user_id": user_id,
            "bestell_liste": BestellListe.objects.all(),
            "user_name": request.user,
            "username": username,
            "users": user,
        "lagerliste": Lagerliste.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung', 'herausgeber', 'ausgabe').exclude(ausgegeben="0").annotate(Menge=Count("bestell_nr_field"))
        })

# View Function that represents the content of Lagerliste and BestellListe that is related to the logged in user
def achievements(request, user_id):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        achievements = Achievements.objects.all().filter(user=request.user)
        return render(request, "webapplication/achievements.html", {
            "achievements": achievements
        })

# View Function that represents the content of Lagerliste_ohne_Invest that is related to the logged in user
def profile_lager_ohne(request, user_id):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        user_name = User.objects.values_list('username').get(pk=user_id)
        username = user_name[0]
        return render(request, "webapplication/profile_lager_ohne.html", {
            "user_id": user_id,
            "username": username,
            "lagerliste": Lagerliste_ohne_Invest.objects.all().values('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'herausgeber', 'ausgabe').exclude(ausgegeben="0").annotate(Menge=Count("bestell_nr_field"))
        })

# View Function that represents the detailed content of entries with the same Bestell_Nr. in Lagerliste that are related to the logged in user
def detail_lager_profile(request, user_id, bestell_nr):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        user_name = User.objects.values_list('username').get(pk=user_id)
        username = user_name[0]
        return render(request, "webapplication/detail_lager_profile.html", {
            "user_id": user_id,
            "bestellung": bestell_nr,
            "lagerliste": Lagerliste.objects.all().values('inventarnummer', 'typ', 'modell', 'spezifikation', 'zuweisung', 'herausgeber', 'ausgabe', 'klinik', 'bestell_nr_field').exclude(ausgegeben="0").filter(bestell_nr_field=bestell_nr)
        })

# View Function that represents the detailed content of entries with the same Bestell_Nr. in Lagerliste_ohne_Invest that are related to the logged in user
def detail_profile_lager_ohne(request, user_id, bestell_nr):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
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
    x = 0
    files = Download.objects.all()

    if request.method == "POST":
        Liste = Investmittelplan.objects.values_list('klinik_ou', 'investmittel_jahresanfang_in_euro', 'investmittel_übrig_in_euro', 'bereich', 'team').filter(Q(klinik_ou__icontains=request.POST["input"]) | Q(investmittel_jahresanfang_in_euro__icontains=request.POST["input"]) | Q(investmittel_übrig_in_euro__icontains=request.POST["input"]) | Q(bereich__icontains=request.POST["input"]) | Q(team__icontains=request.POST["input"]))
        
        f = csv.writer(open("/Users/voigttim/Documents/Programming/WarenWirtschaftsSystem/Webserver/WWSystem/media/Download/investmittelplan.csv", "w"))
        f.writerow(["klinik_ou", "investmittel_jahresanfang_in_euro", "investmittel_übrig_in_euro", "bereich", "team"])

        for _ in Liste:
            f.writerow([Liste[x][0], Liste[x][1], Liste[x][2], Liste[x][3], Liste[x][4]])
            x = x + 1

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
            "investmittelplan": invest,
            "files" : files,
            "confirm": "1"
        })
    else:
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
            "investmittelplan": invest,
            "files": files
        })

# View Function that represents the detailed content of a selected "ou" which shows the entries that are related to said "ou" in Investmittelplan
def detail_invest(request, klinik_ou):
    x = 0
    files = Download.objects.all()
    conf = 0

    if request.method == "POST":
        ou = klinik_ou
        nr = Lagerliste.objects.values_list('bestell_nr_field').filter(klinik=ou)
        detail_invest = Lagerliste.objects.select_related().values('klinik', 'bestell_nr_field', 'modell', 'typ', 'spezifikation', 'bestell_nr_field__preis_pro_stück').filter(bestell_nr_field__in=nr[0:]).filter(klinik=ou).annotate(Menge=Count("bestell_nr_field"))
        
        Liste = Lagerliste.objects.values_list('klinik', 'bestell_nr_field', 'modell', 'typ', 'spezifikation', 'bestell_nr_field__preis_pro_stück').filter(Q(klinik__icontains=request.POST["input"]) | Q(bestell_nr_field__sap_bestell_nr_field__icontains=request.POST["input"]) | Q(modell__icontains=request.POST["input"]) | Q(typ__icontains=request.POST["input"]) | Q(spezifikation__icontains=request.POST["input"]) | Q(bestell_nr_field__preis_pro_stück__icontains=request.POST["input"])).filter(bestell_nr_field__in=nr[0:]).filter(klinik=ou).annotate(Menge=Count("bestell_nr_field"))
        
        f = csv.writer(open(f"/Users/voigttim/Documents/Programming/WarenWirtschaftsSystem/Webserver/WWSystem/media/Download/OU{klinik_ou}detail_investmitteplan.csv", "w"))
        f.writerow(["Klinik", "Bestell-Nr.", "Modell", "Typ", "Spezifikation", "Preis pro Stück", "Menge"])

        for _ in Liste:
            f.writerow([Liste[x][0], Liste[x][1], Liste[x][2], Liste[x][3], Liste[x][4], Liste[x][5], Liste[x][6]])
            x = x + 1
        
        er = Download.objects.values_list('titel')
        x = 0
        for _ in er:
            if str(f"OU{ou}_detail_investmittelplan") in str(_[x]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""):
                conf = 1
                x = x + 1
        if conf != 1:
            Download.objects.create(titel=f"OU{ou}_detail_investmittelplan", dateipfad=f"OU{ou}_detail_investmittelplan.csv")
            Download.save


        return render(request, "webapplication/detail_invest.html", {
            "detail_invest": detail_invest,
            "klinik_ou": ou,
            "files": files,
            "confirm": "1"
        })
    else:
        ou = klinik_ou
        nr = Lagerliste.objects.values_list('bestell_nr_field').filter(klinik=ou)
        detail_invest = Lagerliste.objects.select_related().values('klinik', 'bestell_nr_field', 'modell', 'typ', 'spezifikation', 'bestell_nr_field__preis_pro_stück').filter(bestell_nr_field__in=nr[0:]).filter(klinik=ou).annotate(Menge=Count("bestell_nr_field"))
        return render(request, "webapplication/detail_invest.html", {
            "detail_invest": detail_invest,
            "klinik_ou": ou,
            "files": files
        })

def invest_soll(request):
    x = 0
    files = Download.objects.all()

    if request.method == "POST":
        Liste = Investmittelplan_Soll.objects.values_list('ou', 'bereich', 'team', 'investmittel_gesamt').filter(Q(ou__icontains=request.POST["input"]) | Q(investmittel_gesamt__icontains=request.POST["input"]) | Q(bereich__icontains=request.POST["input"]) | Q(team__icontains=request.POST["input"]))
        
        f = csv.writer(open("/Users/voigttim/Documents/Programming/WarenWirtschaftsSystem/Webserver/WWSystem/media/Download/investmittelplan_planung.csv", "w"))
        f.writerow(["OU", "Bereich", "Team", "Investmittel Gesamt"])

        for _ in Liste:
            f.writerow([Liste[x][0], Liste[x][1], Liste[x][2], Liste[x][3]])
            x = x + 1
        
        investmittelplan_soll = Investmittelplan_Soll.objects.all().order_by('ou')
        alle = Investmittelplan_Soll.objects.values_list('investmittel_gesamt')
        l = len(alle)
        i = 0
        c = 0.00
        while i < l:
            c = c + float(str(alle[i]).replace("(Decimal('", "").replace("'),)", ""))
            i = i + 1
        gesamt = Investmittelplan_Soll.objects.values_list("investmittel_gesamt")
        return render(request, "webapplication/invest_soll.html", {
            "investmittelplan_soll": investmittelplan_soll,
            "alle": c,
            "files": files,
            "confirm": "1"
        })
    else:
        investmittelplan_soll = Investmittelplan_Soll.objects.all().order_by('ou')
        alle = Investmittelplan_Soll.objects.values_list('investmittel_gesamt')
        l = len(alle)
        i = 0
        c = 0.00
        while i < l:
            c = c + float(str(alle[i]).replace("(Decimal('", "").replace("'),)", ""))
            i = i + 1
        gesamt = Investmittelplan_Soll.objects.values_list("investmittel_gesamt")
        return render(request, "webapplication/invest_soll.html", {
            "investmittelplan_soll": investmittelplan_soll,
            "alle": c,
            "files": files
        })

def detail_invest_soll(request, ou):
    x = 0
    files = Download.objects.all()
    conf = 0

    if request.method == "POST":
        Liste = Detail_Investmittelplan_Soll.objects.values_list('typ', 'modell', 'menge', 'preis_pro_stück', 'admin', 'spezifikation').filter(Q(typ__icontains=request.POST["input"]) | Q(modell__icontains=request.POST["input"]) | Q(menge__icontains=request.POST["input"]) | Q(preis_pro_stück__icontains=request.POST["input"]) | Q(admin__username__icontains=request.POST["input"]) | Q(spezifikation__icontains=request.POST["input"])).filter(ou_invsoll=ou)

        f = csv.writer(open(f"/Users/voigttim/Documents/Programming/WarenWirtschaftsSystem/Webserver/WWSystem/media/Download/OU{ou}_investmittelplanung.csv", "w"))
        f.writerow(["Typ", "Modell", "Menge", "Preis pro Stück", "Ersteller", "Spezifikation"])

        for _ in Liste:
            f.writerow([Liste[x][0], Liste[x][1], Liste[x][2], Liste[x][3], Liste[x][4], Liste[x][5]])
            x = x + 1

        er = Download.objects.values_list('titel')
        x = 0
        for _ in er:
            if str(f"OU{ou}_investmittelplanung") in str(_[x]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""):
                conf = 1
                x = x + 1
        if conf != 1:
            Download.objects.create(titel=f"OU{ou}_investmittelplanung", dateipfad=f"OU{ou}_investmittelplanung.csv")
            Download.save

        return render(request, "webapplication/detail_invest_soll.html", {
            "ou": ou,
            "detail_investmittelplan_soll": Detail_Investmittelplan_Soll.objects.all().filter(ou_invsoll=ou),
            "files": files,
            "confirm": "1"
        })
    else:
        return render(request, "webapplication/detail_invest_soll.html", {
            "ou": ou,
            "detail_investmittelplan_soll": Detail_Investmittelplan_Soll.objects.all().filter(ou_invsoll=ou),
            "files": files
        })

def create_invest_soll(request, ou):
    if request.method == "POST":
        ou_invsoll = Investmittelplan_Soll.objects.get(ou=ou)
        typ = request.POST["typ"]
        modell = request.POST["modell"]
        menge = request.POST["menge"]
        preis_pro_stück = str(request.POST["preis_pro_stück"]).replace(",", ".")
        admin = request.user
        spezifikation = request.POST["spezifikation"]
        try:
            invest_planung = Detail_Investmittelplan_Soll.objects.create(ou_invsoll=ou_invsoll, typ=typ, modell=modell, menge=menge, preis_pro_stück=preis_pro_stück, admin=admin, spezifikation=spezifikation)
            preis = Detail_Investmittelplan_Soll.objects.values_list('preis_pro_stück').filter(ou_invsoll=ou_invsoll)
            meng = Detail_Investmittelplan_Soll.objects.values_list('menge').filter(ou_invsoll=ou_invsoll)
            length = len(preis) - 1
            gesamt = float(str(preis[length]).replace("(", "").replace(")", "").replace("Decimal", "").replace("'", "").replace(",", "")) * float(str(meng[length]).replace("(", "").replace(")", "").replace("Decimal", "").replace("'", "").replace(",", ""))
            jetzt = Investmittelplan_Soll.objects.values_list('investmittel_gesamt').get(ou=ou)
            neu = float(jetzt[0]) + gesamt
            Investmittelplan_Soll.objects.update_or_create(ou = ou, defaults={'investmittel_gesamt': neu})
            return render(request, "webapplication/create_invest_soll.html", {
                "message": "Eintrag erfolgreich geplant",
                "ou": ou
            })
        except ValueError:
            return render(request, "webapplication/create_invest_soll.html", {
                "alert": "Sie müssen angemeldet sein, damit Sie einen Eintrag erstellen können!",
                "ou": ou
            })
    return render(request, "webapplication/create_invest_soll.html", {
        "ou": ou
    })

def update_detail_invest_soll(request, ou, id):
    if request.method == "POST":
        items = Detail_Investmittelplan_Soll.objects.values_list("modell", "typ", "menge", "preis_pro_stück", "spezifikation").get(pk=id)
        modell = request.POST["modell"] or items[0]
        typ = request.POST["typ"] or items[1]
        menge = str(request.POST["menge"]).replace("-", "") or items[2]
        preis_pro_stück = str(request.POST["preis_pro_stück"]).replace(",", ".") or items[3]
        spezifikation = request.POST["spezifikation"] or items[4]

        preis_alt = Detail_Investmittelplan_Soll.objects.values_list("preis_pro_stück").filter(id=id)
        menge_alt = Detail_Investmittelplan_Soll.objects.values_list("menge").filter(id=id)
        length_alt = len(preis_alt) - 1
        gesamt_alt = float(str(preis_alt[length_alt]).replace("(", "").replace(")", "").replace("Decimal", "").replace("'", "").replace(",", "")) * float(str(menge_alt[length_alt]).replace("(", "").replace(")", "").replace("Decimal", "").replace("'", "").replace(",", ""))
        jetzt_alt = Investmittelplan_Soll.objects.values_list('investmittel_gesamt').get(ou=ou)
        neu_alt = float(jetzt_alt[0]) - gesamt_alt
        Investmittelplan_Soll.objects.update_or_create(ou = ou, defaults={'investmittel_gesamt': neu_alt})
        update = Detail_Investmittelplan_Soll.objects.filter(id=id).update(modell=modell, typ=typ, menge=menge, preis_pro_stück=preis_pro_stück, spezifikation=spezifikation)
        preis_neu = Detail_Investmittelplan_Soll.objects.values_list("preis_pro_stück").filter(id=id)
        menge_neu = Detail_Investmittelplan_Soll.objects.values_list("menge").filter(id=id)
        length_neu = len(preis_neu) - 1
        gesamt_neu = float(str(preis_neu[length_neu]).replace("(", "").replace(")", "").replace("Decimal", "").replace("'", "").replace(",", "")) * float(str(menge_neu[length_neu]).replace("(", "").replace(")", "").replace("Decimal", "").replace("'", "").replace(",", ""))
        jetzt_neu = Investmittelplan_Soll.objects.values_list('investmittel_gesamt').get(ou=ou)
        neu_neu = float(jetzt_neu[0]) + gesamt_neu
        Investmittelplan_Soll.objects.update_or_create(ou = ou, defaults={'investmittel_gesamt': neu_neu})

        if menge == "0":
            Detail_Investmittelplan_Soll.objects.filter(id=id).delete()
            return render(request, "webapplication/detail_invest_soll.html", {
                "ou": ou,
                "detail_investmittelplan_soll": Detail_Investmittelplan_Soll.objects.all().filter(ou_invsoll=ou)
            })

        return render(request, "webapplication/update_detail_invest_soll.html", {
            "invest_soll": Detail_Investmittelplan_Soll.objects.all().filter(id=id),
            "ou": ou,
            "id": id    ,
            "message": "Eintrag erflogreich aktualisiert"
        })

    return render(request, "webapplication/update_detail_invest_soll.html", {
        "invest_soll": Detail_Investmittelplan_Soll.objects.all().filter(id=id),
        "ou": ou,
        "id": id
    })

def test(request):
    username = request.user
    if username.groups.filter(name='Admin').exists():
        return render(request, "webapplication/test.html",{
            "unlock": 3
        })
    else:
        return HttpResponseRedirect(reverse("lagerliste"))