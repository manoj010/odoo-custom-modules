from odoo import http
from odoo.http import request

class CustomBlogController(http.Controller):

    @http.route('/custom_blog', type='http', auth='public', website=True)
    def blog_post_list(self, **kw):
        # Fetch all active blog posts
        posts = request.env['custom_blog.post'].sudo().search([('active', '=', True)])
        return request.render('custom_blog.blog_post_list', {
            'posts': posts,
        })

    @http.route('/custom_blog/<model("custom_blog.post"):post>', type='http', auth='public', website=True)
    def blog_post_detail(self, post, **kw):
        # The 'post' parameter is already an active record because of <model("...")>
        return request.render('custom_blog.blog_post_detail', {
            'post': post,
        })
