{
    'name': 'Kathmandu Time Widget',
    'version': '18.0.1.0.0',
    'summary': 'Website snippet to show the time in Kathmandu',
    'description': """
        This module provides a website building block (snippet) that displays the live time in Kathmandu, Nepal.
    """,
    'category': 'Website',
    'author': 'Your Name',
    'depends': ['website'],
    'data': [
        'views/snippets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'kathmandu_time_widget/static/src/components/kathmandu_time/kathmandu_time_utils.js',
            'kathmandu_time_widget/static/src/components/kathmandu_time/kathmandu_time.js',
            'kathmandu_time_widget/static/src/components/kathmandu_time/kathmandu_time.xml',
        ],
        'web.assets_frontend': [
            'kathmandu_time_widget/static/src/components/kathmandu_time/kathmandu_time_utils.js',
            'kathmandu_time_widget/static/src/components/kathmandu_time/kathmandu_time_frontend.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
