from flask import Flask, render_template, request, session, redirect
import requests
import os
import random
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "accesstour-demo-secret-key"

# ============================================================
# GOOGLE API KEY
# ============================================================

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

GOOGLE_PLACES_SEARCH_URL = (
    "https://places.googleapis.com/v1/places:searchText"
)

# ============================================================
# WIKIMEDIA
# ============================================================

WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"

WIKIMEDIA_HEADERS = {
    "User-Agent": "AccessTour/1.0 (educational accessible tourism project)"
}

# ============================================================
# DESTINATIONS
# ============================================================

DESTINATIONS = [

    {
        "name": "Jaipur, Rajasthan",
        "url": "/destination?place=Jaipur,+Rajasthan",
        "class": "jaipur",
        "search": "Hawa Mahal Jaipur Rajasthan India"
    },

    {
        "name": "Kerala",
        "url": "/destination?place=Kerala",
        "class": "kerala",
        "search": "Kerala India backwaters Alleppey Munnar"
    },

    {
        "name": "Goa",
        "url": "/destination?place=Goa",
        "class": "goa",
        "search": "Goa India beaches tourism"
    },

    {
        "name": "Agra",
        "url": "/destination?place=Agra",
        "class": "agra",
        "search": "Taj Mahal Agra India"
    },

    {
        "name": "New Delhi",
        "url": "/destination?place=New+Delhi",
        "class": "delhi",
        "search": "India Gate New Delhi India"
    },

    {
        "name": "Mumbai, Maharashtra",
        "url": "/destination?place=Mumbai,+Maharashtra",
        "class": "mumbai",
        "search": "Gateway of India Mumbai Marine Drive Mumbai"
    },

    {
        "name": "Hyderabad, Telangana",
        "url": "/destination?place=Hyderabad,+Telangana",
        "class": "hyderabad",
        "search": "Charminar Hyderabad Telangana India"
    },

    {
        "name": "Amritsar, Punjab",
        "url": "/destination?place=Amritsar,+Punjab",
        "class": "amritsar",
        "search": "Golden Temple Amritsar Punjab India"
    },

    {
        "name": "Bengaluru, Karnataka",
        "url": "/destination?place=Bengaluru,+Karnataka",
        "class": "bengaluru",
        "search": "Vidhana Soudha Bengaluru Karnataka India"
    },

    {
        "name": "Kolkata, West Bengal",
        "url": "/destination?place=Kolkata,+West+Bengal",
        "class": "kolkata",
        "search": "Victoria Memorial Kolkata India"
    },

    {
        "name": "Mysore, Karnataka",
        "url": "/destination?place=Mysore,+Karnataka",
        "class": "mysore",
        "search": "Mysore Palace Karnataka India"
    },

    {
        "name": "Varanasi, Uttar Pradesh",
        "url": "/destination?place=Varanasi,+Uttar+Pradesh",
        "class": "varanasi",
        "search": "Varanasi Ganges ghats Uttar Pradesh India"
    }
]


# ============================================================
# TOURIST PLACE SEARCH TERMS
# ============================================================

