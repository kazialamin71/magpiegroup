from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import datetime




class loan_receipt(osv.osv):
    _name = 'loan.receipt'
    _description = "Loan Payment"

    def button_add_receipt_action(self, cr, uid, ids, context=None):
        payment_obj = self.browse(cr, uid, ids, context=None)
        loan_id = context.get('loan_id')
        eve_mee_obj = self.pool.get('loan.receipt.line')
        pay_date = payment_obj.date
        pay_type = payment_obj.type
        pay_amount = payment_obj.amount
        pay_usd_amount = payment_obj.usd_amount

        service_dict = {'date': pay_date, 'type': pay_type, 'amount': pay_amount, 'loan_id': loan_id}
        # import pdb
        # pdb.set_trace()

        service_id = eve_mee_obj.create(cr, uid, vals=service_dict, context=context)

        # proforma_id = self.pool.get('proforma.invoice').search(cr, uid, [('id', '=', pi_id)], context=None)
        # proforma_object = self.pool.get('proforma.invoice').browse(cr, uid, proforma_id, context)
        # total = proforma_object.total
        # due_amount = total - payment_obj.amount
        #
        # cr.execute('update proforma_invoice set due_amount=%s where id=%s',
        #            (due_amount, pi_id))
        # cr.commit()
        # import pdb
        # pdb.set_trace()
        return service_id


    _columns = {
        'loan_id': fields.many2one('loan','Loan ID'),
        'amount': fields.float('Amount', required=True),
        'date': fields.datetime('Date'),
        'type': fields.char('Type'),
        'usd_amount': fields.float('Amount(USD)'),
        'partner_id': fields.many2one('res.partner', 'Customer Name'),

        'con_rate': fields.float('Conversion Rate')
    }
