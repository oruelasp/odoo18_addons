from odoo import api, fields, models

class MrpProductionMatrixLine(models.Model):
    _name = 'mrp.production.matrix.line'
    _description = 'Línea de Matriz de Producción'

    production_id = fields.Many2one('mrp.production', string='Orden de Producción', required=True, ondelete='cascade')
    matrix_type = fields.Selection([
        ('programming', 'Programación'),
        ('distribution', 'Distribución')
    ], string="Tipo de Matriz", default='programming', required=True)
    row_value_id = fields.Many2one('product.attribute.value', string='Valor Fila', ondelete='cascade', required=True)
    col_value_id = fields.Many2one('product.attribute.value', string='Valor Columna', ondelete='cascade', required=True)
    product_qty = fields.Float(string='Cantidad Programada', digits='Product Unit of Measure')
    qty_producing = fields.Float(string='Cantidad Ejecutada', digits='Product Unit of Measure')
    
    _sql_constraints = [
        ('unique_matrix_entry', 'unique(production_id, matrix_type, row_value_id, col_value_id)', 
         'Ya existe una entrada en la matriz para esta combinación de atributos y tipo.')
    ]