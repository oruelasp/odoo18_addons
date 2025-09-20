# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SalesProgram(models.Model):
    _name = 'sales.program'
    _description = 'Sales Program'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Program Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    description = fields.Char(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    date_planned_start = fields.Datetime(
        string='Planned Date',
        default=fields.Datetime.now,
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    line_ids = fields.One2many(
        'sales.program.line',
        'program_id',
        string='Program Lines',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    )
    production_ids = fields.One2many(
        'mrp.production',
        'sales_program_id',
        string='Manufacturing Orders',
        readonly=True
    )
    production_count = fields.Integer(
        string='Manufacturing Order Count',
        compute='_compute_production_count',
        store=True,
    )

    # Technical fields from wizard
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        "Operation Type",
        domain="[('code', '=', 'mrp_operation')]",
        required=True,
    )
    location_src_id = fields.Many2one(
        'stock.location',
        "Components Location",
        domain="[('usage','=','internal')]",
        required=True,
    )
    location_dest_id = fields.Many2one(
        'stock.location',
        "Finished Products Location",
        domain="[('usage','=','internal')]",
        required=True,
    )
    tag_ids = fields.Many2many(
        'mrp.tag',
        string="Tags",
    )

    @api.depends('production_ids')
    def _compute_production_count(self):
        for program in self:
            program.production_count = len(program.production_ids)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sales.program') or _('New')
        return super().create(vals_list)

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_generate_productions(self):
        self.ensure_one()
        productions = self.env['mrp.production']
        for line in self.line_ids:
            # Inherit tags from the line or the program header
            tag_ids = line.tag_ids or self.tag_ids
            
            vals = {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom_id': line.product_uom_id.id,
                'bom_id': line.bom_id.id,
                'picking_type_id': self.picking_type_id.id,
                'location_src_id': self.location_src_id.id,
                'location_dest_id': self.location_dest_id.id,
                'sales_program_id': self.id,
                'company_id': self.company_id.id,
                'tag_ids': [(6, 0, tag_ids.ids)],
            }
            production = self.env['mrp.production'].create(vals)
            production.action_confirm()
            productions |= production
        
        self.write({'state': 'done'})
        
        # Return action to show the created MOs
        action = self.env['ir.actions.act_window']._for_xml_id('mrp.mrp_production_action')
        action['domain'] = [('id', 'in', productions.ids)]
        return action


class SalesProgramLine(models.Model):
    _name = 'sales.program.line'
    _description = 'Sales Program Line'

    program_id = fields.Many2one(
        'sales.program',
        string='Sales Program',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    product_qty = fields.Float(
        'Quantity',
        default=1.0,
        digits='Product Unit of Measure',
        required=True
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        'Unit of Measure',
        required=True,
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        'Bill of Material',
        domain="[('product_tmpl_id', '=', product_tmpl_id)]"
    )
    product_tmpl_id = fields.Many2one(
        related='product_id.product_tmpl_id',
    )
    tag_ids = fields.Many2many(
        'mrp.tag',
        string="Tags",
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            bom = self.env['mrp.bom']._bom_find(product=self.product_id, bom_type='normal')
            if bom:
                self.bom_id = bom[self.product_id].id if self.product_id in bom else False