TOURIST_SEARCHES = {

    "jaipur": [
        "Hawa Mahal Jaipur Rajasthan",
        "City Palace Jaipur Rajasthan",
        "Amber Fort Jaipur Rajasthan",
        "Jantar Mantar Jaipur Rajasthan"
    ],

    "kerala": [
        "Alleppey Kerala India",
        "Munnar Kerala India",
        "Kochi Kerala India",
        "Kovalam Kerala India"
    ],

    "goa": [
        "Basilica of Bom Jesus Goa",
        "Fort Aguada Goa",
        "Calangute Beach Goa",
        "Baga Beach Goa"
    ],

    "agra": [
        "Taj Mahal Agra",
        "Agra Fort Agra",
        "Mehtab Bagh Agra",
        "Itmad Ud Daulah Agra"
    ],

    "new delhi": [
        "India Gate New Delhi",
        "Red Fort Delhi",
        "Lotus Temple Delhi",
        "Qutub Minar Delhi"
    ],

    "mumbai": [
        "Gateway of India Mumbai",
        "Chhatrapati Shivaji Maharaj Terminus Mumbai",
        "Elephanta Caves Mumbai",
        "Sanjay Gandhi National Park Mumbai"
    ],

    "hyderabad": [
        "Charminar Hyderabad",
        "Golconda Fort Hyderabad",
        "Salar Jung Museum Hyderabad",
        "Hussain Sagar Hyderabad"
    ],

    "amritsar": [
        "Golden Temple Amritsar",
        "Jallianwala Bagh Amritsar",
        "Partition Museum Amritsar",
        "Gobindgarh Fort Amritsar"
    ],

    "bengaluru": [
        "Vidhana Soudha Bengaluru",
        "Bangalore Palace",
        "Lalbagh Botanical Garden Bengaluru",
        "Cubbon Park Bengaluru"
    ],

    "kolkata": [
        "Victoria Memorial Kolkata",
        "Indian Museum Kolkata",
        "Howrah Bridge Kolkata",
        "St Paul's Cathedral Kolkata"
    ],

    "mysore": [
        "Mysore Palace",
        "Chamundi Hill Mysore",
        "Brindavan Gardens Mysore",
        "St Philomena's Church Mysore"
    ],

    "varanasi": [
        "Dashashwamedh Ghat Varanasi",
        "Kashi Vishwanath Temple Varanasi",
        "Sarnath Varanasi",
        "Assi Ghat Varanasi"
    ]
}


# ============================================================
# WIKIMEDIA IMAGE FUNCTION
# ============================================================

