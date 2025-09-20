/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { listView } from "@web/views/list/list_view"; // Importación clave
import { onWillStart, onWillUpdateProps, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class StockQuantListWithAttributesRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = useState({
            attributeData: {},
            attributeHeaders: [],
            // La comprobación ahora es más robusta
            showAttributes: this.props.arch.attrs.js_class === 'stock_quant_list_with_attributes',
        });

        onWillStart(async () => {
            if (this.state.showAttributes) {
                await this._fetchAttributeData();
                this._updateColumnsVisibility();
            }
        });

        onWillUpdateProps(async (nextProps) => {
            if (this.state.showAttributes) {
                await this._fetchAttributeData(nextProps);
                this._updateColumnsVisibility(nextProps);
            }
        });
    }

    async _fetchAttributeData(props = this.props) {
        const lotIds = props.list.records.map(rec => rec.data.lot_id && rec.data.lot_id[0]).filter(id => id);
        if (lotIds.length === 0) {
            this.state.attributeData = {};
            this.state.attributeHeaders = [];
            return;
        }

        const data = await this.orm.call(
            'stock.lot',
            'get_attributes_for_lots_view',
            [lotIds]
        );
        this.state.attributeData = data.data;
        this.state.attributeHeaders = data.headers;
    }
    
    _updateColumnsVisibility(props = this.props) {
        if (!this.state.showAttributes) return;

        // Itera sobre las columnas definidas en el arch para decidir su visibilidad
        props.list.columns.forEach(col => {
            if (col.name.startsWith('x_attr_')) {
                col.optional = this.state.attributeHeaders.includes(col.string) ? false : 'hide';
            }
        });
    }

    // Sobrescribimos get cells para inyectar los datos de los atributos
    get cells() {
        const originalCells = super.cells;
        if (!this.state.showAttributes) {
            return originalCells;
        }

        return originalCells.map(row => {
            const lotId = row.record.data.lot_id && row.record.data.lot_id[0];
            if (lotId && this.state.attributeData[lotId]) {
                const lotAttrs = this.state.attributeData[lotId];
                return row.map(cell => {
                    if (cell.name.startsWith('x_attr_')) {
                        const attrName = cell.string;
                        return { ...cell, value: lotAttrs[attrName] || "" };
                    }
                    return cell;
                });
            }
            return row;
        });
    }
}

// Vincular el nuevo renderer a la vista. Usamos 'listView' importado.
registry.category("views").add("stock_quant_list_with_attributes", {
    ...listView,
    Renderer: StockQuantListWithAttributesRenderer,
});
