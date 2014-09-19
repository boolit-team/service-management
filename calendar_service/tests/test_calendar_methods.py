from openerp.tests.common import TransactionCase
from openerp import api
from datetime import datetime
import pytz
class TestCalendarMethods(TransactionCase):

    def setUp(self):
        super(TestCalendarMethods, self).setUp()
        self.calendar = self.registry('calendar.service.calendar')

    def test_dt_conversions(self):
        cr, uid = self.cr, self.uid
        self.assertEquals(self.calendar.get_dt_fmt(cr, uid), "%Y-%m-%d %H:%M:%S", "Returned Datetime format is bad!")
        dt_str = '2014-05-20 16:30:50'
        dt = datetime.strptime(dt_str, self.calendar.get_dt_fmt(cr, uid))
        self.assertEquals(self.calendar.str_to_dt(cr, uid, dt_str), dt, "Wrong Datetime Object Returned!")

    def test_setters(self):
        cr, uid = self.cr, self.uid
        local_tz = pytz.timezone(self.env.user.tz)
        dt = datetime.now()
        dt_test = local_tz.localize(dt)
        dt_test = dt_test.astimezone(pytz.utc)
        self.assertEquals(self.calendar.set_utc(cr, uid, dt), dt_test, "UTC set incorrectly")
        dt_test2 = dt.replace(tzinfo=pytz.utc)
        self.assertEquals(self.calendar.set_utc(cr, uid, dt, check_tz=False), dt_test2, "UTC set incorrectly when check_tz=False")
        dt_test3 = dt_test2.astimezone(local_tz)
        self.assertEquals(self.calendar.set_tz(cr, uid, dt), dt_test3, "Incorrect TZ set")

    def test_getters(self):
        cr, uid = self.cr, self.uid
        self.assertEquals(self.calendar.get_weekday(cr, uid, 'F'), 'Friday', "Wrong Weekday Returned")
        self.assertEquals(self.calendar.get_weekday(cr, uid, 'F', name=False), 4, "Wrong weekday number returned")
        self.assertEquals(self.calendar.get_rev_weekday(cr, uid, 4), 'F', "Wrong weekday letter returned")
        end_dt = datetime.now().replace(year=2014, month=9, hour=2, minute=30, second=0, microsecond=0)
        start_dt = end_dt.replace(minute=15)
        self.assertEquals(self.calendar.get_duration(cr, uid, start_dt, end_dt), 0.25, "Incorrect duration")
        dt_test1 = datetime.now().replace(year=2014, month=9, day=20, hour=8, minute=30, second=0, microsecond=0)
        dt_test1 = self.calendar.set_utc(cr, uid, dt_test1)
        self.assertEquals(self.calendar.relative_date(cr, uid, end_dt, 5, 8.5), dt_test1, "Wrong relative date returned")