def get_wikimedia_images(search_terms):

    try:

        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": search_terms,
            "gsrnamespace": "6",
            "gsrlimit": "20",
            "gsrsort": "relevance",
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": "1000",
            "format": "json",
            "formatversion": "2"
        }

        response = requests.get(
            WIKIMEDIA_API,
            params=params,
            headers=WIKIMEDIA_HEADERS,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        pages = data.get("query", {}).get("pages", [])

        images = []

        for page in pages:

            imageinfo = page.get("imageinfo", [])

            if not imageinfo:
                continue

            image = imageinfo[0]

            image_url = (
                image.get("thumburl")
                or image.get("url")
            )

            if image_url:
                images.append(image_url)

        images = list(dict.fromkeys(images))

        random.shuffle(images)

        return images

    except Exception as e:

        print("Wikimedia image error:", e)

        return []


# ============================================================
# PREPARE DESTINATION IMAGES
# ============================================================

def prepare_destination_images():

    destination_images = {}

    for destination in DESTINATIONS:

        images = get_wikimedia_images(
            destination["search"]
        )

        if images:

            destination_images[
                destination["class"]
            ] = images[0]

        else:

            destination_images[
                destination["class"]
            ] = ""

    return destination_images


# ============================================================
# GOOGLE PLACES SEARCH
# ============================================================

def google_place_search(place_name):

    if not GOOGLE_MAPS_API_KEY:

        print("ERROR: GOOGLE_MAPS_API_KEY is not set.")

        return [], "Google API key is not configured."


    headers = {

        "Content-Type": "application/json",

        "X-Goog-Api-Key":
            GOOGLE_MAPS_API_KEY,

        "X-Goog-FieldMask":
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.rating,"
            "places.userRatingCount,"
            "places.googleMapsUri,"
            "places.accessibilityOptions"

    }


    # Find the destination's tourist attractions

    key = place_name.lower()

    search_list = None

    for destination_key in TOURIST_SEARCHES:

        if destination_key in key:

            search_list = TOURIST_SEARCHES[
                destination_key
            ]

            break


    # If destination is not in our list,
    # search Google directly for tourist attractions.

    if not search_list:

        search_list = [

            "tourist attractions " + place_name,
            "popular tourist places " + place_name,
            "landmarks " + place_name
        ]


    places_found = []

    errors = []


    # Search several attractions

    for search_term in search_list:

        payload = {

            "textQuery": search_term,

            "pageSize": 1

        }

        try:

            response = requests.post(

                GOOGLE_PLACES_SEARCH_URL,

                headers=headers,

                json=payload,

                timeout=20

            )


            print(
                "Google Places:",
                search_term,
                "->",
                response.status_code
            )


            if response.status_code != 200:

                print(
                    "Google response:",
                    response.text
                )

                errors.append(
                    "Google Places API returned an error."
                )

                continue


            data = response.json()

            places = data.get(
                "places",
                []
            )


            if not places:

                continue


            result = places[0]

            display_name = result.get(
                "displayName",
                {}
            )


            name = display_name.get(
                "text",
                search_term
            )


            accessibility_options = result.get(
                "accessibilityOptions",
                {}
            )


            place = {

                "place_id":
                    result.get("id"),

                "name":
                    name,

                "address":
                    result.get(
                        "formattedAddress",
                        ""
                    ),

                "rating":
                    result.get("rating"),

                "user_rating_count":
                    result.get(
                        "userRatingCount"
                    ),

                "maps_url":
                    result.get(
                        "googleMapsUri"
                    ),

                "accessibility_options":
                    accessibility_options

            }


            # Avoid duplicate places

            already_exists = False

            for existing in places_found:

                if existing["place_id"] == place["place_id"]:

                    already_exists = True

                    break


            if not already_exists:

                places_found.append(place)


        except requests.exceptions.RequestException as e:

            print(
                "Google Places connection error:",
                e
            )

            errors.append(
                "Could not connect to Google Places."
            )


        except Exception as e:

            print(
                "Google Places error:",
                e
            )


    if not places_found:

        if errors:

            return [], errors[0]

        return [], "No tourist places were found."


    return places_found, None


# ============================================================
# OPENSTREETMAP
# ============================================================

def osm_search(place):

    try:

        url = (
            "https://nominatim.openstreetmap.org/search"
        )

        params = {

            "q": place,

            "format": "json",

            "limit": 1

        }

        headers = {

            "User-Agent":
                "AccessTour/1.0 "
                "(educational accessible tourism project)"

        }


        response = requests.get(

            url,

            params=params,

            headers=headers,

            timeout=15

        )


        response.raise_for_status()


        results = response.json()


        if not results:

            return None


        return results[0]


    except Exception as e:

        print(
            "OpenStreetMap error:",
            e
        )

        return None


# ============================================================
# ACCESSIBILITY HELPERS
# ============================================================

def value_text(value):

    if value is True:

        return "Yes"

    if value is False:

        return "No"

    return "Not reported"


def css_class(value):

    if value is True:

        return "yes"

    if value is False:

        return "no"

    return "unknown"


def make_item(
    icon,
    title,
    value,
    detail="",
    source=""
):

    return {

        "icon": icon,

        "title": title,

        "value": value_text(value),

        "class": css_class(value),

        "detail": detail,

        "source": source

    }
# ============================================================
# PROFILE
# ============================================================

@app.route("/profile")
def profile():
    return render_template("profile.html")

# ============================================================
# SAVE PROFILE
# ============================================================

@app.route("/save-profile", methods=["POST"])
def save_profile():

    session["profile"] = {

        "name": request.form.get(
            "name",
            ""
        ),

        "email": request.form.get(
            "email",
            ""
        ),

        "age": request.form.get(
            "age",
            ""
        ),

        "destination": request.form.get(
            "destination",
            ""
        ),

        # Changed "requirements" to "accessibility" to match your HTML input names
        "requirements":
            request.form.getlist(
                "accessibility"
            ),

        "travel_type":
            request.form.get(
                "travel_type",
                ""
            ),

        "additional":
            request.form.get(
                "notes",
                ""
            )
    }

    return redirect(
        "/journey-evaluation"
    )

# ============================================================
# JOURNEY COMPATIBILITY & RISK EVALUATION
# ============================================================

@app.route("/journey-evaluation")
def journey_evaluation():

    profile = session.get("profile")

    if not profile:

        return redirect("/profile")

    destination_name = profile.get(
        "destination",
        ""
    )

    if not destination_name:

        return render_template(
            "journey-evaluation.html",
            profile=profile,
            places=[],
            compatibility_score=0,
            confidence_score=0,
            status="Review Required",
            status_class="review",
            status_icon="🟡",
            route_notes="Please select a preferred destination in your profile.",
            summary="A destination is required before the journey can be evaluated.",
            verified_items=[]
        )


    # --------------------------------------------------------
    # Get Google accessibility data
    # --------------------------------------------------------

    places, google_error = google_place_search(
        destination_name
    )


    requirements = profile.get(
        "requirements",
        []
    )


    # --------------------------------------------------------
    # Convert profile requirements into Google fields
    # --------------------------------------------------------

    requirement_map = {

        "Wheelchair Access":
            "wheelchairAccessibleEntrance",

        "Accessible Parking":
            "wheelchairAccessibleParking",

        "Accessible Restroom":
            "wheelchairAccessibleRestroom",

        "Accessible Seating":
            "wheelchairAccessibleSeating"

    }


    total_required = 0
    supported = 0
    not_supported = 0
    not_reported = 0

    verified_items = []


    # --------------------------------------------------------
    # Analyse every tourist place
    # --------------------------------------------------------

    for place in places:

        options = place.get(
            "accessibility_options",
            {}
        )

        for requirement in requirements:

            google_field = requirement_map.get(
                requirement
            )


            # Google does not provide this field
            if not google_field:

                not_reported += 1

                verified_items.append({

                    "requirement":
                        requirement,

                    "status":
                        "Not reported",

                    "class":
                        "unknown",

                    "place":
                        place["name"]

                })

                continue


            total_required += 1

            value = options.get(
                google_field
            )


            if value is True:

                supported += 1

                verified_items.append({

                    "requirement":
                        requirement,

                    "status":
                        "Supported",

                    "class":
                        "yes",

                    "place":
                        place["name"]

                })


            elif value is False:

                not_supported += 1

                verified_items.append({

                    "requirement":
                        requirement,

                    "status":
                        "Not accessible",

                    "class":
                        "no",

                    "place":
                        place["name"]

                })


            else:

                not_reported += 1

                verified_items.append({

                    "requirement":
                        requirement,

                    "status":
                        "Not reported",

                    "class":
                        "unknown",

                    "place":
                        place["name"]

                })


    # --------------------------------------------------------
    # Compatibility Score
    # --------------------------------------------------------

    if total_required > 0:

        compatibility_score = round(
            (supported / total_required) * 100
        )

    else:

        compatibility_score = 0


    # --------------------------------------------------------
    # Confidence Score
    # --------------------------------------------------------

    total_checked = (
        total_required +
        not_reported
    )


    if total_checked > 0:

        confidence_score = round(
            (total_required / total_checked) * 100
        )

    else:

        confidence_score = 0


    # --------------------------------------------------------
    # Overall Status
    # --------------------------------------------------------

    if (
        compatibility_score >= 75
        and confidence_score >= 60
    ):

        status = "High Compatibility"

        status_class = "high"

        status_icon = "🟢"


    elif (
        compatibility_score >= 45
    ):

        status = "Review Required"

        status_class = "review"

        status_icon = "🟡"


    else:

        status = "Assistance Recommended"

        status_class = "assistance"

        status_icon = "🔵"


    # --------------------------------------------------------
    # Route Notes
    # --------------------------------------------------------

    notes = []


    if supported > 0:

        notes.append(
            str(supported)
            + " accessibility requirement(s) "
            + "were verified as supported."
        )


    if not_supported > 0:

        notes.append(
            str(not_supported)
            + " requirement(s) were reported "
            + "as not accessible."
        )


    if not_reported > 0:

        notes.append(
            str(not_reported)
            + " accessibility item(s) were "
            + "not reported by the available "
            + "Google Places data."
        )


    if not places:

        notes.append(
            "No tourist places were returned "
            "by Google Places for this destination."
        )


    if google_error:

        notes.append(
            google_error
        )


    route_notes = " ".join(notes)


    summary = (

        "The evaluation compares the accessibility "
        "requirements selected in your profile with "
        "verified accessibility information available "
        "for tourist places in "
        + destination_name
        + "."

    )


    return render_template(

        "journey-evaluation.html",

        profile=profile,

        places=places,

        compatibility_score=
            compatibility_score,

        confidence_score=
            confidence_score,

        status=status,

        status_class=status_class,

        status_icon=status_icon,

        route_notes=route_notes,

        summary=summary,

        verified_items=verified_items

    )

# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    destination_images = (
        prepare_destination_images()
    )

    return render_template(

        "index.html",

        destinations=DESTINATIONS,

        destination_images=
            destination_images

    )


