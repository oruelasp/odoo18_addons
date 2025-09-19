/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        
        this.state = useState({
            qualityColumns: [], // Almacena solo nuestras columnas dinámicas.
        });
        
        // Almacena las columnas base (originales o modificadas por otros componentes).
        this.baseColumns = null; 
        this.lotAttributes = { headers: [], data: {} };
        this.attributesFetched = false;

        const fetchData = async (list) => {
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
                    
                    const newQualityColumns = [];
                    this.lotAttributes.headers.forEach(header => {
                        newQualityColumns.push({
                            name: `x_lot_attr_${header.replace(/\s+/g, '_')}`,
                            string: header,
                            type: 'char',
                        });
                    });
                    
                    // Actualiza el estado solo con nuestras columnas, lo que provoca un re-renderizado.
                    this.state.qualityColumns = newQualityColumns;
                }
            }
        };

        onWillStart(() => fetchData(this.props.list));
        onWillUpdateProps((nextProps) => fetchData(nextProps.list));
    },

    get columns() {
        const base = this.baseColumns || this.props.list.archInfo.columns;
        // Devuelve las columnas base + nuestras columnas de calidad.
        return [...base, ...this.state.qualityColumns];
    },
    
    set columns(newColumns) {
        // Intercepta los intentos de otros componentes de establecer las columnas
        // y los guarda como la nueva base.
        this.baseColumns = newColumns;
    },

    get cells() {
        const originalCellsGetter = super.cells;
        if (!this.state.qualityColumns.length) {
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
