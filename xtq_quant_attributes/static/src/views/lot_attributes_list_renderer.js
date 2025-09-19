/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");

        this.lotAttributes = { headers: [], data: {} };
        this.attributesFetched = false;

        const fetchDataAndInjectColumns = async (list) => {
            const isLotSelection = list.resModel === 'stock.quant' && 'default_product_id' in list.context;
            if (!isLotSelection || this.attributesFetched || list.records.length === 0) {
                return;
            }
            this.attributesFetched = true;

            const productId = list.context.default_product_id;
            if (!productId) { return; }

            const productInfo = await this.orm.read("product.product", [productId], ["product_tmpl_id"]);
            if (!productInfo.length || !productInfo[0].product_tmpl_id) { return; }
            const templateId = productInfo[0].product_tmpl_id[0];

            const templateData = await this.orm.read("product.template", [templateId], ["show_quality_attrs_in_picking"]);

            if (templateData && templateData[0].show_quality_attrs_in_picking) {
                const lotIds = list.records.map(rec => rec.data.lot_id[0]).filter(Boolean);

                if (lotIds.length > 0) {
                    const result = await this.orm.call("stock.lot", "get_attributes_for_lots_view", [lotIds]);
                    this.lotAttributes = result;

                    // Modificar directamente el archInfo de la lista actual.
                    // Esta es la forma más segura de inyectar columnas dinámicamente.
                    const newColumns = [...list.archInfo.columns];
                    this.lotAttributes.headers.forEach(header => {
                        newColumns.push({
                            name: `x_lot_attr_${header.replace(/\s+/g, '_')}`,
                            string: header,
                            type: 'char',
                        });
                    });
                    list.archInfo.columns = newColumns;
                }
            }
        };

        onWillStart(() => fetchDataAndInjectColumns(this.props.list));
        onWillUpdateProps((nextProps) => fetchDataAndInjectColumns(nextProps.list));
    },

    get cells() {
        const originalCellsGetter = super.cells;
        if (!this.lotAttributes.headers || this.lotAttributes.headers.length === 0) {
            return originalCellsGetter;
        }

        return (record, column, index) => {
            const lotId = record.data.lot_id ? record.data.lot_id[0] : null;
            if (lotId && column.name.startsWith('x_lot_attr_')) {
                const attrName = column.string;
                const lotData = this.lotAttributes.data[lotId];
                const value = lotData && lotData[attrName] ? lotData[attrName] : '';
                
                return {
                    ...column,
                    value: value,
                    formattedValue: value,
                    props: { ...column.props, readonly: true },
                };
            }
            return originalCellsGetter(record, column, index);
        };
    }
});