# ============================================================
# DESTINATION
# ============================================================

@app.route("/destination")
def destination():

    place_name = request.args.get(
        "place",
        ""
    ).strip()


    if not place_name:

        return render_template(

            "destination.html",

            place_name="Destination",

            places=[],

            google_used=False,

            osm_used=False,

            error="Please enter a destination."

        )


    google_used = False

    osm_used = False

    error = ""


    # --------------------------------------------------------
    # Search tourist places
    # --------------------------------------------------------

    places, google_error = (
        google_place_search(
            place_name
        )
    )


    if places:

        google_used = True

    elif google_error:

        error = google_error


    # --------------------------------------------------------
    # OSM fallback
    # --------------------------------------------------------

    osm_place = osm_search(
        place_name
    )


    if osm_place:

        osm_used = True


    # --------------------------------------------------------
    # Build accessibility data
    # --------------------------------------------------------

    for place in places:

        options = place.get(
            "accessibility_options",
            {}
        )


        place["accessibility"] = [

            make_item(

                "♿",

                "Wheelchair Accessible Entrance",

                options.get(
                    "wheelchairAccessibleEntrance"
                ),

                "Accessibility information returned by Google Places.",

                "Google Places"

            ),

            make_item(

                "🅿️",

                "Wheelchair Accessible Parking",

                options.get(
                    "wheelchairAccessibleParking"
                ),

                "Accessibility information returned by Google Places.",

                "Google Places"

            ),

            make_item(

                "🚻",

                "Wheelchair Accessible Restroom",

                options.get(
                    "wheelchairAccessibleRestroom"
                ),

                "Accessibility information returned by Google Places.",

                "Google Places"

            ),

            make_item(

                "🪑",

                "Wheelchair Accessible Seating",

                options.get(
                    "wheelchairAccessibleSeating"
                ),

                "Accessibility information returned by Google Places.",

                "Google Places"

            ),

            make_item(

                "🛗",

                "Accessible Lift / Elevator",

                None,

                "Google Places does not currently provide a dedicated lift/elevator accessibility field.",

                "Not available"

            ),

            make_item(

                "👁️",

                "Visual Assistance",

                None,

                "No verified visual-assistance field was returned by the available place data.",

                "Not available"

            ),

            make_item(

                "🔊",

                "Audio Guidance",

                None,

                "No verified audio-guidance field was returned by the available place data.",

                "Not available"

            ),

            make_item(

                "🦻",

                "Hearing Assistance",

                None,

                "No verified hearing-assistance field was returned by the available place data.",

                "Not available"

            ),

            make_item(

                "🚨",

                "Accessible Emergency Services",

                None,

                "No verified emergency-accessibility field was returned by the available place data.",

                "Not available"

            )

        ]


    # --------------------------------------------------------
    # If Google found nothing
    # --------------------------------------------------------

    if not places and not error:

        error = (
            "No tourist places were found "
            "for this destination."
        )


    return render_template(

        "destination.html",

        place_name=place_name,

        places=places,

        google_used=google_used,

        osm_used=osm_used,

        error=error

    )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "AccessTour - Travel Without Barriers"
    )

    print("=" * 60)


    if GOOGLE_MAPS_API_KEY:

        print(
            "Google Places API key: FOUND"
        )

    else:

        print(
            "WARNING: Google Places API key NOT FOUND"
        )

        print(
            "Set GOOGLE_MAPS_API_KEY before running."
        )


    print("=" * 60)
    
    

    app.run(
        debug=True
    )