# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import datetime

class CreateTask(models.TransientModel):
	_name = "create.task.wizard"
	_description="Create Task"

	project_id = fields.Many2one('project.project', 'Project')
	task_title = fields.Char("Title")
	user_ids = fields.Many2many('res.users',string='Assignee')
	allocated_hours = fields.Float("Allocated Hours")
	task_deadline = fields.Datetime(string='Deadline')
	project_tag_ids	 = fields.Many2many('project.tags', string='Tag')
	task_desc = fields.Html(string='Description')


	def create_task_from_eco(self):
		eco_id = self.env['mrp.eco'].browse(self._context.get('active_id'))
		task = self.env['project.task'].create({
			'name':self.task_title,
			'project_id':self.project_id.id,
			'user_ids':self.user_ids.ids,
			'date_deadline':self.task_deadline,
			'tag_ids':self.project_tag_ids.ids,
			'description': self.task_desc,
			'allocated_hours': self.allocated_hours,
			'eco_id':eco_id.id
			})

		eco_id.update({
	        'task_ids': [(4, task.id)]
	    })

		