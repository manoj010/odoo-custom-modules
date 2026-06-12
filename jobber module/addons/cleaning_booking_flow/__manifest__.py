{
    "name": "Sparkle Booking Flow",
    "summary": "Full-screen website booking flow for cleaning services",
    "version": "18.0.1.0.0",
    "category": "Website",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": [
        "web",
        "website",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/cleaning_booking_views.xml",
        "views/website_templates.xml",
    ],
    "post_init_hook": "post_init_hook",
    "assets": {
        "web.assets_frontend": [
            "cleaning_booking_flow/static/src/booking_flow/booking_flow.scss",
            "cleaning_booking_flow/static/src/booking_flow/booking_flow.xml",
            "cleaning_booking_flow/static/src/booking_flow/booking_flow.js",
        ],
    },
    "application": True,
    "installable": True,
}
