from django.db import IntegrityError
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from webapplication.models import BestellListe, Lagerliste, Achievements

# Attempts to fetch a BestellListe entry by the submitted order number (bestell_nr) from the POST request
def get_bestell_nr(request):
    try:
        # Extract the 'bestell_nr' from POST data and use it to retrieve the matching object
        return BestellListe.objects.get(pk=str(request.POST["bestell_nr"]))
    except (BestellListe.DoesNotExist, ValueError):
        # Return None if the order number is invalid or doesn't exist
        return None


# Retrieves all selected inventory numbers from the POST data
def get_selected_items(request):
    x = 0
    selected_items = []

    # Continuously checks the POST data for indexed inventory numbers: "0", "1", ...
    while True:
        item = request.POST.get(f"{x}", False)
        if item:
            # Add the item to the list if it exists
            selected_items.append(item)
        else:
            # Stop looping when no more indexed items are found
            break
        x += 1

    return selected_items


# Looks up detailed information (typ, modell, spezifikation, zuweisung) based on a given bestell_nr
def get_bestell_details(bnr):
    # Query all relevant fields from BestellListe entries
    entries = BestellListe.objects.values_list('sap_bestell_nr_field', 'typ', 'modell', 'spezifikation', 'zuweisung')

    # Iterate through each entry and look for one where bestell_nr matches (as substring)
    for entry in entries:
        if str(bnr) in str(entry[0]):
            return entry[1], entry[2], entry[3], entry[4]  # Return details if found

    # Return None placeholders if nothing matched
    return None, None, None, None


# Handles creation of Lagerliste entries and achievement tracking for all selected inventory numbers
def process_selected_items(request, selected_items, typ, modell, spezifikation, zuweisung, bnr):
    fail = ""  # Tracks failures (not currently used but can be extended)
    dupe = ""  # Tracks duplicate inventory numbers (already exist in Lagerliste)
    ach = 0    # Stores the current unlock level for achievements

    # Get current user's existing count of created Lagerliste entries
    lager_count = Achievements.objects.filter(user=request.user).values_list('lager_count')

    # Process each selected inventory number
    for inventarnummer in selected_items:
        try:
            # Attempt to create a new Lagerliste entry
            create_lager_entry(inventarnummer, typ, modell, spezifikation, zuweisung, bnr)

            # Update user achievements and get new total
            ach, new = update_achievements(request, lager_count)

            # Check if the new total unlocks an achievement badge
            check_achievement_unlock(request, ach, new)

        except IntegrityError:
            # If the inventory number already exists in Lagerliste (unique constraint), treat it as a duplicate
            dupe += f"{inventarnummer}, "
            continue

    # Return a rendered response to the user with results
    return handle_response(request, ach, fail, dupe)


# Creates a Lagerliste database entry for the given inventory number and associated details
def create_lager_entry(inventarnummer, typ, modell, spezifikation, zuweisung, bnr):
    Lagerliste.objects.create(
        inventarnummer=inventarnummer,     # Unique identifier for the item
        typ=typ,                            # Type of item (e.g., PC, Monitor)
        modell=modell,                      # Model name or number
        spezifikation=spezifikation,        # Any technical specifications
        zuweisung=zuweisung,                # Intended usage or department assignment
        bestell_nr_field=bnr,               # Reference to the original order
        ausgegeben=0                        # Item is not issued yet (default state)
    )


# Updates the achievement tracking for the user; either increments or initializes the count
def update_achievements(request, lager_count):
    if lager_count:
        # Convert count to integer and increment it
        new = int(str(lager_count[0]).replace('(', '').replace(',)', '')) + 1
    else:
        # First-time entry creation: initialize Achievements for the user
        new = 1
        Achievements.objects.update_or_create(user=request.user, defaults={
            'lager_count': new,
            'lager_achievement': 0,
            'bestell_count': 0,
            'bestell_achievement': 0,
            'handout_count': 0,
            'handout_achievement': 0,
            'rueckgabe_count': 0,
            'rueckgabe_achievement': 0
        })
    return 0, new  # Return current achievement level (default 0) and the updated count


# Determines if a new achievement level has been reached and updates it accordingly
def check_achievement_unlock(request, ach, new):
    if new == 50:
        # Unlock achievement level 1 at 50 items
        Achievements.objects.filter(user=request.user).update(lager_achievement=1)
    elif new == 200:
        # Unlock achievement level 2 at 200 items
        Achievements.objects.filter(user=request.user).update(lager_achievement=2)
    elif new == 500:
        # Unlock achievement level 3 at 500 items
        Achievements.objects.filter(user=request.user).update(lager_achievement=3)


# Returns an appropriate template response depending on success, duplicates, or failure
def handle_response(request, ach, fail, dupe):
    # Load only order numbers that are not yet marked as delivered and have investmittel == "Ja"
    bestell_nr_options = BestellListe.objects.all().exclude(geliefert="1").exclude(investmittel="Nein")

    if fail:
        fail = fail.rstrip(', ')
        return render(request, "webapplication/create_lager.html", {
            "dupe": dupe,
            "fail": fail,
            "bestell_nr": bestell_nr_options,
            "unlock": ach
        })

    if dupe:
        dupe = dupe.rstrip(', ')
        return render(request, "webapplication/create_lager.html", {
            "dupe": dupe,
            "bestell_nr": bestell_nr_options,
            "unlock": ach
        })

    # If everything was successful
    return render(request, "webapplication/create_lager.html", {
        "message": "Einträge erfolgreich angelegt",  # Success message
        "unlock": ach,
        "bestell_nr": bestell_nr_options
    })