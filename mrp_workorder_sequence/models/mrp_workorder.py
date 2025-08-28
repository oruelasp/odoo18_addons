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
        # This block handles the drag-and-drop reordering.
        # It triggers ONLY when 'sequence' is being written and it's not an internal update.
        if 'sequence' in vals and not self.env.context.get('bypass_sequence_write'):
            # Handle each record one by one, which is how the UI sends them.
            for workorder in self:
                if not workorder.production_id:
                    # If there's no production order, there are no siblings to reorder.
                    continue

                # Get all siblings, sorted by their current sequence.
                siblings = self.search(
                    [('production_id', '=', workorder.production_id.id)],
                    order='sequence asc'
                )

                # Create a mutable list of records for reordering.
                sibling_list = list(siblings)
                if workorder in sibling_list:
                    sibling_list.remove(workorder)

                # The 'sequence' value from the UI is the new 0-based index for the record.
                new_index = vals['sequence']
                # Clamp the index to a valid range to prevent errors.
                new_index = max(0, min(new_index, len(sibling_list)))

                # Insert the moved record at its new position in the list.
                sibling_list.insert(new_index, workorder)

                # Re-write the sequence for the entire list with a bypass flag.
                # This ensures this reordering logic doesn't run in an infinite loop.
                for i, rec in enumerate(sibling_list):
                    # We use i + 1 because sequences are typically 1-based for users.
                    rec.with_context(bypass_sequence_write=True).write({'sequence': i + 1})
            
            # After handling the sequence, if there are other values being written
            # at the same time, let the original method handle them.
            other_vals = vals.copy()
            other_vals.pop('sequence')
            if other_vals:
                super(MrpWorkOrder, self).write(other_vals)
            
            # Return True to signify that we have handled the write operation.
            return True

        # For all other write operations (e.g., changing state), run the standard Odoo method.
        # This also handles our own internal calls that have the 'bypass_sequence_write' flag.
        return super().write(vals)
