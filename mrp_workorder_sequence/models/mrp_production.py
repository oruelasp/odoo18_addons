# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _reset_work_order_sequence(self):
        for rec in self:
            # Add the context flag to prevent the write method in mrp.workorder
            # from triggering this logic again in an infinite loop.
            workorders_with_context = rec.workorder_ids.with_context(
                bypass_sequence_write=True
            )
            for current_seq, work in enumerate(workorders_with_context, 1):
                work.sequence = current_seq

    def _link_bom(self, bom):
        # Bypass sequence assignation on create and make sure there is no gap
        # using _reset_work_order_sequence
        res = super(
            MrpProduction,
            self.with_context(_bypass_sequence_assignation_on_create=True),
        )._link_bom(bom)
        self._reset_work_order_sequence()
        return res
