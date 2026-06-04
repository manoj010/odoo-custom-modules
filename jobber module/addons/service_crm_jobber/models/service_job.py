from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ServiceJob(models.Model):
    _name = "service.job"
    _description = "Service Job"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheduled_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    sequence = fields.Char(readonly=True, copy=False, default=lambda self: _("New"), tracking=True)
    quote_id = fields.Many2one("service.quote", tracking=True)
    request_id = fields.Many2one("service.request", tracking=True)
    partner_id = fields.Many2one("res.partner", string="Client", required=True, tracking=True)
    property_address = fields.Text()
    job_type = fields.Selection(
        [("one_off", "One-off"), ("recurring", "Recurring")],
        default="one_off",
        required=True,
    )
    scheduled_date = fields.Date(tracking=True)
    start_time = fields.Float()
    end_time = fields.Float()
    assigned_user_id = fields.Many2one("res.users", string="Assigned To", tracking=True)
    status = fields.Selection(
        [
            ("unscheduled", "Unscheduled"),
            ("upcoming", "Upcoming"),
            ("today", "Today"),
            ("late", "Late"),
            ("action_required", "Action Required"),
            ("requires_invoicing", "Requires Invoicing"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="unscheduled",
        required=True,
        tracking=True,
    )
    visit_instructions = fields.Text()
    line_ids = fields.One2many("service.job.line", "job_id", copy=True)
    total_amount = fields.Monetary(compute="_compute_total_amount", store=True, currency_field="currency_id")
    notes = fields.Text()
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    @api.depends("sequence")
    def _compute_name(self):
        for job in self:
            job.name = job.sequence if job.sequence != _("New") else _("New Job")

    @api.depends("line_ids.subtotal")
    def _compute_total_amount(self):
        for job in self:
            job.total_amount = sum(job.line_ids.mapped("subtotal"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("sequence", _("New")) == _("New"):
                vals["sequence"] = self.env["ir.sequence"].next_by_code("service.job") or _("New")
        return super().create(vals_list)

    def action_schedule(self):
        for job in self:
            if not job.scheduled_date:
                raise UserError(_("Set a scheduled date before scheduling the job."))
            job.status = "upcoming"
        return True

    def action_complete(self):
        self.write({"status": "requires_invoicing"})
        return True

    def action_create_invoice(self):
        self.ensure_one()
        if self.status not in ("requires_invoicing", "completed"):
            raise UserError(_("Complete the job before creating an invoice."))
        invoice = self.env["service.invoice"].create(
            {
                "job_id": self.id,
                "quote_id": self.quote_id.id,
                "partner_id": self.partner_id.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_name": line.product_name,
                            "description": line.description,
                            "quantity": line.quantity,
                            "unit_price": line.unit_price,
                        },
                    )
                    for line in self.line_ids
                ],
                "client_message": self.notes,
            }
        )
        self.status = "completed"
        return {
            "type": "ir.actions.act_window",
            "name": _("Invoice"),
            "res_model": "service.invoice",
            "view_mode": "form",
            "res_id": invoice.id,
        }

    def action_cancel(self):
        self.write({"status": "cancelled"})
        return True


class ServiceJobLine(models.Model):
    _name = "service.job.line"
    _description = "Service Job Line"

    job_id = fields.Many2one("service.job", required=True, ondelete="cascade")
    product_name = fields.Char(required=True)
    description = fields.Text()
    quantity = fields.Float(default=1.0)
    unit_price = fields.Monetary(currency_field="currency_id")
    subtotal = fields.Monetary(compute="_compute_subtotal", store=True, currency_field="currency_id")
    currency_id = fields.Many2one(related="job_id.currency_id", store=True)

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
