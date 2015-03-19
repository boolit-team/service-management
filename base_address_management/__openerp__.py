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
    'name': 'Addresses Management',
    'version': '1.01',
    'category': 'Base',
    'sequence': 2,
    'summary': 'Partners addresses management',
    'description': """
	Extends address with additional fields like house and apartment
    number. Also you can archive old addresses that any partner had.
    You can see history of all addreses and the current one that is being used.
    There are buttons to help arvhive and update address easier.
	""",
    'author': 'OERP',
    'website': 'www.oerp.eu',
    'depends': [
        'base_location_extension',      
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        #'data/,        

    ],
    'demo': [
    ],
    'test': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
