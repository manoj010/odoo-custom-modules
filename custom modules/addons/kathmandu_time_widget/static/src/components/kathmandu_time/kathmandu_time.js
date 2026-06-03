/** @odoo-module **/

import { Component, useState, onWillStart, onWillDestroy } from "@odoo/owl";
import { registry } from "@web/core/registry";

import { getKathmanduTime } from "./kathmandu_time_utils";

export class KathmanduTimeWidget extends Component {
    setup() {
        this.state = useState({ time: getKathmanduTime() });
        
        onWillStart(() => {
            this.interval = setInterval(() => {
                this.state.time = getKathmanduTime();
            }, 1000);
        });

        onWillDestroy(() => {
            if (this.interval) {
                clearInterval(this.interval);
            }
        });
    }
}

KathmanduTimeWidget.template = "kathmandu_time_widget.KathmanduTimeWidget";

export const systrayItem = {
    Component: KathmanduTimeWidget,
};

registry.category("systray").add("kathmandu_time_widget.KathmanduTimeWidget", systrayItem, { sequence: 100 });
