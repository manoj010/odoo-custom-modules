{
    "name": "Service CRM Jobber",
    "summary": "Jobber-style service business CRM workflow",
    "version": "18.0.1.0.0",
    "category": "Services",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
        "website",
        "mail",
        "contacts",
        "sale_management",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence_data.xml",
        "views/service_request_views.xml",
        "views/service_quote_views.xml",
        "views/service_job_views.xml",
        "views/service_invoice_views.xml",
        "views/service_dashboard_views.xml",
        "views/service_menu_views.xml",
        "views/website_templates.xml",
        "views/website_snippets.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "service_crm_jobber/static/src/scss/backend.scss",
        ],
        "web.assets_frontend": [
            "service_crm_jobber/static/src/scss/request_snippet.scss",
            "service_crm_jobber/static/src/js/request_snippet.js",
        ],
    },
    "application": True,
    "installable": True,
}
