from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, connection
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Q
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.urls.exceptions import NoReverseMatch
from django.contrib.auth.models import Group
import csv, datetime
from django.http import HttpResponse, JsonResponse
from webapplication.external_functions.getmethod import *
from webapplication.external_functions.create_lager import *
from django.db.models import Count


from .models import Lagerliste, BestellListe, Investmittelplan, User, Lagerliste_ohne_Invest, Detail_Investmittelplan_Soll, Achievements, Download, Invest, Ou
#from .forms import UploadForm

this_year = str(int(datetime.date.today().year))

def group_check(user):
    username = user
    if username.groups.filter(name='Klinik-Admin').exists():
        return("1")
    else:
        return("0")
    
def reset_group_check(user):
    username=user
    if username.groups.filter(name='Admin').exists():
        return("1")
    else:
        return("0")

# View Function if nothing of the below is loaded
def index(request):
    return render(request, "webapplication/login.html")

# View Function that processes the login of users
# View function for handling user login
def login_view(request):
    # Check if the request is a POST request (i.e., form submission)
    if request.method == "POST":
        # Get the username and password from the POST data
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate the user using Django's authenticate function
        user = authenticate(request, username=username, password=password)

        # If authentication fails (user is None), show an error message
        if user is None:
            return render(request, "webapplication/login.html", {
                "message": "Ungültiger Nutzername und/oder Passwort."  # Invalid username or password
            })

        # Define the allowed user groups for this application
        GROUP_KLINIK_ADMIN = 'Klinik-Admin'
        GROUP_ADMIN = 'Admin'
        GROUP_SERVICEDESK = 'Servicedesk'

        # Get the list of groups the user is a member of
        user_groups = user.groups.values_list('name', flat=True)

        # Set of allowed groups
        allowed_groups = {GROUP_KLINIK_ADMIN, GROUP_ADMIN, GROUP_SERVICEDESK}

        # Check if the user belongs to any of the allowed groups
        if not any(group in allowed_groups for group in user_groups):
            # If not, add the user to the Servicedesk group (default group for unclassified users)
            servicedesk_group, _ = Group.objects.get_or_create(name=GROUP_SERVICEDESK)
            servicedesk_group.user_set.add(user)

        # If the user is in the Servicedesk group, set them as staff
        if GROUP_SERVICEDESK in user.groups.values_list('name', flat=True):
            User.objects.filter(username=username).update(is_staff=True)

        # Log the user in
        login(request, user)

        # Redirect to appropriate page based on user group
        if GROUP_KLINIK_ADMIN in user.groups.values_list('name', flat=True):
            return redirect(reverse("investmittel_soll"))
        return redirect(reverse("lagerliste"))

    # If the request method is not POST, render the login page
    return render(request, "webapplication/login.html")


# View function for handling user logout
def logout_view(request):
    # Log out the current user and redirect to the index page
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# View function for handling the registration and creation of new users
def register(request):
    # Check if the request is a POST request (form submission)
    if request.method == "POST":
        # Get the username, password, and confirmation password from the POST data
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")

        # Validate if password and confirmation password match
        if password != confirmation:
            return render(request, "webapplication/register.html", {
                "message": "Passwörter müssen sich gleichen."  # Passwords must match
            })

        try:
            # Create a new user (inactive initially, requiring admin approval)
            user = User.objects.create_user(username=username, password=password)
            user.is_active = False  # Set user as inactive
            user.save()

            # Assign the user to the 'Klinik-Admin' group (this is the default group)
            klinik_admin_group, _ = Group.objects.get_or_create(name='Klinik-Admin')
            klinik_admin_group.user_set.add(user)

        except IntegrityError:
            # If username already exists, return an error message
            return render(request, "webapplication/register.html", {
                "message": "Nutzername bereits vergeben."  # Username already taken
            })

        # If registration is successful, show a confirmation message
        return render(request, "webapplication/register.html", {
            "confirm": "1"  # Show confirmation that registration was successful
        })

    # If the request method is not POST, render the registration page
    return render(request, "webapplication/register.html")


# View function for handling password reset functionality
def pw_reset(request):
    # Check if the user is in the reset group (group '1') before allowing password reset
    if reset_group_check(request.user) == '1':
        # If the request is a POST request (form submission)
        if request.method == "POST":
            # Get the username, new password, and confirmation password from POST data
            uname = request.POST["username"]
            new_pw = request.POST["new_password"]
            confirm_pw = request.POST["confirm_password"]

            # Check if the new password and confirmation password match
            if new_pw != confirm_pw:
                return render(request, "webapplication/pw_reset.html", {
                    "message": "Passwörter müssen sich gleichen."  # Passwords must match
                })
            else:
                try:
                    # Attempt to find the user by username
                    u = User.objects.get(username=uname)
                    # Set the new password and save the user
                    u.set_password(new_pw)
                    u.save()
                    # Show confirmation that password reset was successful
                    return render(request, "webapplication/pw_reset.html", {
                        "confirm": "1"  # Show success message
                    })
                except ObjectDoesNotExist:
                    # If user does not exist, show an error message
                    return render(request, "webapplication/pw_reset.html", {
                        "message": "Nutzername exisitert nicht!"  # Username does not exist
                    })
        else:
            # If the request is not a POST request, just render the password reset page
            return render(request, "webapplication/pw_reset.html")
    else:
        # If the user is not authorized to reset passwords, show a different message
        return render(request, "webapplication/pw_reset.html", {
            "check": "1"  # Show that the user does not have permission for this action
        })
        
def pw_reset_msg(request):
    return render(request, "webapplication/pw_reset_msg.html")

