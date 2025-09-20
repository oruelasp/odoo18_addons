/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { listView } from "@web/views/list/list_view";
import { onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class StockQuantListWithAttributesRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.orm = useService("orm");

        onWillStart(async () => {
            if (this.props.list.context.show_lot_attributes) {
                const fieldMap = await this._fetchAttributeMap();
                if (Object.keys(fieldMap).length > 0) {
                    this._updateColumns(fieldMap);
                }
            }
        });
    }

    async _fetchAttributeMap() {
        const productId = this.props.list.context.lot_attributes_product_id;
        if (!productId) {
            return {};
        }
        return await this.orm.call(
            'stock.quant',
            'get_attribute_field_map',
            [productId]
        );
    }

    _updateColumns(fieldMap) {
        const fieldsToShow = new Set(Object.keys(fieldMap));

        for (const col of this.props.list.columns) {
            if (col.name.startsWith('x_attr_')) {
                if (fieldsToShow.has(col.name)) {
                    // Actualiza la etiqueta y se asegura de que sea visible
                    col.string = fieldMap[col.name];
                    col.optional = false; 
                } else {
                    // Si no está en el mapa, nos aseguramos de que esté oculta
                    col.optional = 'hide';
                }
            }
        }
    }
}

registry.category("views").add("stock_quant_list_with_attributes", {
    ...listView,
    Renderer: StockQuantListWithAttributesRenderer,
});
