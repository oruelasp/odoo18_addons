# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class MrpEco(models.Model):
	_inherit = 'mrp.eco'

	task_ids = fields.Many2many('project.task')
	task_count = fields.Integer(string="Tasks",compute="compute_task_count")

	def compute_task_count(self):
		for count in self:
			count.task_count = len(self.task_ids)

	def eco_tasks(self):
		record = self.env['ir.actions.actions']._for_xml_id('project.action_view_my_task')
		for rec in self:
			domain = [('eco_id', '=', rec.task_ids.eco_id.id)]
		record['domain'] = domain
		return record


class ProjectTaskInherit(models.Model):
	_inherit = "project.task"

	eco_id = fields.Many2one('mrp.eco')