# View Function that represents the content of the Lagerliste
def lager(request):
    # Check if the user is part of group '1' and redirect to a different page if true
    if group_check(request.user) == '1':
        return redirect(reverse("investmittel_soll"))

    # Retrieve all download files available to the user
    files = Download.objects.all()
    type = "lager"  # Set the type for the current view to "lager"

    # Normalize 'None' zuweisungen (assignments) to "Keine Zuweisung" (No Assignment)
    # This ensures that if there are any items without an assigned 'zuweisung', 
    # we update those records with a default value "Keine Zuweisung"
    for zuweisung, inventarnummer in Lagerliste.objects.values_list('zuweisung', 'inventarnummer'):
        if zuweisung is None:
            Lagerliste.objects.update_or_create(
                inventarnummer=inventarnummer,
                defaults={'zuweisung': "Keine Zuweisung"}  # Set default zuweisung to "Keine Zuweisung"
            )

    # Retrieve all Lagerliste entries that are not marked as "ausgegeben" (issued) 
    # and get their order number (bestell_nr_field), type (typ), model (modell),
    # specification (spezifikation), and assignment (zuweisung).
    raw_lager = Lagerliste.objects.exclude(ausgegeben="1").values(
        'bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung'
    ).annotate(Menge=Count('bestell_nr_field'))  # Add a "Menge" (count) for each order number

    # Retrieve a separate list of Lagerliste entries to count the number of items
    # for each unique bestell_nr_field and typ.
    nr_list = Lagerliste.objects.exclude(ausgegeben="1").values_list(
        'bestell_nr_field', 'typ'
    ).annotate(Menge=Count('bestell_nr_field'))

    # Create a list of raw Lagerliste data (lagerliste) to work with and a list to hold enriched data
    lagerliste = list(raw_lager)
    enriched_data = []

    # Iterate over the nr_list to enrich the Lagerliste data with additional information
    for index, (bestell_nr, typ, menge) in enumerate(nr_list):
        pk = str(bestell_nr).strip("(),")  # Clean the primary key value

        # Fetch associated data from BestellListe (purchase order list) for each bestell_nr
        bestell_info = BestellListe.objects.values(
            'menge', 'geliefert_anzahl'  # Retrieve quantity and delivered quantity
        ).filter(pk=pk).first()  # Use the first matching result (there should be only one)

        delivered = bestell_info.get('geliefert_anzahl') if bestell_info else 0  # Handle case where no data exists
        total = bestell_info.get('menge') if bestell_info else 0  # Total quantity from BestellListe

        # Count how many items with this bestell_nr_field have been issued (ausgegeben="1")
        issued_count = Lagerliste.objects.filter(
            bestell_nr_field=bestell_nr,
            ausgegeben="1"
        ).count()

        # Append enriched data to the list
        enriched_data.append({
            'menge': total,  # Total quantity from BestellListe
            'geliefert_anzahl': delivered or total,  # Delivered quantity or total if none delivered
            'ausgegeben': issued_count  # Count of issued items
        })

        # Update the raw lager list with the enriched data for this entry
        lagerliste[index].update(enriched_data[index])

    # Function to count matching items for a specific type and partial specification
    # This helps in counting items for specific devices like monitors, notebooks, etc.
    def count_matching(queryset, typ_value, partial_spec):
        # Sum up the 'Menge' for matching typ and partial specification
        return sum(
            row['Menge'] for row in queryset
            if row['typ'] == typ_value and partial_spec.lower() in row['spezifikation'].lower()
        )

    # Retrieve a summary of Lagerliste data with counts per item type and specification
    mengen = Lagerliste.objects.values(
        'bestell_nr_field', 'typ', 'spezifikation', 'modell'
    ).annotate(Menge=Count("bestell_nr_field")).exclude(ausgegeben="1")

    # Create a dictionary of device counts by type and specification
    # Each key represents a device type, and the value is the total number of that device
    device_counts = {
        'monitor24': count_matching(mengen, 'Monitor', '24 Zoll'),
        'monitor27': count_matching(mengen, 'Monitor', '27 Zoll'),
        'monitor32': count_matching(mengen, 'Monitor', '32 Zoll'),
        'notebook13': count_matching(mengen, 'Notebook', '13 Zoll'),
        'notebook14': count_matching(mengen, 'Notebook', '14 Zoll'),
        'notebook15': count_matching(mengen, 'Notebook', '15 Zoll'),
        'pcsff': count_matching(mengen, 'Desktop-PC', 'Small Form Factor'),
        'pcmff': count_matching(mengen, 'Desktop-PC', 'Micro-Desktop-PC') + count_matching(mengen, 'Desktop-PC', 'Micro'),
        'drucker': sum(item['Menge'] for item in mengen if item['typ'] == 'Drucker'),
        'scanner': sum(item['Menge'] for item in mengen if item['typ'] == 'Scanner'),
        'dock': sum(item['Menge'] for item in mengen if item['typ'] == 'Dockingstation'),
        'dik': sum(item['Menge'] for item in mengen if item['typ'] == 'Diktiergerät'),
        'trans': sum(item['Menge'] for item in mengen if item['typ'] == 'Transkription'),
    }

    # Return the rendered response, passing the enriched data and device counts
    return render(request, "webapplication/lager.html", {
        "lagerliste": lagerliste,  # Pass the enriched Lagerliste data
        **device_counts,  # Expand device counts into the context dictionary
        "files": files,  # Pass all available files for download
        "typ": type  # Pass the type (lager) for current view
    })

# View Function that represents the detailed list of items for a specific Bestell_Nr. inside the Lagerliste
def detail_lager(request, bestell_nr):
    # Check if the user is in the restricted group; redirect if so
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        # Store the provided BestellNr (order number) in 'nr'
        nr = bestell_nr
        
        # Query Lagerliste for items matching the provided BestellNr
        bestell = Lagerliste.objects.filter(bestell_nr_field=nr)
        
        # Render the 'detail_lager.html' template and pass the queried items and BestellNr to the template
        return render(request, "webapplication/detail_lager.html", {
            "detail_lagerliste": bestell,  # List of items for the specific BestellNr
            "bestell_nr": bestell_nr      # The BestellNr itself for context in the template
        })

# View Function that handles the creation of new entries for the Lagerliste
def create_lager(request):
    # Check if the user is in the restricted group; redirect if so
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))

    # Check if the request method is POST (indicating form submission)
    if request.method == "POST":
        # Attempt to get the BestellNr (order number) from the request
        bnr = get_bestell_nr(request)
        
        # If no BestellNr is provided or it's invalid, return an error message and render the form again
        if not bnr:
            return render(request, "webapplication/create_lager.html", {
                "message": "Bitte wähle eine Bestell_Nr. aus",  # Error message for missing BestellNr
                "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")  # Provide valid BestellNr options
            })

        # Extract the selected items from the request (the items to be created in Lagerliste)
        selected_items = get_selected_items(request)
        
        # If no items were selected, return an error message
        if not selected_items:
            return render(request, "webapplication/create_lager.html", {
                "message": "Bitte wähle mindestens ein Element aus.",  # Error message for no selected items
                "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")  # Provide valid BestellNr options
            })

        # Fetch the details (type, model, specification, and assignment) for the given BestellNr
        typ, modell, spezifikation, zuweisung = get_bestell_details(bnr)

        # Process the selected items and handle the creation of Lagerliste entries
        return process_selected_items(request, selected_items, typ, modell, spezifikation, zuweisung, bnr)

    # If the method is not POST, simply render the create page with available BestellNr options
    return render(request, "webapplication/create_lager.html", {
        "bestell_nr": BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")  # Provide valid BestellNr options
    })

