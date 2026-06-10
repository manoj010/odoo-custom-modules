DEFAULT_SERVICES = [
    {
        "name": "Carpet & Upholstery Cleaning",
        "description": "Professional steam and dry cleaning.",
        "icon_class": "fa fa-object-group",
        "price": 45.0,
        "duration_minutes": 90,
        "sequence": 10,
    },
    {
        "name": "Water Damage Restoration",
        "description": "Professional steam and dry cleaning.",
        "icon_class": "fa fa-tint",
        "price": 85.0,
        "duration_minutes": 120,
        "sequence": 20,
    },
    {
        "name": "End Of Lease Cleaning",
        "description": "Professional steam and dry cleaning.",
        "icon_class": "fa fa-paint-brush",
        "price": 120.0,
        "duration_minutes": 180,
        "sequence": 30,
    },
    {
        "name": "Commercial Premises Cleaning",
        "description": "Professional steam and dry cleaning.",
        "icon_class": "fa fa-building-o",
        "price": 95.0,
        "duration_minutes": 150,
        "sequence": 40,
    },
    {
        "name": "Mould Removal & Remediation",
        "description": "Professional steam and dry cleaning.",
        "icon_class": "fa fa-fire-extinguisher",
        "price": 75.0,
        "duration_minutes": 120,
        "sequence": 50,
    },
    {
        "name": "Builders & Post-Reno Cleaning",
        "description": "Professional steam and dry cleaning.",
        "icon_class": "fa fa-truck",
        "price": 110.0,
        "duration_minutes": 180,
        "sequence": 60,
    },
]


def post_init_hook(env):
    Service = env["cleaning.booking.service"].sudo()
    if not Service.search_count([]):
        Service.create(DEFAULT_SERVICES)

    Availability = env["cleaning.booking.availability"].sudo()
    if Availability.search_count([]):
        return

    rules = []
    for service in Service.search([]):
        for weekday in ["0", "1", "2", "3", "4", "5"]:
            rules.append(
                {
                    "service_id": service.id,
                    "weekday": weekday,
                    "start_time": 9.0,
                    "end_time": 18.0,
                    "slot_interval_minutes": 60,
                }
            )
    if rules:
        Availability.create(rules)
