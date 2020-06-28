

from openerp.osv import fields, osv
from openerp.osv.orm import setup_modifiers
from openerp.tools.translate import _


class pi_report_common_pi(osv.osv_memory):
    _name = 'pi.report.common.pi'
    _inherit = "pi.report.common"
    _columns = {
        'display_account': fields.selection([('all','All'), ('movement','With movements'),
                                            ('not_zero','With balance is not equal to 0'),
                                            ],'Display Accounts'),

    }
    _defaults = {
        'display_account': 'movement',
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}

        data['form'].update(self.read(cr, uid, ids, ['display_account'], context=context)[0])

        return data