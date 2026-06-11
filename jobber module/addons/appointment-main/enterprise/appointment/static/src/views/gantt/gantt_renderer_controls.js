import { GanttRendererControls } from "@gantt_view/gantt_renderer_controls";

export class AppointmentBookingGanttRendererControls extends GanttRendererControls {
    static template = "appointment.AppointmentBookingGanttRendererControls";
    static props = [...GanttRendererControls.props, "onClickAddLeave", "showAddLeaveButton"];
}
