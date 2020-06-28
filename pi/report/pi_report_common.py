# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from lxml import etree

from openerp.osv import fields, osv
from openerp.osv.orm import setup_modifiers
from openerp.tools.translate import _

class pi_report_common(osv.osv_memory):
    _name = "pi.report.common"
    _description = "Proforman Invoice Common Report"


    _columns = {
        'vendor_id': fields.many2one('res.partner', 'Vendor name', select=True),
        'date_from': fields.date("Start Date"),
        'date_to': fields.date("End Date"),

        }

    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        result['vendor'] = 'vendor_id' in data['form'] and data['form']['vendor_id'] or False
        result['date_from'] = 'date_from' in data['form'] and data['form']['date_from'] or False
        return result


    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['vendor_id',  'date_from', 'date_to'], context=context)[0]

        for field in ['vendor_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        # import pdb
        # pdb.set_trace()
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)

