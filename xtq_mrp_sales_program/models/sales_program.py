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
        compute="_compute_locations",
        store=True,
        readonly=False,
        precompute=True,
        domain="[('usage','=','internal')]",
        required=True,
    )
    location_dest_id = fields.Many2one(
        'stock.location',
        "Finished Products Location",
        compute="_compute_locations",
        store=True,
        readonly=False,
        precompute=True,
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
    
    @api.depends('picking_type_id')
    def _compute_locations(self):
        for program in self:
            if not program.picking_type_id:
                continue
            
            fallback_loc = False
            if not program.picking_type_id.default_location_src_id or not program.picking_type_id.default_location_dest_id:
                company_id = program.company_id.id if program.company_id else self.env.company.id
                fallback_loc = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1).lot_stock_id

            program.location_src_id = program.picking_type_id.default_location_src_id.id or fallback_loc
            program.location_dest_id = program.picking_type_id.default_location_dest_id.id or fallback_loc

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or vals.get('name', _('New')) == _('New'):
                picking_type_id = vals.get('picking_type_id')
                if picking_type_id:
                    picking_type = self.env['stock.picking.type'].browse(picking_type_id)
                    if picking_type.sequence_id:
                        vals['name'] = picking_type.sequence_id.next_by_id()
                    else:
                        vals['name'] = self.env['ir.sequence'].next_by_code('sales.program') or _('New')
                else:
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
        compute='_compute_uom_id',
        store=True,
        readonly=False,
        precompute=True,
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        'Bill of Material',
        compute='_compute_bom_id',
        store=True,
        readonly=False,
        precompute=True,
        domain="""[
            '&',
                '|',
                    ('product_tmpl_id', '=', product_tmpl_id),
                    '&',
                        ('product_id.product_tmpl_id.product_variant_ids', '=', product_id),
                        ('product_id', '=', False),
            ('type', '=', 'normal')
        ]"""
    )
    product_tmpl_id = fields.Many2one(
        related='product_id.product_tmpl_id',
    )
    tag_ids = fields.Many2many(
        'mrp.tag',
        string="Tags",
    )

    @api.depends('product_id', 'program_id.picking_type_id', 'program_id.company_id')
    def _compute_bom_id(self):
        for line in self:
            if not line.product_id:
                line.bom_id = False
                continue
            # Ensure program_id is available
            if not line.program_id or not isinstance(line.program_id.id, int):
                line.bom_id = False
                continue
            
            bom = self.env['mrp.bom']._bom_find(
                line.product_id,
                picking_type=line.program_id.picking_type_id,
                company_id=line.program_id.company_id.id,
                bom_type='normal'
            )
            line.bom_id = bom.get(line.product_id, False)

    @api.depends('bom_id', 'product_id')
    def _compute_uom_id(self):
        for line in self:
            if line.bom_id and (not line.product_uom_id or line.bom_id != line._origin.bom_id):
                line.product_uom_id = line.bom_id.product_uom_id.id
            elif line.product_id and not line.product_uom_id:
                line.product_uom_id = line.product_id.uom_id.id
            elif not line.product_id and not line.bom_id:
                line.product_uom_id = False
