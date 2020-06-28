from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class add_service_loan(osv.osv):
    _name = "add.service.loan"


    def button_add_service_action(self,cr,uid,ids,context=None):

        service_obj=self.browse(cr,uid,ids,context=None)
        loan_id=context.get('loan_id')
        eve_mee_obj = self.pool.get('loan.service.line')
        service_name=service_obj.service_name
        service_cost=service_obj.total_cost
        service_dict={'total_cost': service_cost, 'service_name': service_name, 'loan_id': loan_id}
        service_id = eve_mee_obj.create(cr, uid, vals=service_dict, context=context)
        return service_id




    _columns = {

         'total_cost': fields.float('Service Cost'),
         'service_name': fields.char('Service name',required=True),
         'loan_id': fields.many2one('loan', 'Loan Ids')

    }

    # def create(self, cr, uid, vals, context=None):

        # values={}
        # if not package_name:
        #     return {}
        # # import pdb
        # # pdb.set_trace()
        # abc={'pi.service.line':[]}
        # package_object=self.pool.get('examine.package').browse(cr,uid,package_name,context=None)
        # # import pdb
        # # pdb.set_trace()
        # for item in package_object.examine_package_line_id:
        #     items=item.name
        #     for itemid in items:
        #         car=itemid.id
        #         abc['bill_register_line_id'].append([0, False, {'name':car, 'total_amount': 400}])

        # abc={'bill_register_line_id':[[0, False, {'discount': 0, 'price': 400, 'name': 2, 'total_amount': 400}]]}
        # abc['bill_register_line_id'].append([0, False, {'discount': 0, 'price': 400, 'name': 2, 'total_amount': 400}])
        # values['value']=abc

        # return values
        # import pdb
        # pdb.set_trace()



    # def onchange_test(self,cr,uid,ids,name,context=None):
    #     tests = {'values': {}}
    #     dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
    #     abc = {'price': dep_object.rate,'total_amount':dep_object.rate}
    #     tests['value'] = abc
    #     # import pdb
    #     # pdb.set_trace()
    #     return tests