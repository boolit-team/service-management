from openerp.tests.common import TransactionCase

class TestService(TransactionCase):

    def setUp(self):
        super(TestService, self).setUp()
        cr, uid = self.cr, self.uid   
        imd = self.registry('ir.model.data')
        partner_id = imd.get_object_reference(cr, uid, 'base', 'res_partner_2')[1]
        product_id = imd.get_object_reference(cr, uid, 'product', 'product_product_consultant')[1]
        user_id = imd.get_object_reference(cr, uid, 'base', 'user_root')[1]
        emp1_id = imd.get_object_reference(cr, uid, 'hr', 'employee_al')[1]
        emp2_id = imd.get_object_reference(cr, uid, 'hr', 'employee_mit')[1]
        serv_model = self.registry('calendar.service')
        work_model = self.registry('calendar.service.work')
        vals = {
            'partner_id': partner_id,
            'start_time': "2014-08-25 16:30:00",
            'end_time': '2014-08-25 17:30:00',
            'work_type': 'one',
            'state': 'open',
        }
        serv_vals = dict(vals, product_id=product_id, user_id=user_id)
        self.service_id = serv_model.create(cr, uid, serv_vals)
        work_vals = dict(vals, service_id=self.service_id)
        work_vals1 = dict(work_vals, employee_id=emp1_id)
        work_vals2 = dict(work_vals, employee_id=emp2_id)
        self.work1_id = work_model.create(cr, uid, work_vals1)
        self.work2_id = work_model.create(cr, uid, work_vals2)
        self.service = serv_model.browse(cr, uid, self.service_id)
        self.work1 = work_model.browse(cr, uid, self.work1_id)
        self.work2 = work_model.browse(cr, uid, self.work2_id)

    def test_service_updates(self):
        #Init test
        cr, uid = self.cr, self.uid
        service = self.service
        work1 = self.work1
        work2 = self.work2
        service.write({'work_type': 'recurrent'})
        service.cancel_state()
        self.assertEquals(service.state, 'cancel', "After calling cancel_state(), state should be cancel")
        for work in service.work_ids:
            self.assertEquals(work.state, 'cancel', "After calling cancel_state(), service work state should be cancel")
        service.open_state()
        self.assertEquals(service.state, 'open', "After calling open_state(), state should be open")
        for work in service.work_ids:
            self.assertEquals(work.state, 'open', "After calling open_state(), service work state should be open")
        service.close_state()
        self.assertEquals(service.state, 'done', 'After closing service state should be done')
        is_order = False
        if service.order_id:
            is_order = True
        self.assertEquals(is_order, True, "Sale Order was not created or calendar service was not related with it")
        for work in service.work_ids:
            self.assertEquals(work.work_type, service.work_type, "Work type for work should be the same as for it's service")
            self.assertEquals(work.state, 'done', "Work state should be done state after closing")
