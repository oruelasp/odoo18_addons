from odoo import models, fields

class SalesProgramCurveLine(models.Model):
    _name = 'sales.program.curve.line'
    _description = 'Línea de Curva de Tallas para Programa de Ventas'

    program_id = fields.Many2one(
        'sales.program',
        string='Programa de Venta',
        required=True,
        ondelete='cascade'
    )
    attribute_value_id = fields.Many2one(
        'product.attribute.value',
        string='Valor de Atributo',
        required=True,
        help="Valor del atributo (ej. Talla) asociado a esta proporción."
    )
    proportion = fields.Integer(
        'Proporción',
        default=0,
        help="La proporción de la curva para este valor de atributo."
    )

    _sql_constraints = [
        ('unique_curve_entry', 'unique(program_id, attribute_value_id)',
         'Cada valor de atributo en la curva debe ser único por Programa de Venta.')
    ]
