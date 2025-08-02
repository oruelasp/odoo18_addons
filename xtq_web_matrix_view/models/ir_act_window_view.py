# models/ir_act_window_view.py
from odoo import fields, models

class IrActWindowView(models.Model):
    _inherit = "ir.act.window.view"

    view_mode = fields.Selection(
        selection_add=[("matrix_editable", "Matrix Editable")],
        ondelete={"matrix_editable": "cascade"},
    ) 