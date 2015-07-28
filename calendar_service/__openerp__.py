# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Odoo, Open Source Management Solution
#
#    Author: Andrius Laukavičius. Copyright: JSC NOD Baltic
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################


{
    'name': 'Calendar Service Management',
    'version': '1.2.6',
    'category': 'Calendar',
    'sequence': 2,
    'summary': 'Manage recurrent or one time services that need resources and planning',
    'description': """
	Plan and automatically generate recurrent events that repeat weekly or every second week.
    Assign resources to complete service works. Every service is on one calendar where you can
    plan accordingly. Change recurrent events when needed, put one time non repeating services
    in empty time intervals with free resources. 
	""",
    'author': 'OERP',
    'website': 'www.oerp.eu',
    'depends': [
        'base_address_management',
        'sale',
        'hr',
        #'web_calendar',     
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/rule_change_view.xml',
        'views/calendar_service_view.xml',
        'views/calendar_service_recurrent_view.xml',
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'data/sequences.xml',
        'data/schedulers.xml',
        #'views/calendar_service.xml',        

    ],
    'demo': [
        'demo/calendar_service_demo.xml'
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
