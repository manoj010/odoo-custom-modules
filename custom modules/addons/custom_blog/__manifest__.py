{
    'name': 'Custom Blog',
    'version': '18.0.1.0.0',
    'summary': 'A simple custom blog module',
    'description': """
        This module provides a simple way to create and manage blog posts.
    """,
    'category': 'Website',
    'author': 'Your Name',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/blog_post_views.xml',
        'views/blog_menus.xml',
        'views/blog_templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