# View Function that handles the "austragung" of entries from the Lagerliste
def handout_lager(request):
    # Redirect users in a restricted group to another view
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))

    # Handle POST request (form submission)
    if request.method == "POST":
        # Initialize variables for tracking user achievements, errors, and handout operations
        handout_count = 0                # Number of items handed out by user
        achieved_level = 0               # Achievement level unlocked (50, 200, 500 items)
        dne_entries = []                 # Items not found in Lagerliste (Does Not Exist)
        fail_entries = []                # Items that were already marked as 'ausgegeben'
        items_to_process = []            # Valid selected inventory numbers to process
        ausgegeben = 1                   # Status flag to mark item as handed out
        ausgabe_time = timezone.now()    # Timestamp of the handout
        clinic = request.POST["klinik"]  # Target clinic receiving the items
        issuer = request.user            # Logged-in user performing the handout
        annahme = request.POST["annahme"]

        # Collect up to 50 selected items from the form data
        index = 0
        while True:
            item = request.POST.get(str(index), False)
            if item:
                items_to_process.append(item)  # Add selected item to processing list
                index += 1
            else:
                index += 1
                if index == 50:  # Limit processing to 50 items
                    break

        # Process each selected inventory number
        for item in items_to_process:
            try:
                inventory_number = str(item)  # Ensure it's a string for DB lookup

                # Only proceed if item is not already marked as issued
                if Lagerliste.objects.filter(pk=inventory_number, ausgegeben="0").exists():
                    # Retrieve related BestellNr for pricing and budgeting updates
                    bestell_nr = Lagerliste.objects.values_list('bestell_nr_field', flat=True).get(pk=inventory_number)
                    price_per_item = BestellListe.objects.values_list('preis_pro_stück', flat=True).get(pk=bestell_nr)

                    # Retrieve target clinic's ID for filtering budget entries
                    clinic_ou_id = Ou.objects.values_list('ou_id', flat=True).filter(ou=clinic).first()
                    
                    # Get the current active investment plan for the clinic this year
                    invest = Invest.objects.filter(
                        ou_id=clinic_ou_id, typ="Aktiv", jahr=this_year
                    ).first()
                    
                    # Get current budget and spent values
                    remaining_funds = invest.investmittel_übrig
                    spent_funds = invest.investmittel_verausgabt

                    # Calculate updated values
                    new_remaining_funds = remaining_funds - price_per_item
                    new_spent_funds = spent_funds + price_per_item

                    # Update the investment entry with new financial values
                    Invest.objects.filter(id=invest.id).update(
                        investmittel_übrig=new_remaining_funds,
                        investmittel_verausgabt=new_spent_funds
                    )

                    # Mark the inventory item as handed out in Lagerliste
                    Lagerliste.objects.filter(pk=inventory_number).update(
                        ausgegeben=ausgegeben,
                        klinik=clinic,
                        ausgabe=ausgabe_time,
                        herausgeber=issuer,
                        ausgegeben_an=annahme
                    )

                    # Retrieve current handout count for the user (if exists)
                    handout_count = Achievements.objects.filter(
                        user=issuer
                    ).values_list('handout_count', flat=True).first() or 0

                    # Increment handout count
                    new_handout_count = handout_count + 1

                    # Create or update the achievement record with new count
                    Achievements.objects.update_or_create(
                        user=issuer,
                        defaults={'handout_count': new_handout_count}
                    )

                    # Check for achievement unlocks at thresholds
                    if new_handout_count == 50:
                        achieved_level = 1
                    elif new_handout_count == 200:
                        achieved_level = 2
                    elif new_handout_count == 500:
                        achieved_level = 3

                else:
                    # Inventory item is already handed out; add to failure list
                    fail_entries.append(inventory_number)

            except ObjectDoesNotExist:
                # Inventory item doesn't exist in database; add to dne list
                dne_entries.append(inventory_number)

        # Update user's achievement level if unlocked
        if achieved_level > 0:
            Achievements.objects.filter(user=issuer).update(handout_achievement=achieved_level)

        # Display result page with failure message if any items were already issued
        if fail_entries:
            return render(request, "webapplication/handout_lager.html", {
                "dne": ", ".join(dne_entries),      # Items not found
                "fail": ", ".join(fail_entries),    # Items already issued
                "unlock": achieved_level            # Achievement level unlocked
            })

        # Display result page if any items did not exist
        if dne_entries:
            return render(request, "webapplication/handout_lager.html", {
                "dne": ", ".join(dne_entries),
                "unlock": achieved_level
            })

        # Check if the clinic's budget went below 0 after handout
        remaining_budget = Investmittelplan.objects.values_list(
            'investmittel_übrig_in_euro', flat=True
        ).filter(klinik_ou=clinic).first()

        # Display warning if overspending occurred
        if float(remaining_budget) < 0:
            return render(request, "webapplication/handout_lager.html", {
                "message": "Einträge erfolgreich ausgetragen",  # Success message
                "alarm": clinic,                                # Clinic name
                "geld": float(remaining_budget),                # Remaining budget
                "unlock": achieved_level                        # Achievement unlocked
            })

        # Generic success message if everything went well
        return render(request, "webapplication/handout_lager.html", {
            "message": "Einträge erfolgreich ausgetragen",
            "unlock": achieved_level
        })

    # For GET request: render the initial handout form page
    return render(request, "webapplication/handout_lager.html")

