/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { onWillStart, onWillUpdateProps, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class StockQuantListWithAttributesRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = useState({
            attributeData: {},
            attributeHeaders: [],
            showAttributes: this.props.arch.attrs.class?.includes('stock_quant_list_with_attributes'),
        });

        onWillStart(async () => {
            if (this.state.showAttributes) {
                await this._fetchAttributeData();
                this._updateColumns();
            }
        });

        onWillUpdateProps(async (nextProps) => {
            if (this.state.showAttributes) {
                await this._fetchAttributeData(nextProps);
                this._updateColumns(nextProps);
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
    
    _updateColumns(props = this.props) {
        if (!this.state.showAttributes) return;

        // Mostrar solo las columnas de atributos que tienen datos
        for (const col of props.arch.children) {
            if (col.attrs.name.startsWith('x_attr_')) {
                const header = col.attrs.string;
                col.attrs.invisible = this.state.attributeHeaders.includes(header) ? '0' : '1';
            }
        }
    }

    getColumns(props = this.props) {
        // Devuelve las columnas actualizadas
        // Esta función podría ser necesaria si _updateColumns no refleja los cambios a tiempo
        return super.getColumns(props);
    }
}

// Vincular el nuevo renderer a la vista a través de la js_class
registry.category("views").add("stock_quant_list_with_attributes", {
    ...registry.get("web.ListView"),
    Renderer: StockQuantListWithAttributesRenderer,
});
