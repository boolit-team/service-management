# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Odoo, Open Source Management Solution
#
#    Author: Andrius Laukavičius. Copyright: Andrius Laukavičius
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
    'name': 'Payroll Timesheet',
    'version': '1.0',
    'category': 'payroll',
    'sequence': 2,
    'summary': 'Timesheet integration for Payroll',
    'description': """
    	Lets calculate payroll using timesheet activities. 
        Implements new method getDuration() that can be used in payroll rules. 
        This method returns total duration of hours from timesheet activities for 
        specific employee per payslip. It filters duration according to 
        payslip 'date_from' and 'date_to'. Also implements new field 'salary_per_h' in 
        employee contracts that can be used to calculate salary for worked hours. 
        Salary Rule example:
            'contract.salary_per_h * employee.getDuration(payslip)'


	""",
    'author': 'OERP',
    'website': 'www.oerp.eu',
    'depends': [
        'hr_payroll',
        'hr_timesheet_employee',      
    ],
    'data': [
        #'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
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
