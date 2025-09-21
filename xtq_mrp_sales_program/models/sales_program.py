# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


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
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        tracking=True
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

    # Size Curve fields
    matrix_attribute_col_id = fields.Many2one(
        'product.attribute', 
        string='Atributo para Curva (Tallas)',
        help="Atributo que se usará como eje para la curva de tallas."
    )
    matrix_curve_ids = fields.One2many(
        'sales.program.curve.line',
        'program_id',
        string='Curva de Tallas',
        copy=True,
    )
    matrix_values_col_ids = fields.Many2many(
        'product.attribute.value', 
        'sales_program_matrix_col_rel', 
        string='Valores para Curva', 
        domain="[('attribute_id', '=', matrix_attribute_col_id)]"
    )

    # Attribute lines
    attribute_line_ids = fields.One2many(
        'sales.program.attribute.line',
        'program_id',
        string='Líneas de Atributos'
    )

    # Matrix lines
    matrix_line_ids = fields.One2many(
        'sales.program.matrix.line',
        'program_id',
        string='Líneas de Matriz de Producción'
    )
    
    # JSON payload used by the matrix widget
    matrix_data_json = fields.Text(string="Matrix Data JSON", copy=False)

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
        productions_to_create = []
        
        # Prepare curve data
        curve_lines_data = []
        for curve_line in self.matrix_curve_ids:
            curve_lines_data.append((0, 0, {
                'attribute_value_id': curve_line.attribute_value_id.id,
                'proportion': curve_line.proportion,
            }))

        for line in self.line_ids:
            # Inherit tags from the line or the program header
            tag_ids = line.tag_ids or self.tag_ids
            productions_to_create.append({
                'project_id': self.project_id.id,
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
                # Add curve data
                'matrix_attribute_col_id': self.matrix_attribute_col_id.id,
                'matrix_values_col_ids': [(6, 0, self.matrix_values_col_ids.ids)],
                'matrix_curve_ids': curve_lines_data,
            })
        
        if not productions_to_create:
            return

        productions = self.env['mrp.production'].create(productions_to_create)
        
        self.write({'state': 'done'})
        
        # Return action to show the created MOs
        action = self.env['ir.actions.act_window']._for_xml_id('mrp.mrp_production_action')
        action['domain'] = [('id', 'in', productions.ids)]
        return action

    # --- Matrix widget integration ---
    def get_matrix_data(self, matrix_type='programming'):
        self.ensure_one()
        # Eje Y: líneas del programa
        axis_y = {
            'name': _('Línea del Programa'),
            'values': [{'id': line.id, 'name': line.name or str(line.id)} for line in self.line_ids]
        }
        # Eje X: valores seleccionados del atributo columna
        axis_x = {
            'name': self.matrix_attribute_col_id.name if self.matrix_attribute_col_id else _('Columna'),
            'values': [{'id': v.id, 'name': v.name} for v in self.matrix_values_col_ids]
        }
        # Mapear cantidades existentes
        quantities = {}
        for ml in self.matrix_line_ids:
            key = f"{ml.sales_program_line_id.id}-{ml.col_value_id.id}"
            quantities[key] = {
                'product_qty': ml.product_qty,
                'qty_producing': 0,
            }
        return {
            'axis_y': axis_y,
            'axis_x': axis_x,
            'quantities': quantities,
            'matrix_state': 'pending',
        }

    def _sync_matrix_lines_from_json(self, json_data):
        """Replace matrix_line_ids from provided JSON structure."""
        import json
        self.ensure_one()
        try:
            data = json.loads(json_data or '[]')
        except Exception:
            data = []
        commands = [(5, 0, 0)]
        for item in data:
            row_id = item.get('yValueId')
            col_id = item.get('xValueId')
            qty = item.get('product_qty') or 0.0
            if not row_id or not col_id:
                continue
            commands.append((0, 0, {
                'program_id': self.id,
                'sales_program_line_id': row_id,
                'col_value_id': col_id,
                'product_qty': qty,
            }))
        self.write({'matrix_line_ids': commands})

    def write(self, vals):
        res = super().write(vals)
        if 'matrix_data_json' in vals:
            for program in self:
                program._sync_matrix_lines_from_json(vals.get('matrix_data_json'))
        return res

    def action_calculate_matrix(self):
        self.ensure_one()
        
        # 1. Validations
        if not self.line_ids:
            raise UserError(_("Por favor, añada al menos una línea de producción."))
        if not self.matrix_curve_ids:
            raise UserError(_("Por favor, defina la Curva de Tallas."))

        # 2. Prepare proportions
        curve_map = {c.attribute_value_id.id: c.proportion for c in self.matrix_curve_ids}
        total_proportion = sum(curve_map.values())
        if total_proportion == 0:
            raise UserError(_("La suma de las proporciones en la Curva de Tallas no puede ser cero."))

        # 3. Clear existing matrix and prepare new lines
        matrix_lines_vals = []
        self.matrix_line_ids = [(5, 0, 0)]

        for line in self.line_ids:
            for curve_line in self.matrix_curve_ids:
                proportion = curve_line.proportion
                calculated_qty = (line.product_qty * proportion) / total_proportion
                
                matrix_lines_vals.append({
                    'program_id': self.id,
                    'sales_program_line_id': line.id,
                    'col_value_id': curve_line.attribute_value_id.id,
                    'product_qty': calculated_qty,
                })
        
        # 4. Create new matrix lines
        if matrix_lines_vals:
            self.env['sales.program.matrix.line'].create(matrix_lines_vals)

        return True

    def action_view_productions(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('mrp.mrp_production_action')
        action['domain'] = [('id', 'in', self.production_ids.ids)]
        action['context'] = {'create': False}
        return action


class SalesProgramLine(models.Model):
    _name = 'sales.program.line'
    _description = 'Sales Program Line'

    name = fields.Char(
        string='Descripción de Línea',
        compute='_compute_name',
        store=True,
    )
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

    @api.depends('tag_ids', 'product_qty')
    def _compute_name(self):
        for line in self:
            tags = ', '.join(line.tag_ids.mapped('name'))
            line.name = f"{tags}: {line.product_qty}" if tags else str(line.product_qty)

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