# View function to handle the bulk "handout" (Austragung) of inventory items from the warehouse list (Lagerliste)
# based on a common order number (bestell_nr)
def handout_lager_all(request, bestell_nr):
    # Step 1: Authorization check — if user group is '1', redirect to another page
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))

    # Step 2: Handle form submission (POST method)
    if request.method == 'POST':
        # Initialize tracking variables
        achievement_level = 0  # Used to determine whether an achievement milestone is reached
        clinic = request.POST["klinik"]  # Clinic name from the form submission
        user = request.user  # Currently logged-in user
        issue_time = timezone.now()  # Timestamp of when items are handed out
        issued_flag = 1  # Value indicating that an item is now "issued"
        annahme = request.POST["annahme"]

        # Lists to collect inventory numbers that failed for specific reasons
        dne_items = []     # Items that "Do Not Exist" in the Lagerliste table
        failed_items = []  # Items already marked as "ausgegeben" (handed out)

        # Step 3: Fetch all unissued inventory items (inventarnummern) for the given Bestellnummer
        inventory_numbers = Lagerliste.objects.filter(
            bestell_nr_field=bestell_nr,
            ausgegeben=0  # Only include items not yet handed out
        ).values_list('inventarnummer', flat=True)

        # Step 4: Iterate only over unissued inventory numbers
        for inv_number in inventory_numbers:
            try:
                # Step 4a: Check if the item has already been handed out
                is_issued = Lagerliste.objects.get(pk=inv_number).ausgegeben
                if str(is_issued) != '0':
                    # Skip and record items already handed out
                    failed_items.append(str(inv_number))
                    continue

                # Step 4b: Retrieve the price of the item from the BestellListe table
                bestell_entry = Lagerliste.objects.get(pk=inv_number).bestell_nr_field
                price = BestellListe.objects.get(pk=bestell_entry).preis_pro_stück

                # Step 4c: Get the organizational unit ID (ou_id) for the clinic
                ou_id = Ou.objects.filter(ou=clinic).values_list('ou_id', flat=True).first()

                # Step 4d: Retrieve the active investment entry for this clinic for the current year
                invest = Invest.objects.filter(
                    ou_id=ou_id, typ="Aktiv", jahr=this_year
                ).first()

                # Step 4e: Update budget values — subtract item price from available funds, add to spent
                invest.investmittel_übrig -= price
                invest.investmittel_verausgabt += price
                invest.save()

                # Step 4f: Mark the item in Lagerliste as issued (ausgegeben), and record metadata
                Lagerliste.objects.filter(pk=inv_number).update(
                    ausgegeben=issued_flag,      # Set item as issued
                    klinik=clinic,               # Record issuing clinic
                    ausgabe=issue_time,          # Timestamp of issue
                    herausgeber=user,             # User who issued the item
                    ausgegeben_an=annahme
                )

                # Step 4g: Track achievements by updating handout counts
                handout_record, created = Achievements.objects.get_or_create(user=user)

                if created:
                    # If the user has no record yet, initialize all achievement fields
                    handout_record.lager_count = 0
                    handout_record.lager_achievement = 0
                    handout_record.bestell_count = 0
                    handout_record.bestell_achievement = 0
                    handout_record.handout_count = 1
                    handout_record.handout_achievement = 0
                    handout_record.rueckgabe_count = 0
                    handout_record.rueckgabe_achievement = 0
                else:
                    # Otherwise, increment the count for handouts
                    handout_record.handout_count += 1

                handout_record.save()  # Save the updated achievement record

                # Step 4h: Unlock achievement levels at defined thresholds
                if handout_record.handout_count == 50:
                    achievement_level = 1
                elif handout_record.handout_count == 200:
                    achievement_level = 2
                elif handout_record.handout_count == 500:
                    achievement_level = 3

                # Update the achievement level in the record if any was reached
                if achievement_level:
                    handout_record.handout_achievement = achievement_level
                    handout_record.save()

            except Lagerliste.DoesNotExist:
                # Case: Item does not exist in Lagerliste table
                dne_items.append(str(inv_number))
                continue
            except (BestellListe.DoesNotExist, Invest.DoesNotExist, Ou.DoesNotExist):
                # Case: Required related data is missing — treat as non-existent
                dne_items.append(str(inv_number))
                continue
            except ValueError:
                # Case: Request user is somehow invalid (e.g., not authenticated)
                return render(request, "webapplication/login.html", {
                    "message": "Sie sind nicht angemeldet!"  # Not logged in
                })

        # Step 5: Handle any failures (either already issued or missing items)
        if failed_items:
            # Remove trailing comma and return result with error message
            return render(request, "webapplication/handout_lager_all.html", {
                "bestell_nr": bestell_nr,
                "dne": ", ".join(dne_items),   # Items not found
                "fail": ", ".join(failed_items),  # Already issued items
                "unlock": achievement_level     # Achievement unlock status
            })

        if dne_items:
            return render(request, "webapplication/handout_lager_all.html", {
                "bestell_nr": bestell_nr,
                "dne": ", ".join(dne_items),
                "unlock": achievement_level
            })

        # Step 6: Check for budget overspending
        remaining_funds = Investmittelplan.objects.filter(
            klinik_ou=clinic
        ).values_list('investmittel_übrig_in_euro', flat=True).first()

        if remaining_funds is not None and float(remaining_funds) < 0:
            # Warn user about overspending from investment budget
            return render(request, "webapplication/handout_lager_all.html", {
                "bestell_nr": bestell_nr,
                "message": "Einträge erfolgreich ausgetragen",  # Success message
                "alarm": clinic,
                "geld": float(remaining_funds),  # Remaining budget (negative)
                "unlock": achievement_level
            })

        # Step 7: Default case — render success message
        return render(request, "webapplication/handout_lager_all.html", {
            "bestell_nr": bestell_nr,
            "message": "Einträge erfolgreich ausgetragen",
            "unlock": achievement_level
        })

    # Step 8: Render initial view for GET requests (form loading)
    return render(request, "webapplication/handout_lager_all.html", {
        "bestell_nr": bestell_nr
    })

# View Function that handles the "Rückgabe" of already "ausgegebenen" entries in Lagerliste
def rückgabe(request):
    # Redirects users with permission level '1' away from this view
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))

    if request.method == 'POST':
        index = 0  # Iteration counter to collect submitted items
        empty_count = 0  # Counter for blank fields to limit unnecessary iterations
        achievement_level = 0  # Achievement unlock level
        submitted_items = []  # List to collect all submitted Inventarnummern
        dne_items = []  # Inventarnummern not found in database
        already_returned = []  # Inventarnummern that were not issued

        # Status flags for Rückgabe (return)
        ausgegeben = 0  # Marking item as 'not issued'
        herausgeber_reset = None
        ausgabe_reset = None
        klinik_reset = None

        # Loop to extract up to 50 entries from POST data
        while True:
            value = request.POST.get(str(index), False)
            if value:
                submitted_items.append(value)
                empty_count = 0  # Reset empty streak if value found
            else:
                empty_count += 1
                if empty_count == 50:  # Stop if 50 consecutive empty values
                    break
            index += 1

        # Process each Inventarnummer
        # Iterate through each submitted inventory number
        for inventarnummer in submitted_items:
            try:
                # Attempt to retrieve the Lagerliste entry (inventory item) by its primary key (inventory number)
                item = Lagerliste.objects.get(pk=inventarnummer)

                # Convert 'ausgegeben' to an integer for reliable comparison
                # If the item is not currently marked as issued (ausgegeben == 1), then it cannot be returned
                if int(item.ausgegeben) != 1:
                    # Append the inventory number to the list of items that are already returned
                    already_returned.append(inventarnummer)
                    continue  # Skip to the next item in the loop

                # Retrieve the related order number from the Lagerliste item
                bestell_nr = item.bestell_nr_field

                # Retrieve the unit price of the item from the order list using the bestell_nr
                preis_pro_stueck = BestellListe.objects.get(pk=bestell_nr).preis_pro_stück

                # Retrieve the organizational unit (OU) where the item was issued
                klinik_ou = item.klinik

                # Get the OU ID from the OU table using the clinic short name (e.g., "CHM", "RAD", etc.)
                ou_id = Ou.objects.get(ou=klinik_ou).ou_id

                # Retrieve the current year's active investment entry for the specific OU
                invest_entry = Invest.objects.get(
                    ou_id=ou_id,
                    typ="Aktiv",       # We only deal with active budget entries
                    jahr=this_year     # Only the current year is relevant
                )

                # Add the unit price back to the remaining budget (investmittel_übrig),
                # because the item has been returned and is no longer counted as spent
                invest_entry.investmittel_übrig += preis_pro_stueck

                # Subtract the unit price from the amount already spent (investmittel_verausgabt)
                invest_entry.investmittel_verausgabt -= preis_pro_stueck

                # Save the updated financial records
                invest_entry.save()

                # Update the Lagerliste item to reflect it is no longer issued
                item.ausgegeben = 0                 # Mark as not issued
                item.herausgeber = None             # Clear the user who issued it
                item.klinik = None                  # Clear the clinic OU association
                item.ausgabe = None                 # Clear the issue date
                item.save()                         # Persist the changes to the database

                # Update the user’s achievements for returning items
                # Either retrieve the existing record or create a new one
                achievement_record, _ = Achievements.objects.get_or_create(user=request.user)

                # If the return count is None (never set), initialize it
                if achievement_record.rueckgabe_count is None:
                    achievement_record.rueckgabe_count = 1
                else:
                    # Otherwise, increment the return counter
                    achievement_record.rueckgabe_count += 1

                # Determine the achievement level based on the return count
                if achievement_record.rueckgabe_count == 10:
                    achievement_level = 1
                elif achievement_record.rueckgabe_count == 50:
                    achievement_level = 2
                elif achievement_record.rueckgabe_count == 150:
                    achievement_level = 3
                else:
                    achievement_level = achievement_record.rueckgabe_achievement or 0  # Default or existing level

                # Update the user's achievement level
                achievement_record.rueckgabe_achievement = achievement_level

                # Save the updated achievement record
                achievement_record.save()

            # If the inventory number doesn't exist in the Lagerliste, add it to the "does not exist" list
            except Lagerliste.DoesNotExist:
                dne_items.append(inventarnummer)
                continue

            # If the user is not properly logged in or a value error occurs, redirect them to login
            except ValueError:
                return render(request, "webapplication/login.html", {
                    "message": "Sie sind nicht angemeldet!"
                })

        # Prepare output based on errors or success
        context = {
            "unlock": achievement_level
        }

        if already_returned:
            context["fail"] = ", ".join(already_returned)

        if dne_items:
            context["dne"] = ", ".join(dne_items)

        if not already_returned and not dne_items:
            context["message"] = "Geräte erfolgreich zurückgegeben"

        return render(request, "webapplication/rückgabe.html", context)

    # For GET request, show empty form
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

