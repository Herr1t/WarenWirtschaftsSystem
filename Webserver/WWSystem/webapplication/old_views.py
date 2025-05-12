# def create_lager(request):
#     if group_check(request.user) == '1':
#         return HttpResponseRedirect(reverse("investmittel_soll"))
#     else:
#         if request.method == "POST":
#             x = int(0)
#             y = int(0)
#             c = 0
#             ach = 0
#             list = []
#             dupe = ""
#             fail = ""
#             entrys = BestellListe.objects.values_list('sap_bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung')
#             # Checks if a Bestell_Nr. was selected
#             try:
#                 bnr = BestellListe.objects.get(pk=str(request.POST["bestell_nr"]))
#             except ValueError:
#                 return render(request, "webapplication/create_lager.html", {
#                     "message": "Bitte wähle eine Bestell_Nr. aus",
#                     "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")
#                 })

#             ausgegeben = 0
#             # Appends all entries in the obejct "list"
#             while True:
#                 check = request.POST.get(f"{x}", False)
#                 if check:
#                     list.append(request.POST[f"{x}"])
#                     x = x + 1
#                 else:
#                     x = x + 1
#                     c = c + 1
#                     if c == 50:
#                         break
#             # Assigning the values to their respective variable
#             for __ in entrys:
#                 if str(bnr) in str(entrys[y][0]):
#                     typ = entrys[y][1]
#                     modell = entrys[y][2]
#                     spezifikation = entrys[y][3]
#                     zuweisung = entrys[y][4]
#                 else:
#                     y = y + 1
#             # Creating the new entries in "list" for Lagerliste
#             for _ in list:
#                 inventarnummer = _
#                 try:
#                     lager_count = Achievements.objects.filter(user=request.user).values_list('lager_count')
#                     Lagerliste.objects.create(inventarnummer=inventarnummer, typ=typ, modell=modell, spezifikation=spezifikation, zuweisung=zuweisung, bestell_nr_field=bnr, ausgegeben=ausgegeben)
#                     obj = Lagerliste.objects.get(pk=inventarnummer)
#                     # Checking if creation of entry was succesfull
#                     if obj is None:
#                         fail = fail + inventarnummer + ", "
#                     # Achievement check
#                     if lager_count:
#                         temp = str(lager_count[0]).replace('(', '').replace(',)', '')
#                         if temp == "None":
#                             new = 0
#                             achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 1, 'lager_achievement': 0, 'bestell_count': 0, 'bestell_achievement': 0, 'handout_count': 0, 'handout_achievement': 0, 'rueckgabe_count': 0, 'rueckgabe_achievement': 0})
#                         else:
#                             new = int(str(lager_count[0]).replace('(', '').replace(',)', '')) + 1
#                             achievement_count = Achievements.objects.filter(user=request.user).update(lager_count=new)
#                     else:
#                         new = 0
#                         achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 1, 'lager_achievement': 0, 'bestell_count': 0, 'bestell_achievement': 0, 'handout_count': 0, 'handout_achievement': 0, 'rueckgabe_count': 0, 'rueckgabe_achievement': 0})
#                     # If count 100 for Lagereinträge then Achievement unlock
#                     if new == 50:
#                         ach = 1
#                     if new == 200:
#                         ach = 2
#                     if new == 500:
#                         ach = 3
#                 # Checking if entry already exists
#                 except IntegrityError:
#                     dupe = dupe + inventarnummer + ", "
#                     continue
#                 except ValueError:
#                     return render(request, "webapplication/login.html", {
#                         "message": "Sie sind nicht angemeldet!"
#                     })
#             # Check if achievement unlocked
#             if ach == 1:
#                 achievement_unlock = Achievements.objects.filter(user=request.user).update(lager_achievement=1)
#             if ach == 2:
#                 achievement_unlock = Achievements.objects.filter(user=request.user).update(lager_achievement=2)
#             if ach == 3:
#                 achievement_unlock = Achievements.objects.filter(user=request.user).update(lager_achievement=3)
#             # Output if creation of at least one entry failed
#             if fail:
#                 fail = fail[:-2]
#                 return render(request, "webapplication/create_lager.html", {
#                     "dupe": dupe,
#                     "fail": fail,
#                     "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein"),
#                     "unlock": ach
#                 })
#             # Output if at least one of the entries already existed
#             if dupe:
#                 dupe = dupe[:-2]
#                 return render(request, "webapplication/create_lager.html", {
#                     "dupe": dupe,
#                     "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein"),
#                     "unlock": ach
#                 })
#             return render(request, "webapplication/create_lager.html", {
#                 "message": "Einträge erfolgreich angelegt",
#                 "unlock": ach,
#                 "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")
#             })
#         return render(request, "webapplication/create_lager.html", {
#             "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")
#         })

