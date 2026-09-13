# -*- coding: utf-8 -*-
"""Authored copy for the 8BTSI Corp site.

Everything in this file is written by hand and is checked by lint.py.
Product body text is not in here: it comes from catalogue.json and is the
manufacturer's own description, kept for factual accuracy.
"""

COMPANY = {
    "name": "8BTSI Corp.",
    "legal": "8BTSI Corp.",
    "tagline": "Being On-Air is Global",
    "founded": "November 2006",
    "address_line1": "JEB Building, Unit 305",
    "address_line2": "Eulogio Amang Rodriguez Ave., Rosario",
    "address_line3": "Pasig City 1609, Metro Manila",
    "phone_display": "02 275 4035",
    "phone_link": "+6322754035",
    "email": "info@btsi.com.ph",
    "support_email": "support@btsi.com.ph",
    "hours": "Weekdays, 8:30am to 5:30pm",
    "facebook": "https://www.facebook.com/8BTSI/",
    "linkedin": "https://www.linkedin.com/company/8btsi-corp/",
}

HOME = {
    "hero_eyebrow": "Broadcast supply and engineering since 2006",
    "hero_h1": "Transmission, studio and playout equipment for Philippine broadcasters.",
    "hero_sub": (
        "8BTSI Corp supplies the transmitters, antennas, consoles, processors and "
        "playout systems that put radio and television stations on air, and our "
        "engineers install and commission them anywhere in the country."
    ),
    "hero_cta_primary": "Browse equipment",
    "hero_cta_secondary": "Request a quote",

    "pillars_h2": "What we carry",
    "pillars_sub": (
        "Five equipment groups covering the signal chain from the studio microphone "
        "to the antenna."
    ),

    "services_h2": "Engineering and project services",
    "services_sub": (
        "Supply is one part of the contract. We plan the system, install it, wire it "
        "and hand it over commissioned."
    ),

    "brands_h2": "Brands we represent",
    "brands_sub": (
        "Fourteen manufacturers whose equipment we carry, install and support in the "
        "Philippines."
    ),

    "featured_h2": "Three we are asked for most.",
    "featured_sub": "Telos on the phones, Omnia on the processing, Axia on the desk.",

    "testi_h2": "What stations say.",
    "testi_sub": "Three customers, in their own words.",

    "cta_h2": "Tell us what the station needs.",
    "cta_body": (
        "Send us the power, coverage and studio requirements and we will specify the "
        "equipment against them and quote it."
    ),
}

# Each pillar: slug, title, short line for cards, longer intro for the page.
PILLARS = {
    "rf-transmission": {
        "title": "RF transmission",
        "card": "FM and AM transmitters, remote control units and radio antennas.",
        "intro": (
            "Radio transmission runs from a 20W community FM exciter up to a 50kW AM "
            "plant. We carry Elenos FM transmitters and Continental Lensa AM "
            "transmitters, the remote control and changeover units that keep an "
            "unattended site running, and Aldena antennas to radiate the result."
        ),
        "meta": (
            "FM and AM transmitters, remote control units, changeover systems and "
            "radio broadcast antennas supplied and installed in the Philippines by "
            "8BTSI Corp."
        ),
    },
    "tv-transmission": {
        "title": "TV transmission",
        "card": "Television transmitters, exciters, headend and loudness control.",
        "intro": (
            "Digital and analogue television transmission built around Itelco "
            "transmitters and MEX II exciters, with Tecsys headend equipment for "
            "receiving, converting and remultiplexing feeds, Linear Acoustic "
            "processors for loudness compliance, and Aldena antennas for Band I, "
            "Band III and UHF."
        ),
        "meta": (
            "DVB-T television transmitters, exciters, satellite headend and DTV "
            "loudness control supplied and installed in the Philippines by 8BTSI Corp."
        ),
    },
    "playout": {
        "title": "Playout systems",
        "card": "Television and radio automation, ingest, graphics and ad insertion.",
        "intro": (
            "Automation that runs a channel without someone watching the clock. "
            "PlayBox covers television playout, ingest, on-screen graphics, ad "
            "insertion and archive, while WinMedia handles radio playout, music "
            "scheduling and traffic."
        ),
        "meta": (
            "PlayBox television automation and WinMedia radio automation for playout, "
            "ingest, graphics, ad insertion and scheduling, supplied in the "
            "Philippines by 8BTSI Corp."
        ),
    },
    "studio-audio": {
        "title": "Studio and audio",
        "card": "AoIP consoles, processing, routing, phone systems and acoustics.",
        "intro": (
            "A studio built on audio over IP. Axia consoles and xNodes carry the audio "
            "on the network, Omnia processors shape what goes to the transmitter, "
            "Telos systems put callers on air, Yellowtec mounts the microphones and "
            "Vicoustic panels treat the room."
        ),
        "meta": (
            "Axia AoIP mixing consoles, Omnia audio processing, Telos talkshow "
            "systems, routing, microphone arms and acoustic treatment from 8BTSI Corp "
            "in the Philippines."
        ),
    },
    "ip-codecs": {
        "title": "IP codecs",
        "card": "Audio and video codecs for remotes and studio to transmitter links.",
        "intro": (
            "Links that bring audio and video back from the field over whatever "
            "network is available. Telos codecs cover ISDN, IP and streaming links "
            "between studio and transmitter, and Comrex LiveShot sends two-way HD "
            "video over bonded cellular."
        ),
        "meta": (
            "Telos and Comrex audio and video IP codecs for remote broadcasts and "
            "studio to transmitter links, supplied in the Philippines by 8BTSI Corp."
        ),
    },
}

