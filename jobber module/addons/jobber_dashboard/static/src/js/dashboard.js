/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class JobberDashboard extends Component {
    static template = "jobber_dashboard.Dashboard";

    setup() {
        this.action = useService("action");
        this.state = useState({
            loading: true,
            data: {},
        });

        onWillStart(async () => {
            this.state.data = await rpc("/jobber_dashboard/data", {});
            this.state.loading = false;
        });
    }

    openAction(actionId) {
        if (actionId) {
            this.action.doAction(actionId);
        }
    }
}

registry.category("actions").add("jobber_dashboard.dashboard", JobberDashboard);
