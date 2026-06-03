from odoo import models, fields

class BlogPost(models.Model):
    _name = 'custom_blog.post'
    _description = 'Blog Post'

    name = fields.Char(string='Title', required=True)
    content = fields.Html(string='Content')
    image = fields.Image(string="Image")
    image_position = fields.Selection([
        ('top', 'Top'),
        ('bottom', 'Bottom'),
        ('left', 'Left'),
        ('right', 'Right')
    ], string='Image Position', default='top')
    active = fields.Boolean(string='Active', default=True)
