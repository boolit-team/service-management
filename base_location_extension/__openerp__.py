# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#
#    Author: Andrius Laukavičius
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
    'name': 'Base Location',
    'version': '1.2.0',
    'category': 'Base',
    'sequence': 2,
    'summary': 'Cities, Streets management',
    'description': """
This module updates current localization for countries and Fed. States. It adds cities, and street and extends base_location module.
""",
    'author': 'Andrius Laukavičius',
    'website': '',
    'depends': [      
       'base_location',
    ],
    'data': [
        'res/city_view.xml',
        'res/street_view.xml',
        'res/partner_view.xml',       
        'res/company_view.xml',
        'res/state_view.xml',
        'better_zip_view.xml',
        'security/ir.model.access.csv',
        'data/res.country.state.csv',
    ],
    'demo': [
        'demo/res_country_state_city.xml',
        'demo/res_country_state_city_street.xml',                
        'demo/demo_addresses.xml',        

    ],
    'test': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