def create_lager_ohne(request):
    nr = BestellListe.objects.values('sap_bestell_nr_field').exclude(investmittel="Ja").exclude(geliefert=1)
    
    if request.method == "POST":
        bestell_nr = request.POST["bestell_nr"]
        bestellung = BestellListe.objects.values_list("menge", "typ", "modell", "spezifikation", "zuweisung").filter(sap_bestell_nr_field=bestell_nr)
        menge = str(bestellung[0][0]).replace("(", "").replace(",)", "")
        typ = str(bestellung[0][1]).replace("(", "").replace(",)", "")
        modell = str(bestellung[0][2]).replace("(", "").replace(",)", "")
        spezifikation = str(bestellung[0][3]).replace("(", "").replace(",)", "")
        zuweisung = str(bestellung[0][4]).replace("(", "").replace(",)", "")
        bestell_nr_field = BestellListe.objects.get(pk=bestell_nr)
        i = 0
        
        while i < int(menge):
            Lagerliste_ohne_Invest.objects.create(typ=typ, modell=modell, spezifikation=spezifikation, zuweisung=zuweisung, bestell_nr_field=bestell_nr_field, ausgegeben=0)
            i = i + 1
        bestellung = BestellListe.objects.update_or_create(sap_bestell_nr_field=bestell_nr, defaults={'geliefert': 1})
        
        return render(request, "webapplication/create_lager_ohne.html", {
            "bestell_nr": nr,
            "message": "Einträge erfolgreich erstellt!"
        })
    else:
        return render(request, "webapplication/create_lager_ohne.html", {
            "bestell_nr": nr
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
        typ = "bestellliste"

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
            "files": files,
            "typ": typ
        })

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
        files = Download.objects.all()
        nr = bestell_nr
        if request.method == "POST":
            items = BestellListe.objects.values_list('sap_bestell_nr_field', 'modell', 'typ', 'menge', 'preis_pro_stück', 'spezifikation', 'geliefert_anzahl', 'zuweisung').get(pk=nr)
            sap_bestell_nr_field = request.POST["sap_bestell_nr_field"] or items[0]
            modell = request.POST["modell"] or items[1]
            typ = request.POST["typ"] or items[2]
            menge = request.POST["menge"] or items[3]
            preis_pro_stück = str(request.POST["preis_pro_stück"]).replace(",", ".") or items[4]
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
                    "unlock": ach,
                    "files": files,
                    "typ": "bestellliste"
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

def some_view(request):
    zeile = ""
    jahr = 2026
    ous = Ou.objects.values_list('ou_id', 'ou').distinct()
    path = "/media/daten/Invest/"
    with open(f'{path}Investplaung_2026_Desktop.csv', 'r') as file:
        reader = csv.reader(file, delimiter=";")
        next(reader)
        for row in reader:
            ou = str(row[0]).replace("OU0", "").replace("OU", "")
            menge = row[1]
            if not menge:
                menge = 0
            typ = row[2]
            preis = str(row[3]).replace(" €", "").replace(".", "")
            modell = row[4]
            if int(menge) > 0:
                for item in ous:
                    if str(item[1]).replace("(", "").replace(",)", "") == ou:
                        ou_id = Ou.objects.get(ou_id=str(item[0]).replace("(", "").replace(",)", ""))
                        # Detail_Investmittelplan_Soll.objects.create(ou_id=ou_id, jahr=jahr, typ=typ, modell=modell, menge=menge, preis_pro_stück=preis)
                        # alt_gesamt = Invest.objects.values_list('investmittel_gesamt').filter(jahr=jahr).filter(ou_id=str(item[0]).replace("(", "").replace(",)", "")).filter(typ="Planung")
                        # alt_gesamt = float(str(alt_gesamt[0]).replace("(Decimal('", "").replace("'),)", ""))
                        # kosten = int(menge) * int(preis)
                        # neu_gesamt = alt_gesamt + kosten
                        # invest_id = Invest.objects.values_list('id').filter(ou_id=ou_id).filter(jahr=jahr).filter(typ="Planung")
                        # Invest.objects.update_or_create(id=str(invest_id[0]).replace("(", "").replace(",)", ""), defaults={'investmittel_gesamt': neu_gesamt})            

    return render(request, "webapplication/csv.html")

