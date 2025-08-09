from odoo import models, api


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def get_matrix_data(self, record_ids: list):
        record_ids.sort()
        records = self.browse(record_ids)
        products = records.mapped("product_id")

        result = list()

        for product in products:
            header = [{"value": product.product_tmpl_id.name}]
            body = list()
            footer = [{"value": "TOTAL"}]
            domain = [("product_id", "=", product.id)]
            production_records = self.search(domain)
            lot_producing_records = production_records.mapped("lot_producing_id")
            attribute_line_ids = lot_producing_records.mapped("attribute_line_ids")
            tones = list(
                set(
                    attribute_line_ids.sorted(lambda rec: rec.value_id.name)
                    .filtered(lambda rec: rec.attribute_id.name == "TONO")
                    .mapped("value_id")
                )
            )
            sizes = list(
                set(
                    attribute_line_ids.sorted(lambda rec: rec.value_id.name)
                    .filtered(lambda rec: rec.attribute_id.name == "TALLA")
                    .mapped("value_id")
                )
            )
            tones = sorted(tones, key=lambda rec: rec.name)
            sizes = sorted(sizes, key=lambda rec: rec.name)

            for index, size in enumerate(sizes, 1):
                header.append({"value": f"T{index}:{size.name}"})

            for index, tone in enumerate(tones, 1):
                row = [{"value": f"Tono {index}:{tone.name}", "editable": False}]
                lot_tone_ids = set(attribute_line_ids.filtered(lambda rec: rec.value_id == tone).mapped("lot_id"))
                product_qty_total = 0
                for size in sizes:
                    lot_size_ids = set(attribute_line_ids.filtered(lambda rec: rec.value_id == size).mapped("lot_id"))
                    product_qty = 0
                    lot_ids = lot_tone_ids & lot_size_ids
                    production_records_by_lots = production_records.filtered(
                        lambda rec: rec.lot_producing_id in lot_ids
                    )
                    product_qty = sum(production_records_by_lots.mapped("product_qty"))
                    product_qty_total += product_qty
                    editable = bool(production_records_by_lots)
                    row.append(
                        {
                            "value": product_qty,
                            "editable": editable,
                            "id": editable and production_records_by_lots[0].id,
                            "field": "product_qty",
                        }
                    )

                row.append({"value": product_qty_total, "editable": False})
                body.append(row)

            footer = [
                {"value": sum(item["value"] for item in col if isinstance(item["value"], (int, float)))}
                for col in zip(*body)
            ]

            if footer:
                footer[0] = {"value": "TOTAL"}

            if body:
                header.append({"value": "TOTAL"})
                result.append({"header": header, "body": body, "footer": footer})

        return result
