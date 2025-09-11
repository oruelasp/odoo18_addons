# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Create Task from Engineering Change Orders | Engineering Change Order Integration with Task | Sync Product Lifecycle Management with Tasks",
    'version': '18.0.0.0',
    'category': 'Project',
    'summary': "generate task from ECO auto create task from engineering change order Sync Engineering Change Order with Task convert ECO to Task PLM task integration manage tasks from ECO engineering order to project task auto create task from ECO",
    'description': """This module allows you to create project tasks directly from Engineering Change Orders (ECOs) in Odoo. A "Create Task" button is added to the ECO form, opening a wizard where users can enter details like Project, Task Title, Assignees, Allocated Hours, Deadline, Tags, and Description. Once a task is created, a "Tasks" smart button with a counter appears in the ECO, providing quick access to all related tasks. This integration helps streamline engineering changes, task assignments, and project tracking, ensuring a smooth workflow between PLM and Project Management.""",
    'author': "BROWSEINFO",
    'website': 'https://www.browseinfo.com',
    'depends': ['base','project','mrp','mrp_plm'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_task.xml',
        'views/views.xml',        
    ],
    'license': 'OPL-1',
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/o2Igf8ds72A',
    "images":['static/description/Banner.gif'],
}
