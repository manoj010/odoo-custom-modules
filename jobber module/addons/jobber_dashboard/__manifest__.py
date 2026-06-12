{
    "name": "Jobber Dashboard",
    "summary": "Jobber-style service dashboard using standard Odoo apps",
    "version": "18.0.1.0.0",
    "category": "Services",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": [
        "account",
        "calendar",
        "contacts",
        "crm",
        "project",
        "sale_management",
        "web",
    ],
    "data": [
        "views/dashboard_templates.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "jobber_dashboard/static/src/js/dashboard.js",
            "jobber_dashboard/static/src/xml/dashboard.xml",
            "jobber_dashboard/static/src/scss/dashboard.scss",
        ],
    },
    "application": True,
    "installable": True,
}
