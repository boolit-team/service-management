from openerp.tests.common import TransactionCase

class TestTimesheet(TransactionCase):

    def setUp(self):
        super(TestTimesheet, self).setUp()
        self.imd = self.registry('ir.model.data')
        self.serv_model = self.registry('calendar.service')
        self.work_model = self.registry('calendar.service.work')
        self.timesheet_model = self.registry('hr.analytic.timesheet')
        self.employee_model = self.registry('hr.employee')
    def test_update(self):
        cr, uid = self.cr, self.uid
        partner_id = self.imd.get_object_reference(cr, uid, 'base', 'res_partner_2')[1]
        product_id = self.imd.get_object_reference(cr, uid, 'product', 'product_product_consultant')[1]
        user_id = self.imd.get_object_reference(cr, uid, 'base', 'user_root')[1]
        emp1_id = self.imd.get_object_reference(cr, uid, 'hr', 'employee')[1]
        emp2_id = self.imd.get_object_reference(cr, uid, 'hr', 'employee_mit')[1]
        employee = self.employee_model.browse(cr, uid, emp2_id)
        journal_id = self.imd.get_object_reference(cr, uid, 'hr_timesheet', 'analytic_journal')[1]
        employee.write({'journal_id': journal_id})
        account_id = self.imd.get_object_reference(cr, uid, 'account', 'analytic_administratif')[1] 
        vals = {
            'partner_id': partner_id,
            'start_time': "2014-08-25 16:30:00",
            'end_time': '2014-08-25 17:30:00',
            'work_type': 'one',
            'state': 'open',
        }
        serv_vals = dict(vals, product_id=product_id, user_id=user_id)
        service_id = self.serv_model.create(cr, uid, serv_vals)
        work_vals = dict(vals, service_id=service_id, account_id=account_id)
        work_vals1 = dict(work_vals, employee_id=emp1_id)
        work_vals2 = dict(work_vals, employee_id=emp2_id)
        work1_id = self.work_model.create(cr, uid, work_vals1)
        work2_id = self.work_model.create(cr, uid, work_vals2)
        service = self.serv_model.browse(cr, uid, service_id)
        work1 = self.work_model.browse(cr, uid, work1_id)
        work2 = self.work_model.browse(cr, uid, work2_id)
        service.close_state()
        for work in service.work_ids:
            self.assertEquals(True if work.timesheet_id else False, True, "Timesheet was not set for work")
            self.assertEquals(work.timesheet_id.unit_amount, 1.0, "Wrong duration calculated from service work time")
            old_tsheet_id = work.timesheet_id.id
            service.close_state()
            service.open_state()
            self.assertEquals(old_tsheet_id, work.timesheet_id.id, "Opening and Closing Service should not \ncreate new timesheet or replace id")