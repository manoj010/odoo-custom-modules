/** @odoo-module **/

import { whenReady } from "@odoo/owl";
import { mountComponent } from "@web/env";
import { BookingRoot } from "./components/booking_root";

whenReady(async () => {
    const targets = document.querySelectorAll(".o_booking_flow_app[data-flow-slug]");
    for (const target of targets) {
        if (target.dataset.bookingMounted) {
            continue;
        }
        target.dataset.bookingMounted = "1";
        await mountComponent(BookingRoot, target, {
            props: {
                slug: target.dataset.flowSlug,
            },
        });
    }
});
