from odoo import http, _
from odoo.http import request


class ServiceCRMWebsiteRequest(http.Controller):
    @http.route(
        "/service-crm/request/submit",
        type="http",
        auth="public",
        website=True,
        methods=["GET", "POST"],
        csrf=False,
    )
    def submit_service_request(self, **post):
        if request.httprequest.method == "GET":
            return request.redirect("/")

        full_name = (post.get("full_name") or "").strip()
        email = (post.get("email") or "").strip()
        message = (post.get("message") or "").strip()
        phone = (post.get("phone") or "").strip()

        if not full_name or not email or not message:
            return request.redirect("/service-crm/request/thank-you?error=missing")

        partner = self._find_or_create_partner(post, full_name, email, phone)
        service_type = post.get("service_type") or "other"
        valid_service_types = dict(request.env["service.request"]._fields["service_type"].selection)
        if service_type not in valid_service_types:
            service_type = "other"

        request.env["service.request"].sudo().create(
            {
                "name": _("Service request from %s") % full_name,
                "partner_id": partner.id,
                "customer_name": full_name,
                "email": email,
                "phone": phone,
                "company_name": (post.get("company_name") or "").strip(),
                "service_type": service_type,
                "property_address": (post.get("property_address") or "").strip(),
                "message": message,
                "source": "website",
                "status": "new",
            }
        )
        return request.redirect("/service-crm/request/thank-you")

    @http.route(
        "/service-crm/request/thank-you",
        type="http",
        auth="public",
        website=True,
    )
    def request_thank_you(self, **kw):
        return request.render(
            "service_crm_jobber.service_request_thank_you",
            {"has_error": bool(kw.get("error"))},
        )

    def _find_or_create_partner(self, post, full_name, email, phone):
        Partner = request.env["res.partner"].sudo()
        domain = []
        if email and phone:
            domain = ["|", ("email", "=ilike", email), ("phone", "=", phone)]
        elif email:
            domain = [("email", "=ilike", email)]
        elif phone:
            domain = [("phone", "=", phone)]
        partner = Partner.search(domain, limit=1) if domain else Partner.browse()
        if partner:
            return partner
        return Partner.create(
            {
                "name": full_name,
                "email": email,
                "phone": phone,
                "company_name": (post.get("company_name") or "").strip(),
                "street": (post.get("property_address") or "").strip(),
                "customer_rank": 1,
            }
        )
