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
        
        this.state = useState({
            axis_x: { name: "X", values: [] },
            axis_y: { name: "Y", values: [] },
            quantities: {}, 
            rowTotals: {},
            colTotals: {},
            grandTotal: 0,
            error: null,
            matrix_state: 'pending',
            cellTemplate: 'default', // plantilla reactiva
        });
        
        onWillStart(() => this.loadMatrixData());
        onWillUpdateProps((nextProps) => this.loadMatrixData(nextProps));
        this.debouncedSave = debounce(this.saveMatrixState, 400);
    }

    resetStateOnError(errorMessage) {
        this.state.error = errorMessage;
        this.state.axis_x = { name: "X", values: [] };
        this.state.axis_y = { name: "Y", values: [] };
        this.state.quantities = {};
        this.calculateTotals();
    }

    async loadMatrixData(props = this.props) {
        // Configuración basada en el nombre del campo
        if (props.name === 'distribution_line_ids') {
            this.jsonField = 'distribution_data_json';
            this.matrixType = 'distribution';
            this.state.cellTemplate = 'single_qty';
        } else {
            this.jsonField = 'matrix_data_json';
            this.matrixType = 'programming';
            this.state.cellTemplate = 'default';
        }

        const record = props.record;

        // Forzar el reseteo del estado antes de cada carga de datos.
        this.state.axis_x = { name: "X", values: [] };
        this.state.axis_y = { name: "Y", values: [] };
        this.state.quantities = {};
        this.state.matrix_state = record.data.matrix_state || 'pending';

        if (record.isNew) {
            this.resetStateOnError(null);
            return;
        }
        try {
            const data = await this.orm.call(record.resModel, "get_matrix_data", [record.resId], {
                matrix_type: this.matrixType 
            });
            if (!data || data.error) {
                this.resetStateOnError(data ? data.error : "No se recibieron datos del servidor.");
            } else {
                this.state.axis_x = data.axis_x;
                this.state.axis_y = data.axis_y;
                this.state.quantities = data.quantities;
                this.state.error = null;
                this.state.matrix_state = data.matrix_state;
                this.calculateTotals();
            }
        } catch (e) {
            this.resetStateOnError("No se pudo cargar la información de la matriz.");
            console.error(e);
        }
    }

    // Adaptar para obtener product_qty o qty_producing
    getQuantity(yValueId, xValueId, type) {
        const key = `${yValueId}-${xValueId}`;
        const cellData = this.state.quantities[key];
        if (!cellData) {
            return 0;
        }
        return type === 'product_qty' ? cellData.product_qty : (cellData.qty_producing || 0);
    }

    calculateTotals() {
        const totals = {
            rows: {},
            cols: {},
            grand_total: { product_qty: 0, qty_producing: 0 }
        };

        for (const y_val of this.state.axis_y.values) {
            totals.rows[y_val.id] = { product_qty: 0, qty_producing: 0 };
        }
        for (const x_val of this.state.axis_x.values) {
            totals.cols[x_val.id] = { product_qty: 0, qty_producing: 0 };
        }

        for (const y_val of this.state.axis_y.values) {
            for (const x_val of this.state.axis_x.values) {
                const key = `${y_val.id}-${x_val.id}`;
                const cell = this.state.quantities[key] || { product_qty: 0, qty_producing: 0 };
                
                totals.rows[y_val.id].product_qty += cell.product_qty;
                totals.rows[y_val.id].qty_producing += cell.qty_producing || 0;
                
                totals.cols[x_val.id].product_qty += cell.product_qty;
                totals.cols[x_val.id].qty_producing += cell.qty_producing || 0;

                totals.grand_total.product_qty += cell.product_qty;
                totals.grand_total.qty_producing += cell.qty_producing || 0;
            }
        }

        this.state.totals = totals;
    }

    _onQtyChange = (ev, yValueId, xValueId) => {
        // Método unificado para la matriz de distribución
        const value = parseFloat(ev.target.value) || 0;
        const key = `${yValueId}-${xValueId}`;
        
        if (!this.state.quantities[key]) {
            this.state.quantities[key] = { product_qty: 0, qty_producing: 0 };
        }
        // Para la matriz de distribución, asumimos que se modifica product_qty
        this.state.quantities[key].product_qty = value;
        
        this.calculateTotals();
        this.debouncedSave();
    }

    _onQtyProducingChange = (ev, yValueId, xValueId) => {
        const value = parseFloat(ev.target.value) || 0;
        const key = `${yValueId}-${xValueId}`;
        this.state.quantities[key].qty_producing = value;
        this.calculateTotals();
        this.debouncedSave();
    }

    _onProductQtyChange = (ev, yValueId, xValueId) => {
        const value = parseFloat(ev.target.value) || 0;
        const key = `${yValueId}-${xValueId}`;
        
        if (!this.state.quantities[key]) {
            this.state.quantities[key] = { product_qty: 0, qty_producing: 0 };
        }

        this.state.quantities[key].product_qty = value;
        
        this.calculateTotals();
        this.debouncedSave();
    }

    async saveMatrixState() {
        const lines = [];
        for (const [key, cellData] of Object.entries(this.state.quantities)) {
            const [yValueId, xValueId] = key.split('-').map(Number);
            
            // CORRECCIÓN 2: Guardado inteligente basado en el tipo de matriz.
            const lineData = {
                yValueId: yValueId,
                xValueId: xValueId,
                product_qty: cellData.product_qty || 0,
            };
            // Solo añadimos qty_producing si estamos en la matriz de programación.
            if (this.matrixType === 'programming') {
                lineData.qty_producing = cellData.qty_producing || 0;
            }
            lines.push(lineData);
        }
        const jsonData = JSON.stringify(lines);

        // Usar el campo JSON dinámico
        await this.props.record.update({ [this.jsonField]: jsonData });
    }

    // Método para determinar si qty_producing es editable
    isQtyProducingEditable() {
        return this.state.matrix_state === 'planned';
    }

    // Método para determinar si product_qty es editable
    isProductQtyEditable() {
        return this.state.matrix_state === 'pending';
    }
}

ProductionMatrixWidget.template = "xtq_mrp_matrix_form.ProductionMatrixWidget";
ProductionMatrixWidget.props = {
    ...standardFieldProps,
};

registry.category("fields").add("production_matrix_widget", {
    component: ProductionMatrixWidget,
});