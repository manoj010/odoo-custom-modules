from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ServiceRequest(models.Model):
    _name = "service.request"
    _description = "Service Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "requested_date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    sequence = fields.Char(
        readonly=True,
        copy=False,
        default=lambda self: _("New"),
        tracking=True,
    )
    partner_id = fields.Many2one("res.partner", string="Customer", tracking=True)
    customer_name = fields.Char(tracking=True)
    email = fields.Char()
    phone = fields.Char()
    company_name = fields.Char()
    service_type = fields.Selection(
        [
            ("cleaning", "Cleaning"),
            ("lawn_care", "Lawn Care"),
            ("plumbing", "Plumbing"),
            ("electrical", "Electrical"),
            ("hvac", "HVAC"),
            ("maintenance", "Maintenance"),
            ("other", "Other"),
        ],
        default="other",
        tracking=True,
    )
    property_address = fields.Text()
    message = fields.Text()
    requested_date = fields.Date(default=fields.Date.context_today, tracking=True)
    salesperson_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        tracking=True,
    )
    status = fields.Selection(
        [
            ("new", "New"),
            ("assessment_complete", "Assessment Complete"),
            ("quoted", "Quoted"),
            ("converted", "Converted"),
            ("lost", "Lost"),
        ],
        default="new",
        required=True,
        tracking=True,
    )
    source = fields.Selection(
        [("website", "Website"), ("manual", "Manual")],
        default="manual",
        required=True,
        tracking=True,
    )
    quote_id = fields.Many2one("service.quote", readonly=True, copy=False)
    job_id = fields.Many2one("service.job", readonly=True, copy=False)
    color = fields.Integer()
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("sequence", _("New")) == _("New"):
                vals["sequence"] = self.env["ir.sequence"].next_by_code("service.request") or _("New")
            if not vals.get("name"):
                vals["name"] = vals["sequence"]
        return super().create(vals_list)

    def action_convert_to_client(self):
        for request in self:
            if request.partner_id:
                continue
            if not request.customer_name and not request.email:
                raise UserError(_("Add a customer name or email before creating a client."))
            partner_vals = {
                "name": request.customer_name or request.email,
                "email": request.email,
                "phone": request.phone,
                "company_name": request.company_name,
                "street": request.property_address,
                "customer_rank": 1,
            }
            request.partner_id = self.env["res.partner"].create(partner_vals)
        return True

    def action_create_quote(self):
        self.ensure_one()
        if not self.partner_id:
            self.action_convert_to_client()
        quote = self.env["service.quote"].create(
            {
                "request_id": self.id,
                "partner_id": self.partner_id.id,
                "property_address": self.property_address,
                "salesperson_id": self.salesperson_id.id,
                "notes": self.message,
            }
        )
        self.write({"quote_id": quote.id, "status": "quoted"})
        return {
            "type": "ir.actions.act_window",
            "name": _("Quote"),
            "res_model": "service.quote",
            "view_mode": "form",
            "res_id": quote.id,
        }

    def action_mark_lost(self):
        self.write({"status": "lost"})
        return True