# def handout_lager(request):
#     if group_check(request.user) == '1':
#         return HttpResponseRedirect(reverse("investmittel_soll"))
#     else:
#         if request.method == "POST":
#             x = 0
#             c = 0
#             ach = 0
#             list = []
#             ausgegeben = 1
#             ausgabe = timezone.now
#             klinik = request.POST["klinik"]
#             herausgeber = request.user
#             dne = ""
#             fail = ""
#             # Appends all entries in the obejct "list"
#             while True:
#                 check = request.POST.get(f"{x}", False)
#                 if check:
#                     list.append(request.POST[f"{x}"])
#                     x = x + 1
#                 else:
#                     x = x + 1
#                     c = c + 1
#                     if c == 50:
#                         break
#             # "Austragung" of the entries in "list"
#             for _ in list:
#                 inventarnummer = str(_)
#                 try:
#                     handout_count = Achievements.objects.filter(user=request.user).values_list('handout_count')
#                     ausgabe_check = str(Lagerliste.objects.values_list('ausgegeben').get(pk=inventarnummer))
#                     # Checks if entry isnt already "ausgegeben"
#                     if ausgabe_check in "('0',)":
#                         ___ = Lagerliste.objects.values_list('bestell_nr_field').get(pk=inventarnummer)
#                         temp = BestellListe.objects.values_list('preis_pro_stück').get(pk=___[0])
#                         ou_id = Ou.objects.values_list('ou_id').filter(ou=klinik)
#                         inv_id = Invest.objects.values_list('id').filter(ou_id=str(ou_id[0]).replace("(", "").replace(",)", "")).filter(typ="Aktiv").filter(jahr=this_year)
#                         __ = Invest.objects.values_list('investmittel_übrig').get(pk=str(inv_id[0]).replace("(", "").replace(",)", ""))
#                         ____ = Invest.objects.values_list('investmittel_verausgabt').get(pk=str(inv_id[0]).replace("(", "").replace(",)", ""))
#                         # Subtracting the "preis_pro_stück" of the entries in "list" from the column "investmittel_übrig_in_euro" of the selected "ou" in Investmittelplan
#                         abzug = __[0] - temp[0]
#                         addition = ____[0] + temp[0]
#                         abrechnung = Invest.objects.update_or_create(id=str(inv_id[0]).replace("(", "").replace(",)", ""), defaults={'investmittel_übrig': abzug})
#                         aufrechnung = Invest.objects.update_or_create(id=str(inv_id[0]).replace("(", "").replace(",)", ""), defaults={'investmittel_verausgabt': addition})
#                         # "Austragung" of the entries in Lagerliste
#                         ausgeben = Lagerliste.objects.update_or_create(inventarnummer=inventarnummer, defaults={'ausgegeben': ausgegeben, 'klinik': klinik, 'ausgabe': ausgabe, 'herausgeber': herausgeber})
#                         if handout_count:
#                             temp = str(handout_count[0]).replace('(', '').replace(',)', '')
#                             if temp == "None":
#                                 new = 0
#                                 achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 0, 'lager_achievement': 0, 'bestell_count': 0, 'bestell_achievement': 0, 'handout_count': 1, 'handout_achievement': 0, 'rueckgabe_count': 0, 'rueckgabe_achievement': 0})
#                             else:
#                                 new = int(str(handout_count[0]).replace('(', '').replace(',)', '')) + 1
#                                 achievement_count = Achievements.objects.filter(user=request.user).update(handout_count=new)
#                         else:
#                             new = 0
#                             achievement_count = Achievements.objects.update_or_create(user=request.user, defaults={'lager_count': 0, 'lager_achievement': 0, 'bestell_count': 0, 'bestell_achievement': 0, 'handout_count': 1, 'handout_achievement': 0, 'rueckgabe_count': 0, 'rueckgabe_achievement': 0})
#                         if new == 50:
#                             ach = 1
#                         if new == 200:
#                             ach = 2
#                         if new == 500:
#                             ach = 3
#                     # Output if entry is already "ausgetragen"
#                     else:
#                         fail = fail + inventarnummer + ", "
#                         continue 
#                 # If entry does not exist in Lagerliste then it gets appended to the variable "dne"
#                 except ObjectDoesNotExist:
#                     dne = dne + inventarnummer + ", "
#                     continue
#                 # except ValueError:
#                 #     return render(request, "webapplication/login.html", {
#                 #         "message": "Sie sind nicht angemeldet!"
#                 #     })
#             if ach == 1:
#                 achievement_unlock = Achievements.objects.filter(user=request.user).update(handout_achievement=1)
#             if ach == 2:
#                 achievement_unlock = Achievements.objects.filter(user=request.user).update(handout_achievement=2)
#             if ach == 3:
#                 achievement_unlock = Achievements.objects.filter(user=request.user).update(handout_achievement=3)
#             # If there is at least one entry in "fail" then is uses this output
#             if fail:
#                 fail = fail[:-2]
#                 return render(request, "webapplication/handout_lager.html", {
#                     "dne": dne,
#                     "fail": fail,
#                     "unlock": ach
#                 })
#             # If there is at least one entry in "dne" then it uses this output
#             if dne:
#                 dne = dne[:-2]
#                 return render(request, "webapplication/handout_lager.html", {
#                     "dne": dne,
#                     "unlock": ach
#                 })
#             # Checks if column "investmittel_übrig_in_euro" from Investmittelplan is below 0
#             check = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').get(klinik_ou=klinik)
#             if float(check[0]) < 0:
#                     return render(request, "webapplication/handout_lager.html", {
#                     "message": "Einträge erfolgreich ausgetragen",
#                     "alarm": klinik,
#                     "geld": float(check[0]),
#                     "unlock": ach
#                 })
#             else:
#                 return render(request, "webapplication/handout_lager.html", {
#                     "message": "Einträge erfolgreich ausgetragen",
#                     "unlock": ach
#                 })
#         return render(request, "webapplication/handout_lager.html")