def download(request, typ, input):
    files = Download.objects.all()
    download_id=""
    inputs = ""
    x = 0
    path = "/home/adminukd/WarenWirtschaftsSystem/Webserver/WWSystem/media/Download/"
    if input == 1:
        pass
    else:
        inputs = input 
    if typ == "invest_aktiv":
        Liste = Invest.objects.values_list('ou_id__ou', 'investmittel_gesamt', 'investmittel_übrig', 'bereich', 'team').filter(Q(ou_id__ou__icontains=inputs) | Q(investmittel_gesamt__icontains=inputs) | Q(investmittel_übrig__icontains=inputs) | Q(bereich__icontains=inputs) | Q(team__icontains=inputs)).filter(typ="Aktiv").filter(jahr=(int(datetime.date.today().year)))
        
        file = open(f"{path}investmittelplan.csv", "w")
        f = csv.writer(file)
        #f = csv.writer(open("/Users/voigttim/Programming/WarenWirtschaftsSystem/Webserver/WWSystem/media/Download/investmittelplan.csv", "w"))
        f.writerow(["OU", "Investmittel Jahresanfang in Euro", "Investmittel übrig in Euro", "Bereich", "Team"])

        for _ in Liste:
            f.writerow([Liste[x][0], Liste[x][1], Liste[x][2], Liste[x][3], Liste[x][4]])
            x = x + 1
        file.close()
        for file in files:
            if file.titel == "investmittelplan":
                download_id=file.pk
    elif typ == "lager":
        Liste = Lagerliste.objects.values_list('bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung').filter(Q(bestell_nr_field__sap_bestell_nr_field__icontains=inputs) | Q(modell__icontains=inputs) | Q(typ__icontains=inputs) | Q(spezifikation__icontains=inputs) | Q(zuweisung__icontains=inputs)).exclude(ausgegeben="1").annotate(Menge=Count("bestell_nr_field"))
        
        file = open(f"{path}lagerliste.csv", "w")        
        f = csv.writer(file)        
        f.writerow(["Bestell-Nr.", "Modell", "Typ", "Spezifikation", "Zuweisung", "Menge"])

        for _ in Liste:
            f.writerow([Liste[x][0], Liste[x][1], Liste[x][2], Liste[x][3], Liste[x][4], Liste[x][5]])
            x = x + 1
        file.close()
        for file in files:
            if file.titel == "lagerliste":
                download_id=Download.objects.values_list('id').filter(titel="lagerliste")
    elif typ == "bestellliste":
        Liste = BestellListe.objects.values_list('sap_bestell_nr_field', 'modell', 'typ', 'spezifikation', 'zuweisung', 'ersteller', 'investmittel', 'preis_pro_stück', 'menge', 'geliefert_anzahl').filter(Q(sap_bestell_nr_field__icontains=inputs) | Q(modell__icontains=inputs) | Q(typ__icontains=inputs) | Q(spezifikation__icontains=inputs) | Q(zuweisung__icontains=inputs) | Q(ersteller__username__icontains=inputs) | Q(investmittel__icontains=inputs) | Q(preis_pro_stück__icontains=inputs) | Q(menge__icontains=inputs) | Q(geliefert_anzahl__icontains=inputs)).exclude(geliefert="1")

        file = open(f"{path}bestellliste.csv", "w")
        #f = csv.writer()        
        f = csv.writer(file)        
        f.writerow(["SAP Bestell-Nr.", "Modell", "Typ", "Spezifikation", "Zuweisung", "Ersteller", "Invest", "Preis pro Stück", "Menge", "Anzahl Geliefert"])

        for _ in Liste:
            f.writerow([Liste[x][0], Liste[x][1], Liste[x][2], Liste[x][3], Liste[x][4], Liste[x][5], Liste[x][6], Liste[x][7], Liste[x][8], Liste[x][9]])
            #f.writerow([Test[x][0], Test[x][1], Test[x][2], Test[x][3], Test[x][4], Test[x][5], Test[x][6], Test[x][7], Test[x][8], Test[x][9], Test[x][10], Test[x][11]])
            x = x + 1
        file.close()
        for file in files:
            if file.titel == "bestellliste":
                download_id=Download.objects.values_list('id').filter(titel="bestellliste")
    elif typ == "invest_planung":
        Liste = Invest.objects.values_list('ou_id__ou', 'bereich', 'team', 'investmittel_gesamt').filter(Q(ou_id__ou__icontains=inputs) | Q(investmittel_gesamt__icontains=inputs) | Q(bereich__icontains=inputs) | Q(team__icontains=inputs)).filter(typ="Planung").filter(jahr=this_year)
        
        file = open(f"{path}investmittelplan_planung.csv", "w")
        #f = csv.writer(open("/Users/voigttim/Programming/WarenWirtschaftsSystem/Webserver/WWSystem/media/Download/investmittelplan_planung.csv", "w"))
        f = csv.writer(file)
        f.writerow(["OU", "Bereich", "Team", "Investmittel Gesamt"])

        for _ in Liste:
            f.writerow([Liste[x][0], Liste[x][1], Liste[x][2], Liste[x][3]])
            x = x + 1
        file.close()
        for file in files:
            if file.titel == "invest_planung":
                download_id=Download.objects.values_list('id').filter(titel="investmittelplan_planung")
    datei = get_object_or_404(Download, pk=str(download_id[0]).replace("(", "").replace(",)", ""))
    dateipfad = datei.dateipfad.path
    wrapper = datei.dateipfad.read()
    #response = FileResponse(file)
    response = HttpResponse( wrapper )
    response['Content-Type'] = 'test/csv'
    response['Content-Disposition'] = f'attachment; filename="{datei.titel}.csv"'
    print(response)
    return response
        
def Investmittelplanung(request):
    return getInvestmittelplanung(request)

def investmittelplanung(request):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel"))
    elif reset_group_check(request.user) == '0':
        return HttpResponseRedirect(reverse("investmittel"))
    else:
        Jahre = Invest.objects.values('jahr').distinct()
        if request.method == "POST":
            ous = Invest.objects.values_list("ou_id__ou").filter(typ="Aktiv").exclude(ou_id__ou=1).order_by("ou_id__ou")
            Jahr = request.POST["Jahr"]
            gelder = request.POST["gelder"]
            for ou in ous:
                ou = str(ou).replace("(", "").replace(",)", "")
                id = Invest.objects.values_list("id").filter(jahr=Jahr).filter(typ="Aktiv").filter(ou_id__ou=ou)
                input = str(request.POST[f"{ou}"]).replace(",", ".") or 0.00
                investmittel_übrig = input
                bestell_nr = Lagerliste.objects.values_list('bestell_nr_field').filter(klinik=ou).filter(ausgabe__year=Jahr)
                for nr in bestell_nr:
                    nr = str(nr).replace("('", "").replace("',)", "")
                    kosten = BestellListe.objects.values_list('preis_pro_stück').filter(sap_bestell_nr_field=nr)
                    for preis in kosten:
                        preis = float(str(preis).replace('(Decimal(', "").replace('),)', "").replace("'", ""))
                        investmittel_übrig = float(investmittel_übrig) - preis
                Invest.objects.update_or_create(id=str(id[0]).replace("(", "").replace(",)", ""), defaults={'investmittel_gesamt': input, 'investmittel_übrig': investmittel_übrig})
            
            return render(request, "webapplication/investmittelplanung.html", {
                "rows": Invest.objects.values('ou_id__ou').filter(typ="Aktiv").exclude(ou_id__ou=1).distinct(),
                "Jahre": Jahre
            })
        else:
            return render(request, "webapplication/investmittelplanung.html", {
                "rows": Invest.objects.values('ou_id__ou').filter(typ="Aktiv").exclude(ou_id__ou=1).distinct(),
                "Jahre": Jahre
            })

