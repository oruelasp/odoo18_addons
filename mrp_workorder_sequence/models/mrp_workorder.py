# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpWorkOrder(models.Model):
    _inherit = "mrp.workorder"
    _order = "production_id, sequence, id"

    sequence = fields.Integer(default=0)

    def _assign_sequence_on_create(self, values_list):
        """Assign sequence number for manually added operations"""
        new_wos_production_ids_without_seq = {
            vals["production_id"] for vals in values_list if not vals.get("sequence")
        }
        if new_wos_production_ids_without_seq:
            max_seq_by_production = self.read_group(
                [("production_id", "in", list(new_wos_production_ids_without_seq))],
                ["sequence:max", "production_id"],
                ["production_id"],
            )
            max_seq_by_prod_id = {
                res["production_id"][0]: res["sequence"]
                for res in max_seq_by_production
            }
            for values in values_list:
                prod_id = values["production_id"]
                values_seq = values.get("sequence")
                max_seq = max_seq_by_prod_id.setdefault(prod_id, 0)
                if values_seq and values_seq > max_seq:
                    max_seq_by_prod_id[prod_id] = values_seq
                    continue
                max_seq_by_prod_id[prod_id] += 1
                values["sequence"] = max_seq_by_prod_id[prod_id]

    @api.model_create_multi
    def create(self, values_list):
        if not self.env.context.get("_bypass_sequence_assignation_on_create"):
            self._assign_sequence_on_create(values_list)
        return super().create(values_list)

    def write(self, vals):
        if 'sequence' in vals and not self.env.context.get('bypass_sequence_write'):
            # Handle drag-and-drop reordering to avoid cyclic dependency errors.
            # We handle records one by one, which is fine for drag-and-drop.
            for line in self:
                # Get all siblings, including self, sorted by current sequence
                lines = self.search(
                    [('production_id', '=', line.production_id.id)],
                    order='sequence asc'
                )
                # If the line is not in the list, it's a new line, so we can skip
                if line not in lines:
                    continue

                # Create a mutable list of records
                line_list = list(lines)
                line_list.remove(line)

                # The sequence from the UI is the new index.
                # Ensure it's within the valid range.
                new_index = vals['sequence']
                new_index = max(0, min(new_index, len(line_list)))

                line_list.insert(new_index, line)

                # Re-assign the sequence to all siblings
                for i, rec in enumerate(line_list):
                    rec.with_context(bypass_sequence_write=True).write({'sequence': i})
            
            # If there are other values to write, write them now on the original recordset
            other_vals = vals.copy()
            other_vals.pop('sequence')
            if other_vals:
                return super(MrpWorkOrder, self).write(other_vals)

            return True

        return super(MrpWorkOrder, self).write(vals)
