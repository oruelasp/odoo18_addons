/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { debounce } from "@web/core/utils/timing";

const { Component, onWillStart, onWillUpdateProps, useState } = owl;

export class ProductionMatrixWidget extends Component {
    static template = "xtq_mrp_matrix_form.ProductionMatrixWidget";
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ axis_x: { name: "X", values: [] }, axis_y: { name: "Y", values: [] }, quantities: {}, rowTotals: {}, colTotals: {}, grandTotal: 0, error: null, });
        onWillStart(() => this.loadMatrixData());
        onWillUpdateProps((nextProps) => this.loadMatrixData(nextProps));
        this.debouncedSave = debounce(this.saveMatrixState, 400);
    }

    resetStateOnError(errorMessage) { this.state.error = errorMessage; this.state.axis_x = { name: "X", values: [] }; this.state.axis_y = { name: "Y", values: [] }; this.state.quantities = {}; this.calculateTotals(); }
    async loadMatrixData(props = this.props) {
        const record = props.record;
        if (record.isNew) { this.resetStateOnError(null); return; }
        try {
            const data = await this.orm.call(record.resModel, "get_matrix_data", [record.resId]);
            if (!data || data.error) { this.resetStateOnError(data ? data.error : "No se recibieron datos del servidor."); } 
            else {
                this.state.axis_x = data.axis_x;
                this.state.axis_y = data.axis_y;
                this.state.quantities = data.quantities;
                this.state.error = null;
                this.calculateTotals();
            }
        } catch (e) { this.resetStateOnError("No se pudo cargar la información de la matriz."); console.error(e); }
    }
    getQuantity(yValueId, xValueId) { return this.state.quantities[`${yValueId}-${xValueId}`] || 0; }
    calculateTotals() {
        this.state.rowTotals = {}; this.state.colTotals = {}; this.state.grandTotal = 0;
        if (!this.state.axis_y.values || !this.state.axis_x.values) return;
        for (const y_val of this.state.axis_y.values) { this.state.rowTotals[y_val.id] = this.state.axis_x.values.reduce((sum, x_val) => sum + this.getQuantity(y_val.id, x_val.id), 0); }
        for (const x_val of this.state.axis_x.values) { this.state.colTotals[x_val.id] = this.state.axis_y.values.reduce((sum, y_val) => sum + this.getQuantity(y_val.id, x_val.id), 0); }
        this.state.grandTotal = Object.values(this.state.colTotals).reduce((sum, val) => sum + val, 0);
    }

    _onQuantityChange(ev, yValueId, xValueId) {
        const value = parseFloat(ev.target.value) || 0;
        this.state.quantities[`${yValueId}-${xValueId}`] = value;
        this.calculateTotals();
        this.debouncedSave();
    }

    async saveMatrixState() {
        const lines = [];
        for (const [key, qty] of Object.entries(this.state.quantities)) {
            if (qty > 0) {
                const [yValueId, xValueId] = key.split('-').map(Number);
                lines.push({ yValueId, xValueId, quantity: qty });
            }
        }
        const jsonData = JSON.stringify(lines);
        
        await this.props.record.update({ matrix_data_json: jsonData });
    }
}

registry.category("fields").add("production_matrix_xy", {
    component: ProductionMatrixWidget,
});