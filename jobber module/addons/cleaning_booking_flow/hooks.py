DEFAULT_SERVICES = [
    {"name": "Carpet & Upholstery Cleaning", "description": "Professional steam and dry cleaning.", "icon_class": "fa fa-object-group", "price": 45.0, "appointment_duration": 1.5, "sequence": 10, "is_cleaning_service": True, "appointment_tz": "UTC",},
    {"name": "Water Damage Restoration", "description": "Professional steam and dry cleaning.", "icon_class": "fa fa-tint", "price": 85.0, "appointment_duration": 2.0, "sequence": 20, "is_cleaning_service": True, "appointment_tz": "UTC",},
    {"name": "End Of Lease Cleaning", "description": "Professional steam and dry cleaning.", "icon_class": "fa fa-paint-brush", "price": 120.0, "appointment_duration": 3.0, "sequence": 30, "is_cleaning_service": True, "appointment_tz": "UTC",},
    {"name": "Commercial Premises Cleaning", "description": "Professional steam and dry cleaning.", "icon_class": "fa fa-building-o", "price": 95.0, "appointment_duration": 2.5, "sequence": 40, "is_cleaning_service": True, "appointment_tz": "UTC",},
    {"name": "Mould Removal & Remediation", "description": "Professional steam and dry cleaning.", "icon_class": "fa fa-fire-extinguisher", "price": 75.0, "appointment_duration": 2.0, "sequence": 50, "is_cleaning_service": True, "appointment_tz": "UTC",},
    {"name": "Builders & Post-Reno Cleaning", "description": "Professional steam and dry cleaning.", "icon_class": "fa fa-truck", "price": 110.0, "appointment_duration": 3.0, "sequence": 60, "is_cleaning_service": True, "appointment_tz": "UTC",},
]

def _seed_data(env):
    import logging
    _logger = logging.getLogger(__name__)
    
    Service = env["appointment.type"].sudo()
    for default in DEFAULT_SERVICES:
        existing = Service.search([
            ("name", "=", default["name"]),
            ("is_cleaning_service", "=", True)
        ], limit=1)
        if not existing:
            _logger.info("Creating service: %s", default["name"])
            Service.create(default)

    Availability = env["cleaning.booking.availability"].sudo()
    for service in Service.search([("is_cleaning_service", "=", True)]):
        existing = Availability.search_count([("service_id", "=", service.id)])
        if not existing:
            for weekday in ["0", "1", "2", "3", "4", "5"]:
                Availability.create({
                    "service_id": service.id,
                    "weekday": weekday,
                    "start_time": 9.0,
                    "end_time": 18.0,
                    "slot_interval_minutes": 60,
                })

def post_init_hook(env):
    _seed_data(env)
