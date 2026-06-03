from odoo import http
from odoo.http import request


class BookingController(http.Controller):
    @http.route("/booking/<string:slug>", type="http", auth="public", website=True)
    def booking_page(self, slug, **kwargs):
        flow = request.env["booking.flow"].sudo().search(
            request.env["booking.flow"]._get_public_flow_domain(slug),
            limit=1,
        )
        if not flow:
            return request.not_found()
        return request.render(
            "booking_flow_builder.booking_flow_page",
            {"flow": flow},
        )

    @http.route(
        "/booking/api/flow/<string:slug>",
        type="json",
        auth="public",
        website=True,
        csrf=False,
    )
    def booking_flow_data(self, slug, **kwargs):
        flow = request.env["booking.flow"].sudo().search(
            request.env["booking.flow"]._get_public_flow_domain(slug),
            limit=1,
        )
        if not flow:
            return {"success": False, "error": "Flow not found."}
        steps = flow.step_ids.filtered("active").sorted(lambda step: (step.sequence, step.id))
        return {
            "success": True,
            "flow": {
                "id": flow.id,
                "name": flow.name,
                "slug": flow.slug,
                "currency": {
                    "id": flow.currency_id.id,
                    "symbol": flow.currency_id.symbol,
                    "position": flow.currency_id.position,
                },
                "steps": [
                    {
                        "id": step.id,
                        "title": step.title,
                        "subtitle": step.subtitle or "",
                        "step_type": step.step_type,
                        "required": step.required,
                        "options": [
                            {
                                "id": option.id,
                                "label": option.label,
                                "image_url": "/web/image/booking.flow.option/%s/image" % option.id
                                if option.image
                                else "",
                                "pricing_type": option.pricing_type,
                                "pricing_value": option.pricing_value,
                            }
                            for option in step.option_ids.filtered("active").sorted(
                                lambda option: (option.sequence, option.id)
                            )
                        ],
                    }
                    for step in steps
                ],
            },
        }

    @http.route(
        "/booking/api/submit",
        type="json",
        auth="public",
        website=True,
        csrf=False,
    )
    def booking_submit(self, **payload):
        flow_id = payload.get("flow_id")
        answers = payload.get("answers") or []
        flow = request.env["booking.flow"].sudo().browse(int(flow_id or 0)).exists()
        if not flow or not flow.active:
            return {"success": False, "error": "Invalid booking flow."}

        session_model = request.env["booking.session"].sudo()
        partner = session_model._partner_from_customer(payload)
        session = session_model.create(
            {
                "flow_id": flow.id,
                "partner_id": partner.id if partner else False,
                "state": "completed",
                "current_step_id": False,
                "currency_id": flow.currency_id.id,
                "total_price": float(payload.get("total_price") or 0.0),
                "customer_name": payload.get("customer_name"),
                "customer_email": payload.get("customer_email"),
                "customer_phone": payload.get("customer_phone"),
                "customer_note": payload.get("customer_note"),
            }
        )

        answer_model = request.env["booking.session.answer"].sudo()
        for answer in answers:
            step = request.env["booking.flow.step"].sudo().browse(int(answer.get("step_id") or 0)).exists()
            if not step or step.flow_id.id != flow.id:
                continue
            option_ids = answer.get("option_ids") or []
            if answer.get("option_id"):
                option_ids.append(answer.get("option_id"))
            if option_ids:
                for option_id in option_ids:
                    option = request.env["booking.flow.option"].sudo().browse(int(option_id or 0)).exists()
                    if option and option.step_id.id == step.id:
                        answer_model.create(
                            {
                                "session_id": session.id,
                                "step_id": step.id,
                                "option_id": option.id,
                            }
                        )
            if answer.get("text_value"):
                answer_model.create(
                    {
                        "session_id": session.id,
                        "step_id": step.id,
                        "text_value": answer.get("text_value"),
                    }
                )
            if answer.get("numeric_value") not in (None, ""):
                answer_model.create(
                    {
                        "session_id": session.id,
                        "step_id": step.id,
                        "numeric_value": float(answer.get("numeric_value") or 0.0),
                    }
                )

        session_model._create_sale_order_for_session(session)
        return {"success": True, "session_id": session.id}