def InvestAktiv(request):
    return getInvestAktiv(request)

# View Function that represents the content of Investmittelplan
def invest(request):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        files = Download.objects.all()
        Jahre = Invest.objects.values('jahr').distinct()
        typ = "invest_aktiv"
        if reset_group_check(request.user) == '1':
            allowed = 1
        else:
            allowed = 0
        
        return render(request, "webapplication/invest.html", {
            "files": files,
            "allowed": allowed,
            "Jahre": Jahre,
            "rows": Invest.objects.values('ou_id__ou').filter(typ="Aktiv").distinct(),
            "typ": typ
        })

def ModifyInvest(request):
    return getModifyInvest(request)

def modify_invest(request, jahr):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel"))
    elif reset_group_check(request.user) == '0':
        return HttpResponseRedirect(reverse("investmittel"))
    else:
        Jahre = Invest.objects.values('jahr').filter(jahr=jahr)
        if request.method == "POST":
            ous = Invest.objects.values_list("ou_id__ou").filter(typ="Aktiv").order_by("ou_id__ou")
            Jahr = request.POST["Jahr"]
            for ou in ous:
                ou = str(ou).replace("(", "").replace(",)", "")
                id = Invest.objects.values_list("id").filter(jahr=Jahr).filter(typ="Aktiv").filter(ou_id__ou=ou)
                input = str(request.POST[f"{ou}"]).replace(".", "").replace(",", ".") or 0.00
                investmittel_übrig = input
                bestell_nr = Lagerliste.objects.values_list('bestell_nr_field').filter(klinik=ou).filter(ausgabe__year=Jahr)
                for nr in bestell_nr:
                    nr = str(nr).replace("('", "").replace("',)", "")
                    kosten = BestellListe.objects.values_list('preis_pro_stück').filter(sap_bestell_nr_field=nr)
                    for preis in kosten:
                        preis = float(str(preis).replace('(Decimal(', "").replace('),)', "").replace("'", ""))
                        investmittel_übrig = float(investmittel_übrig) - preis
                Invest.objects.update_or_create(id=str(id[0]).replace("(", "").replace(",)", ""), defaults={'investmittel_gesamt': input, 'investmittel_übrig': investmittel_übrig})

            return render(request, "webapplication/modify_invest.html", {
                "rows": Invest.objects.values('ou_id__ou').filter(typ="Aktiv").distinct(),
                "Jahr": Jahre
            })
        else:
            return render(request, "webapplication/modify_invest.html", {
                "rows": Invest.objects.values('ou_id__ou').filter(typ="Aktiv").distinct(),
                "Jahr": Jahre
            })

# View Function that represents the detailed content of a selected "ou" which shows the entries that are related to said "ou" in Investmittelplan
def detail_invest(request, klinik_ou, jahr):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        files = Download.objects.all()

        ou = klinik_ou
        nr = Lagerliste.objects.values_list('bestell_nr_field').filter(klinik=ou)
        detail_invest = Lagerliste.objects.select_related().values('klinik', 'bestell_nr_field', 'modell', 'typ', 'spezifikation', 'bestell_nr_field__preis_pro_stück', 'ausgegeben_an').filter(bestell_nr_field__in=nr[0:]).filter(klinik=ou).filter(ausgabe__year=jahr).annotate(Menge=Count("bestell_nr_field"))
        d_i_s = [{"typ": "Monitor", "menge": 0}, {"typ": "Notebook", "menge": 0}, {"typ": "Desktop-PC", "menge": 0}, {"typ": "Drucker", "menge": 0}, {"typ": "Scanner", "menge": 0}, {"typ": "Dockingstation", "menge": 0}, {"typ": "Diktiergerät", "menge": 0}, {"typ": "Transkription", "menge": 0}]            
        d_i = [{"typ": "Monitor", "menge": 0}, {"typ": "Notebook", "menge": 0}, {"typ": "Desktop-PC", "menge": 0}, {"typ": "Drucker", "menge": 0}, {"typ": "Scanner", "menge": 0}, {"typ": "Dockingstation", "menge": 0}, {"typ": "Diktiergerät", "menge": 0}, {"typ": "Transkription", "menge": 0}]            
        items_d_i_s = Detail_Investmittelplan_Soll.objects.values_list('typ', 'menge').filter(ou_id__ou=klinik_ou).filter(jahr=jahr)
        items_d_i = Lagerliste.objects.select_related().values_list('bestell_nr_field', 'typ').filter(bestell_nr_field__in=nr[0:]).filter(klinik=ou).filter(ausgabe__year=jahr).annotate(Menge=Count("bestell_nr_field"))
        
        for item in items_d_i_s:
            typ = str(item[0]).replace("(", "").replace(",)", "")
            menge = str(item[1]).replace("(", "").replace(",)", "")
            x = 0
            for entry in d_i_s:
                if entry["typ"] == typ:
                    d_i_s[x]["menge"] = d_i_s[x]["menge"] + int(menge)
                x = x + 1
        
        for item in items_d_i:
            typ = str(item[1]).replace("(", "").replace(",)", "")
            menge = str(item[2]).replace("(", "").replace(",)", "")
            x = 0
            for entry in d_i:
                if entry["typ"] == typ:
                    d_i[x]["menge"] = d_i[x]["menge"] + int(menge)
                x = x + 1
        
        return render(request, "webapplication/detail_invest.html", {
            "detail_invest": detail_invest,
            "detail_invest_soll_geplant": d_i_s,
            "detail_invest_soll_ausgegeben": d_i,
            "klinik_ou": ou,
            "files": files
        })
    
def InvestSoll(request):
    return getInvestSoll(request)

def invest_soll(request):
    files = Download.objects.all()
    typ = "invest_planung"
    Jahre = Invest.objects.values('jahr').distinct()
    return render(request, "webapplication/invest_soll.html", {
        "files": files,
        "typ": typ,
        "rows": Invest.objects.values('ou_id__ou').filter(typ="Aktiv").distinct(),
        "Jahre": Jahre
    })

