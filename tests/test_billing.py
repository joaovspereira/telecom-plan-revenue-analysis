import unittest
import pandas as pd
from billing import invoice_months,compare_plans,synthetic_tables

class BillingTests(unittest.TestCase):
    def test_rounding_units_and_zero_usage(self):
        r=invoice_months(*synthetic_tables(),start='2018-01-01',end='2018-01-31').set_index('user_id')
        self.assertEqual(r.loc[1,'minutes'],3)
        self.assertEqual(r.loc[1,'gb'],2)
        self.assertEqual(r.loc[1,'revenue_usd'],30.09)
        self.assertEqual(r.loc[2,'revenue_usd'],20)
    def test_month_grid_and_partial_subscription_policy(self):
        u,p,c,m,i=synthetic_tables()
        u.loc[1,'reg_date']='2018-02-15'
        u.loc[1,'churn_date']='2018-02-20'
        r=invoice_months(u,p,c,m,i,start='2018-01-01',end='2018-03-31')
        self.assertEqual(len(r),4)
        self.assertEqual(r.loc[r.user_id.eq(2),'revenue_usd'].tolist(),[20])
    def test_year_is_part_of_month_key(self):
        r=invoice_months(*synthetic_tables(),start='2018-01-01',end='2019-01-31')
        self.assertEqual(len(r),26)
        self.assertEqual(r.query("month == '2019-01'")['revenue_usd'].tolist(),[20,20])
    def test_invalid_inputs(self):
        u,p,c,m,i=synthetic_tables()
        c.loc[0,'duration']=-1
        with self.assertRaisesRegex(ValueError,'Invalid usage'): invoice_months(u,p,c,m,i)
    def test_comparison_weights_users_once(self):
        r=pd.DataFrame({'user_id':[1,1,1,2,3,4],'plan':['surf']*4+['ultimate']*2,'revenue_usd':[10,10,10,30,40,60]})
        result=compare_plans(r)
        self.assertEqual(result['users_first'],2)
        self.assertEqual(result['mean_first_usd'],20)
        self.assertEqual(result['difference_usd'],-30)
