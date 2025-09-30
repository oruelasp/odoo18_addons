from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    mercado = fields.Selection([
        ('1', 'Agropecuario'),
        ('4', 'Gran Minería'),
        ('5', 'Minería'),
        ('17', 'Marino'),
        ('34', 'Utilities'),
        ('35', 'Oil&Gas'),
        ('37', 'UGMI, Drilling'),
        ('38', 'Automotriz'),
        ('40', 'Portuario'),
        ('41', 'Industrial'),
        ('42', 'Construcción'),
        ('43', 'Clientes diversos'),
    ], string="Mercado")