# def upload(request):
#     if request.method == "POST":
#         conf = 0
#         form = UploadForm(request.POST, request.FILES)
#         test = []
#         y = 0
#         z = 1
#         this_year = str(int(datetime.date.today().year))
#         wrong = ""
#         if form.is_valid():
#             if ".csv" in request.FILES["upload"].name:
#                 er = Upload.objects.values_list('titel')
#                 x = 0
#                 for _ in er:
#                     if str("investmittelupload") in str(_[x]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""):
#                         conf = 1
#                         x = x + 1
#                 if conf != 1:
#                     Upload.objects.create(file = request.FILES["upload"], titel = "investmittelupload")
#                 else:
#                     Upload.objects.filter(titel="investmittelupload").delete()
#                     Upload.objects.create(file = request.FILES["upload"], titel = "investmittelupload")
#                 up = Upload.objects.filter(titel = "investmittelupload").values_list("file")
#                 loc = str(up[0]).replace("'", "").replace("(", "").replace(")", "").replace(",", "")
#                 with open(f"/home/adminukd/WarenWirtschaftsSystem/Webserver/WWSystem/media/{loc}") as csv_file:
#                 #with open(f"/Users/voigttim/Programming/WarenWirtschaftsSystem/Webserver/WWSystem/media/{loc}") as csv_file:
#                     csv_reader = csv.reader(csv_file, delimiter=',')
#                     x = 0
#                     for row in csv_reader:
#                         test.append(row)
#                 ous = Investmittelplan.objects.values_list("klinik_ou")
#                 if "OU" in test[0][0] and "Investmittel" in test[0][1]:
#                     pass
#                 else:
#                     return render(request, "webapplication/upload.html", {
#                         "alert": "Im Header der CSV Datei müssen im ersten Feld 'OU' enthalten sein und im zweiten Feld 'Investmittel' enthalten sein. Bitte auch nicht mehr als diese zwei Spalten!"
#                     })
#                 for _ in ous:
#                     if str(ous[y]).replace("'", "").replace("(", "").replace(")", "").replace(",", "") == test[z][0]:
#                         Investmittelplan.objects.filter(klinik_ou = str(ous[y]).replace("'", "").replace("(", "").replace(")", "").replace(",", "")).update(investmittel_jahresanfang_in_euro=test[z][1], investmittel_übrig_in_euro=test[z][1])
#                         austragung_la = Lagerliste.objects.values_list('bestell_nr_field').filter(klinik=int(str(ous[y]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))).filter(ausgabe__year=this_year)
#                         for __ in austragung_la:
#                             austragung_be = BestellListe.objects.values_list('preis_pro_stück').get(pk=str(__[0]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
#                             austragung_in = Investmittelplan.objects.values_list('investmittel_übrig_in_euro').get(pk=int(str(ous[y]).replace("'", "").replace("(", "").replace(")", "").replace(",", "")))
#                             abzug = austragung_in[0] - austragung_be[0]
#                             abrechnung = Investmittelplan.objects.update_or_create(klinik_ou=str(ous[y]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""), defaults={'investmittel_übrig_in_euro': abzug})
#                         z = z + 1
#                         y = y + 1
#                     else:
#                         Investmittelplan.objects.filter(klinik_ou = str(ous[y]).replace("'", "").replace("(", "").replace(")", "").replace(",", "")).update(investmittel_jahresanfang_in_euro="0", investmittel_übrig_in_euro="0")
#                         y = y + 1
#                 return render(request, "webapplication/upload.html", {
#                     "message": "CSV erfolgreich importiert!"
#                 })
#             else:
#                 return render(request, "webapplication/upload.html", {
#                     "alert": "Es muss sich um eine .csv Datei handeln"
#                 })
#     else:
#         form = UploadForm()
#         return render(request, "webapplication/upload.html", {
#             "form": form
#         })

# def investmittelplanung(request):
#     if group_check(request.user) == '1':
#         return HttpResponseRedirect(reverse("investmittel"))
#     elif reset_group_check(request.user) == '0':
#         return HttpResponseRedirect(reverse("investmittel"))
#     else:
#         Jahre = Invest.objects.values('jahr').distinct()
#         if request.method == "POST":
#             ous = Invest.objects.values_list("ou_id__ou").filter(typ="Planung").exclude(ou_id__ou=1).order_by("ou_id__ou")
#             x = 1
#             for ou in ous:
#                 ou = str(ou).replace("(", "").replace(",)", "")
#                 input = request.POST[f"{ou}"]
#                 jahr = request.POST["jahr"]
            
#             return render(request, "webapplication/investmittelplanung.html", {
#                 "rows": Invest.objects.values('ou_id__ou').filter(typ="Aktiv").exclude(ou_id__ou=1).distinct(),
#                 "Jahre": Jahre,
#                 "message": "test"
#             })
#         else:
#             return render(request, "webapplication/investmittelplanung.html", {
#                 "rows": Invest.objects.values('ou_id__ou').filter(typ="Aktiv").exclude(ou_id__ou=1).distinct(),
#                 "Jahre": Jahre
#             })