CATEGORY_TITLES = {
    "fm-transmitters": "FM transmitters",
    "fm-remote-control-unit": "FM remote control and changeover",
    "am-transmitters": "AM transmitters",
    "radio-broadcast-antennas": "Radio broadcast antennas",
    "tv-transmitters": "TV transmitters",
    "tv-exciters": "TV exciters",
    "tv-headend": "TV headend",
    "tv-loudness-control": "TV loudness control",
    "tv-broadcast-antennas": "TV broadcast antennas",
    "tv-automation": "TV automation",
    "radio-automation": "Radio automation",
    "acoustic-panels": "Acoustic panels",
    "audio-interfaces-routing-control": "Audio interfaces, routing and control",
    "audio-mixers": "Audio mixers",
    "audio-processors": "Audio processors",
    "axia-software": "Axia software",
    "broadcast-telephone-systems": "Broadcast telephone systems",
    "mic-arm": "Microphone arms",
    "microphone-processing": "Microphone processing",
    "networked-radio-consoles": "Networked radio consoles",
    "signaling-device": "Signalling devices",
    "streaming-audio-processing-encoding": "Streaming audio processing and encoding",
    "audio-codecs": "Audio codecs",
    "video-codecs": "Video codecs",
}

# The three brand posters carried over from the old home page. Each is a
# product photograph on that manufacturer's colour, with no text baked in, so
# the heading and line below are set in our own type over the top.
FEATURED = [
    {
        "brand": "telos",
        "line": "Broadcast telephone systems",
        "blurb": "Callers on air with hybrid processing and echo cancellation.",
    },
    {
        "brand": "omnia",
        "line": "Audio processing",
        "blurb": "What sits between the studio and the transmitter and decides how a station sounds.",
    },
    {
        "brand": "axia",
        "line": "AoIP consoles and routing",
        "blurb": "Six faders up to forty, with the audio carried on the network.",
    },
]

SERVICES = [
    {
        "title": "Project management",
        "body": (
            "We plan the system, schedule the work and run it to handover. System "
            "planning, studio design layout and customer training are part of it."
        ),
    },
    {
        "title": "Engineering services",
        "body": (
            "Our engineers install and commission equipment on site, with years of "
            "field experience in Philippine broadcast behind them."
        ),
    },
    {
        "title": "Installation and wiring",
        "body": (
            "Racks, cabling, grounding and the transmitter site itself. The station "
            "takes delivery of a commissioned system."
        ),
    },
    {
        "title": "Product training",
        "body": (
            "We train your operators and engineers on the equipment before we leave."
        ),
    },
]

COMPANY_PAGE = {
    "h1": "Our company",
    "lead": "Broadcast equipment supplied, installed and supported in the Philippines.",
    "body": [
        "8BTSI Corp was established in November 2006 to serve the broadcast and "
        "telecom industry in the Philippines.",
        "The company is a team of sales executives and engineers with long experience "
        "in Philippine broadcast. We supply equipment from fourteen manufacturers and "
        "support it here with project management, system planning, installation and "
        "wiring, and product training.",
        "We aim to supply reliable equipment at a price a station can carry, and to "
        "stay reachable after the installation is signed off.",
    ],
    "stats": [
        {"figure": "2006", "label": "Serving Philippine broadcast since"},
        {"figure": "14", "label": "Manufacturers represented"},
        {"figure": "106", "label": "Products in the catalogue"},
        {"figure": "Nationwide", "label": "Installation and service coverage"},
    ],
}

CONTACT_PAGE = {
    "h1": "Contact us",
    "lead": "Tell us what you need and an engineer will answer.",
    "form_note": "We answer quote requests on weekdays within office hours.",
}

# User interface strings. Instructional register, one rule per line.
UI = {
    "quote_button": "Request a quote",
    "quote_heading": "Request a quote",
    "quote_intro": "Fill in the form and we will send a price and a lead time.",
    "quote_intro_direct": "Send the model and what the station needs and we will come back with a price and a lead time.",
    "find_label": "Find a product",
    "find_placeholder": "Model, brand or category",
    "find_none": "Nothing matches that.",
    "field_name": "Name",
    "field_company": "Company or station",
    "field_email": "Email",
    "field_phone": "Contact number",
    "field_product": "Product",
    "field_message": "Message",
    "field_required": "required",
    "submit": "Send request",
    "nav_products": "Equipment",
    "nav_brands": "Brands",
    "nav_services": "Services",
    "nav_company": "Company",
    "nav_customers": "Customers",
    "nav_contact": "Contact",
    "back_to": "Back to",
    "view_all": "View all",
    "products_in": "Products in",
    "related": "More from",
    "spec_heading": "Features",
    "faq_heading": "Manufacturer FAQ",
    "image_pending": "Photograph to follow",
    "notfound_h1": "Page not found",
    "notfound_body": "Use the equipment menu to find the product.",
    "thanks_h1": "Request received",
    "thanks_body": "We will reply to the email address you gave.",
}
