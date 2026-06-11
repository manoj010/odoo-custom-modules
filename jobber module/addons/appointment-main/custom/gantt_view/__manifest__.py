# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Gantt View',
    'category': 'Hidden',
    'description': """
Odoo Gantt View.
=============================

    """,
    'version': '2.0',
    'depends': ['web'],
    'assets': {
        'web._assets_primary_variables': [
            'gantt_view/static/src/gantt_view.variables.scss',
        ],
        'web.assets_backend_lazy': [
            'gantt_view/static/src/**/*',

            # Don't include dark mode files in light mode
            ('remove', 'gantt_view/static/src/**/*.dark.scss'),
        ],
        'web.assets_backend_lazy_dark': [
            'gantt_view/static/src/**/*.dark.scss',
        ],
        # 'web.assets_unit_tests': [
        #     'web_gantt/static/tests/**/*',
        # ],
        # ========= Dark Mode =========
        "web.dark_mode_variables": [
            ('before', 'backend_enterprise_theme/static/src/**/*.variables.scss', 'gantt_view/static/src/**/*.variables.dark.scss'),
        ],
    },
    # 'auto_install': True,
    'license': 'LGPL-3',}
