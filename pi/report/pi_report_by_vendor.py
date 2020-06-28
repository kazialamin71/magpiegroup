
import time
from lxml import etree

from openerp.osv import fields, osv
from openerp.osv.orm import setup_modifiers
from openerp.tools.translate import _


class pi_report_by_vendor(osv.osv_memory):
    _name = "pi.report.by.vendor"
    _inherit = "pi.report.common"
    _description = "General Ledger Report"

    _columns = {
        'sortby': fields.selection([('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')], 'Sort by', required=True)

    }

    def _print_report(self, cr, uid, ids, data, context=None):
        context = dict(context or {})
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['sortby'])[0])

        return self.pool['report'].get_action(cr, uid, [], 'cma_galib.report_proforma_popup', data=data, context=context)



    # def _print_report(self, cr, uid, ids, data, context=None):
    #     context = dict(context or {})
    #     data = self.pre_print_report(cr, uid, ids, data, context=context)
    #     data['form'].update(self.read(cr, uid, ids, ['landscape',  'initial_balance', 'amount_currency', 'sortby'])[0])
    #     if not data['form']['fiscalyear_id']:# GTK client problem onchange does not consider in save record
    #         data['form'].update({'initial_balance': False})
    #
    #     if data['form']['landscape'] is False:
    #         data['form'].pop('landscape')
    #     else:
    #         context['landscape'] = data['form']['landscape']
    #
    #     return self.pool['report'].get_action(cr, uid, [], 'account.report_generalledger', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

class report_proforma_popup(osv.AbstractModel):
    _name = 'report.pi.report_proforma_popup'
    # _inherit = 'report.abstract_report'
    _template = 'cma_galib.report_proforma_popup'
    # _wrapped_report_class = general_ledger
