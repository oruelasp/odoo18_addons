from odoo import models, fields

class MrpProductionCurveLine(models.Model):
    _name = 'mrp.production.curve.line'
    _description = 'Línea de Curva de Tallas para OP'

    production_id = fields.Many2one(
        'mrp.production',
        string='Orden de Producción',
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
        ('unique_curve_entry', 'unique(production_id, attribute_value_id)',
         'Cada valor de atributo en la curva debe ser único por Orden de Producción.')
    ]
