/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ServiceCRMRequestForm = publicWidget.Widget.extend({
    selector: ".o_service_crm_request_form",
    events: {
        submit: "_onSubmit",
    },

    _onSubmit(ev) {
        const requiredFields = this.el.querySelectorAll("[required]");
        let isValid = true;
        requiredFields.forEach((field) => {
            const valid = Boolean(field.value && field.value.trim());
            field.classList.toggle("is-invalid", !valid);
            isValid = isValid && valid;
        });
        if (!isValid) {
            ev.preventDefault();
            return;
        }
        const button = this.el.querySelector("button[type='submit']");
        if (button) {
            button.disabled = true;
            button.classList.add("disabled");
        }
    },
});
