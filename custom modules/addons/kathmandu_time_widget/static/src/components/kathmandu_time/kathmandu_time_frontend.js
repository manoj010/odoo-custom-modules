/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { getKathmanduTime } from "./kathmandu_time_utils";

publicWidget.registry.KathmanduTimeSnippet = publicWidget.Widget.extend({
    selector: '.s_kathmandu_time',

    start: function () {
        this._super.apply(this, arguments);
        
        this.timeDisplay = this.el.querySelector('.ktm-time-display');
        
        if (this.timeDisplay) {
            this.timeDisplay.textContent = getKathmanduTime();
            this.interval = setInterval(() => {
                this.timeDisplay.textContent = getKathmanduTime();
            }, 1000);
        }
    },

    destroy: function () {
        if (this.interval) {
            clearInterval(this.interval);
        }
        this._super.apply(this, arguments);
    }
});