def detail_invest_soll(request, ou, jahr):
    x = 0
    files = Download.objects.all()
    conf = 0
    typ = "invest_planung"

    return render(request, "webapplication/detail_invest_soll.html", {
        "ou": ou,
        "detail_investmittelplan_soll": Detail_Investmittelplan_Soll.objects.values('id', 'ou_id__ou', 'typ', 'modell', 'preis_pro_stück', 'spezifikation', 'admin', 'menge').filter(ou_id__ou=ou).filter(jahr=jahr),
        "files": files,
        "jahr": jahr
    })

def create_invest_soll(request, ou, jahr):
    if request.method == "POST":
        ou_id = Ou.objects.values_list('ou_id').filter(ou=ou)
        ou_invsoll = Ou.objects.get(ou_id=str(ou_id[0]).replace("(", "").replace(",", "").replace(")", ""))
        id = Invest.objects.values_list("id").filter(ou_id__in=ou_id).filter(typ="Planung").filter(jahr=jahr)
        typ = request.POST["typ"]
        modell = request.POST["modell"]
        menge = request.POST["menge"]
        preis_pro_stück = str(request.POST["preis_pro_stück"]).replace(",", ".")
        admin = request.user
        spezifikation = request.POST["spezifikation"]
        try:
            invest_planung = Detail_Investmittelplan_Soll.objects.create(ou_id=ou_invsoll, jahr=jahr, typ=typ, modell=modell, menge=menge, preis_pro_stück=preis_pro_stück, admin=admin, spezifikation=spezifikation)
            preis = Detail_Investmittelplan_Soll.objects.values_list('preis_pro_stück').filter(ou_id=ou_invsoll)
            meng = Detail_Investmittelplan_Soll.objects.values_list('menge').filter(ou_id=ou_invsoll)
            length = len(preis) - 1
            gesamt = float(str(preis[length]).replace("(", "").replace(")", "").replace("Decimal", "").replace("'", "").replace(",", "")) * float(str(meng[length]).replace("(", "").replace(")", "").replace("Decimal", "").replace("'", "").replace(",", ""))
            jetzt = Invest.objects.values_list('investmittel_gesamt').filter(ou_id=ou_invsoll).filter(typ="Planung").filter(jahr=this_year)
            neu = float(str(jetzt[0]).replace("(Decimal('", "").replace("'),)", "")) + gesamt
            Invest.objects.update_or_create(id = str(id[0]).replace("(", "").replace(",)", ""), defaults={'investmittel_gesamt': neu})
            return render(request, "webapplication/create_invest_soll.html", {
                "message": "Eintrag erfolgreich geplant",
                "ou": ou,
                "jahr": jahr
            })
        except ValueError:
            return render(request, "webapplication/create_invest_soll.html", {
                "alert": "Sie müssen angemeldet sein, damit Sie einen Eintrag erstellen können!",
                "ou": ou,
                "jahr": jahr
            })
    return render(request, "webapplication/create_invest_soll.html", {
        "ou": ou,
        "jahr": jahr
    })

def update_detail_invest_soll(request, ou, id, jahr):
    if request.method == "POST":
        items = Detail_Investmittelplan_Soll.objects.values_list("modell", "typ", "menge", "preis_pro_stück", "spezifikation").get(pk=id)
        modell = request.POST["modell"] or items[0]
        typ = request.POST["typ"] or items[1]
        menge = str(request.POST["menge"]).replace("-", "") or items[2]
        preis_pro_stück = str(request.POST["preis_pro_stück"]).replace(",", ".") or items[3]
        spezifikation = request.POST["spezifikation"] or items[4]
        ou_id = Ou.objects.values_list('ou_id').filter(ou=ou)
        inv_id = Invest.objects.values_list("id").filter(ou_id__in=ou_id).filter(typ="Planung").filter(jahr=this_year)

        preis_alt = Detail_Investmittelplan_Soll.objects.values_list("preis_pro_stück").filter(id=id)
        menge_alt = Detail_Investmittelplan_Soll.objects.values_list("menge").filter(id=id)
        length_alt = len(preis_alt) - 1
        gesamt_alt = float(str(preis_alt[length_alt]).replace("(", "").replace(")", "").replace("Decimal", "").replace("'", "").replace(",", "")) * float(str(menge_alt[length_alt]).replace("(", "").replace(")", "").replace("Decimal", "").replace("'", "").replace(",", ""))
        jetzt_alt = Invest.objects.values_list('investmittel_gesamt').get(id=str(inv_id[0]).replace("(", "").replace(",)", ""))
        neu_alt = float(jetzt_alt[0]) - gesamt_alt
        Invest.objects.update_or_create(id = str(inv_id[0]).replace("(", "").replace(",)", ""), defaults={'investmittel_gesamt': neu_alt})
        update = Detail_Investmittelplan_Soll.objects.filter(id=id).update(modell=modell, typ=typ, menge=menge, preis_pro_stück=preis_pro_stück, spezifikation=spezifikation)
        preis_neu = Detail_Investmittelplan_Soll.objects.values_list("preis_pro_stück").filter(id=id)
        menge_neu = Detail_Investmittelplan_Soll.objects.values_list("menge").filter(id=id)
        length_neu = len(preis_neu) - 1
        gesamt_neu = float(str(preis_neu[length_neu]).replace("(", "").replace(")", "").replace("Decimal", "").replace("'", "").replace(",", "")) * float(str(menge_neu[length_neu]).replace("(", "").replace(")", "").replace("Decimal", "").replace("'", "").replace(",", ""))
        jetzt_neu = Invest.objects.values_list('investmittel_gesamt').get(id=str(inv_id[0]).replace("(", "").replace(",)", ""))
        neu_neu = float(jetzt_neu[0]) + gesamt_neu
        Invest.objects.update_or_create(id = str(inv_id[0]).replace("(", "").replace(",)", ""), defaults={'investmittel_gesamt': neu_neu})

        if menge == "0":
            try:
                Detail_Investmittelplan_Soll.objects.filter(id=id).delete()
            except NoReverseMatch:
                return render(request, "webapplication/detail_invest_soll.html", {
                    "ou": ou,
                    "detail_investmittelplan_soll": Detail_Investmittelplan_Soll.objects.all().filter(ou_id__ou=ou),
                    "jahr": jahr
                })

        return render(request, "webapplication/update_detail_invest_soll.html", {
            "invest_soll": Detail_Investmittelplan_Soll.objects.all().filter(id=id),
            "ou": ou,
            "id": id    ,
            "message": "Eintrag erflogreich aktualisiert",
            "jahr": jahr
        })
    else:
        return render(request, "webapplication/update_detail_invest_soll.html", {
            "invest_soll": Detail_Investmittelplan_Soll.objects.all().filter(id=id),
            "ou": ou,
            "id": id,
            "jahr": jahr
        })

def löschen_detail_invest_soll(request, id):
    pass

def test(request):
    if group_check(request.user) == '1':
        return HttpResponseRedirect(reverse("investmittel_soll"))
    else:
        return render(request, "webapplication/test.html",{
            "unlock": 3
        })