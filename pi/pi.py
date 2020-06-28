from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import datetime




class proforma_invoice(osv.osv):
    _name = 'proforma.invoice'
    _description = "Proforma Invoice"

    def calculate_product_cost(self, cr, uid, ids, field_names, args, context=None):
        product_cost={}
        sum=0
        for items in self.pool.get("proforma.invoice").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.product_lines:
                total_list.append(amount.bdttotal_price)

            for item in total_list:
                sum=item+sum
                # import pdb
                # pdb.ser_trace()
        product_cost[ids[0]]=sum
        return product_cost

    def calculate_service_cost(self, cr, uid, ids, field_names, args, context=None):
        service_cost={}
        sum=0
        for items in self.pool.get("proforma.invoice").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.service_lines:
                total_list.append(amount.total_cost)

            for item in total_list:
                sum=item+sum
        service_cost[ids[0]]=sum
        return service_cost

    def calculate_total(self, cr, uid, ids, field_names, args, context=None):
        service_cost={}
        sum=0
        items=self.pool.get("proforma.invoice").browse(cr,uid,ids,context=None)

        sum=items.ptotal+items.stotal
        # import pdb
        # pdb.set_trace()


        service_cost[ids[0]]=sum
        return service_cost


    _columns = {
        'name': fields.char('PI NO'),
        'pi_date': fields.datetime('Date', required=True),
        'description': fields.text('Description'),
        'pi_ref': fields.char('PI Reference No'),
        'lot_no': fields.char('PI Lot No'),
        'vendor_id': fields.many2one('res.partner', 'Vendor name', select=True),
        'paid':fields.float('Paid Amount'),
        'due_amount': fields.float('Due Amount'),

        # 'total':fields.integer("ksksl"),
        # 'total': fields.function(calculate_total,type='float',string='Total',store=True),
        # 'curency': fields.selection([('usd', 'USD$'), ('bdt', 'BDT'), ('others', 'Others')], string='Curency', default='usd'),
        # 'equivalant': fields.float('Conversion Rate BDT'),
        'ptotal': fields.function(calculate_product_cost,type='float',string='Product Total', store=True),
        'stotal': fields.function(calculate_service_cost,type='float',string='Service Total', store=True),
        'total': fields.function(calculate_total, type='float', string='Grand Total', store=True),

        'state': fields.selection([
            ('pending', 'Pending'),
            ('confirm', 'Confirmed'),
            ('received','Received'),
            ('cancel', 'Cancelled'),

        ], 'Status', readonly=True, copy=False, help="Gives the status of the Proforma Invoices", select=True),
        'internal_state': fields.selection([
            ('available', 'Available'),
            ('booked', 'Booked'),
            ('sold', 'Sold'),
            ('cancel', 'Cancelled'),

        ], 'Internal Status', readonly=True, copy=False, help="Gives the status of the Proforma Invoices", select=True),

        'product_lines': fields.one2many('pi.product.line', 'pi_id', 'PI Product Lines', required=True),
        'service_lines': fields.one2many('pi.service.line', 'pi_id', 'PI Service Lines', required=False),
        'po_id': fields.many2one('purchase.order','Purchase Order'),
        'payment_lines': fields.one2many('pi.payment.line', 'pi_id', 'PI payment Lines')


    }

    def convert_to_po(self,cr,uid,ids,context=None):
        data=self.read(cr,uid,ids,['ptotal','vendor_id'],context=context)

        # 'pi_id': fields.many2one('proforma.invoice', 'PI Ids', required=True, ondelete='cascade', select=True,
        #                          readonly=True),
        # 'product_id': fields.many2one('product.product', 'Product Name', required=True),
        # 'uom': fields.selection([('kg', 'KG'), ('pound', 'Pound')], 'UoM'),
        # 'quantity': fields.float('Quantity/KG'),
        # 'currencyunit_price': fields.float('Foreign Price/kg'),
        # 'currencytotal_price': fields.float('Foreign Price(TOTAL)'),
        # 'bdt_rates': fields.float('Conversion Rate'),
        # 'bdtunit_price': fields.float('unit price bdt'),
        # 'bdttotal_price': fields.float('Total Price (BDT)'),
        # 'calculated_unit_price': fields.float('Calculated Unit Price'),
        # 'calculated_total_price': fields.float('Calculated Total Price'),

        for pi_obj in self.browse(cr, uid, ids, context=context):
            # import pdb
            # pdb.set_trace()

            total_service_value = 0
            total_product_value = 0

            for s_items in pi_obj.service_lines:
                total_service_value += s_items.total_cost


            for p_items in pi_obj.product_lines:
                total_product_value += p_items.bdttotal_price

            tmp_list =[]
            fraction = 0
            quantity=0
            for p_items in pi_obj.product_lines:
                fraction = 0

                fraction = p_items.bdttotal_price/total_product_value
                calculated_total_cost = p_items.bdttotal_price + (total_service_value * fraction)
                quantity=p_items.quantity


                if p_items.quantity > 0:
                    calculated_unit_price = calculated_total_cost / p_items.quantity
                else:
                    calculated_unit_price = 0

                tmp_list.append(
                    {
                        'product_id':p_items.product_id.id,
                        'calculated_unit_price':calculated_unit_price,
                        'calculated_total_cost':calculated_total_cost,
                        'id':p_items.id
                    }
                )
            for item in tmp_list:
                cr.execute('update pi_product_line set calculated_unit_price=%s where id=%s', (item.get("calculated_unit_price"),item.get("id")))
                cr.execute('update pi_product_line set calculated_total_price=%s where id=%s', (item.get("calculated_total_cost"),item.get("id")))
                cr.commit()


            purchase_vals={}
            purchase_vals["origin"] = False
            purchase_vals["message_follower_ids"] = False
            child_list=[]

            for product_items in pi_obj.product_lines:
                # import pdb
                # pdb.set_trace()
                order_tmp_dict = {}
                order_tmp_dict['product_id']= product_items.product_id.id
                order_tmp_dict['product_uom']= 5
                order_tmp_dict['date_planned'] = datetime.now()
                order_tmp_dict['price_unit']=product_items.calculated_unit_price
                order_tmp_dict['taxes_id']= []
                order_tmp_dict['product_qty']= product_items.quantity
                order_tmp_dict['account_analytic_id']= False
                order_tmp_dict['name']=product_items.product_id.name
                child_list.append([0,False,order_tmp_dict])

                    # 'product_uom': 5,
                    # 'date_planned': '2019-11-18',
                    # 'price_unit': calculated_unit_price,
                    # 'taxes_id': [[6, False, []]],
                    # 'product_qty': 1,
                    # 'account_analytic_id': False,
                    # 'name': 'Service'

            purchase_vals["order_line"] =child_list
            # purchase_vals["order_line"] = [[0, False, order_tmp_dict]]
            purchase_vals["company_id"] = 1
            purchase_vals["currency_id"] = 1
            purchase_vals["date_order"] = '2019-11-18 12:17:13'
            purchase_vals["location_id"] = 12
            purchase_vals["message_ids"] = False
            purchase_vals["dest_address_id"] = False
            purchase_vals["fiscal_position"] = False
            purchase_vals["picking_type_id"] = 1
            purchase_vals["partner_id"] = 1
            purchase_vals["journal_id"] = 2
            purchase_vals["bid_validity"] = False
            purchase_vals["pricelist_id"] = 2
            purchase_vals["incoterm_id"] = False
            purchase_vals["payment_term_id"] = False
            purchase_vals["partner_ref"] = '0'
            purchase_vals["name"] = "PO001"+str(pi_obj.id)
            purchase_vals["notes"] = False
            purchase_vals["invoice_method"] = 'order'
            purchase_vals["minimum_planned_date"] = False





           ## Update By Kazi
            #
            # po_vals ={}
            #
            purchase_obj = self.pool.get('purchase.order')
            purchase_id = purchase_obj.create(cr, uid, vals=purchase_vals, context=context)

            ###

            ## Link up with PO
            # cr.execute('update proforma_invoice set po_id=%s where id=%s',(purchase_id,pi_obj ))
            cr.execute('update purchase_order set pi_id=%s where id=%s',(pi_obj.id,purchase_id ))
            cr.commit()
            ## Ends He


        return purchase_id


    def _get_act_window_dict(self, cr, uid, name, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.xmlid_to_res_id(cr, uid, name, raise_if_not_found=True)
        result = act_obj.read(cr, uid, [result], context=context)[0]
        return result

    def confirm(self,cr,uid,ids,context=None):

        if ids is not None:
            cr.execute("update proforma_invoice set state='confirm' where id=%s", (ids))
            cr.commit()
        return True

    def received_goods(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update proforma_invoice set state='received',internal_state='available' where id=%s", (ids))
            cr.commit()
        return True
    def action_cancel(self, cr, uid, ids, context=None):
        """ Sets state to cancel.
        @return: True
        """
        return self.write(cr, uid, ids, {'state':'cancel'}, context=context)

    def cancel_pi(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update proforma_invoice set state='cancel' where id=%s", (ids))
            cr.commit()
        return True

    def add_service(self,cr,uid,ids,context=None):
        # import pdb
        # pdb.set_trace()
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cma_galib', 'add_service_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'add.service',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'pi_id':ids[0]
                # 'default_price': 500,
                # # 'default_name':context.get('name', False),
                # 'default_total_amount': 200,
                # 'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                # 'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                # 'default_reference': inv.name,
                # 'close_after_process': True,
                # 'invoice_type': inv.type,
                # 'invoice_id': inv.id,
                # 'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                # 'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))


    def add_payment(self,cr,uid,ids,context=None):

        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cma_galib', 'pi_payment_form_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'pi.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'pi_id':inv.id,
                # 'default_price': 500,
                # # 'default_name':context.get('name', False),
                # 'default_total_amount': 200,
                # 'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                # 'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                # 'default_reference': inv.name,
                # 'close_after_process': True,
                # 'invoice_type': inv.type,
                # 'invoice_id': inv.id,
                # 'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                # 'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))



    _defaults = {
        'pi_date': fields.datetime.now,
        'state': 'pending',

    }
    def add_services(self,cr,uid,ids,context=None):
        values = {}
        abc = {'service_lines': []}
        abc['service_lines'].append([0, False, {'service_name': 'slkfja', 'total_cost': 400}])
        values['value']=abc

        return values


    def create(self, cr, uid, vals, context=None):
        pi_id = super(proforma_invoice, self).create(cr, uid, vals, context=context)
        # import pdb
        # pdb.set_trace()
        #
        #

        if pi_id is not None:
            sample_text = 'PI-00' + str(pi_id)
            cr.execute('update proforma_invoice set name=%s where id=%s', (sample_text, pi_id))
            cr.commit()

        return pi_id

    def write(self, cr, uid, ids, vals, context=None):
        cr.execute("select state from  proforma_invoice where id=%s", (ids))
        result_list = cr.fetchall()
        # import pdb
        # pdb.set_trace()

        for item in result_list:
            if str(item[0]) == 'done' or str(item[0]) == 'cancel':
                raise osv.except_osv(_('Message'), _("Sorry You Can not Edit it. Because it is already confirmed/Cancelled."))
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(proforma_invoice, self).write(cr, uid, ids, vals, context=context)
        return res



class pi_product_line(osv.osv):
    _name = 'pi.product.line'
    _description = "PI Product List"


    # def _calculateunit(self,cr,uid,ids,field_name,arg,context=None):
    #
    # #     unitcalculate={}
    # #     sum=0
    # #     for item in self.pool.get("proforma.invoice").browse(cr,uid,ids,context=None):
    # #         current_rate=item.equivalant
    # #         for items in self.pool.get('pi.product.line').browse(cr,uid,ids,context=None):
    # #
    # #             currencyunit=items.cunit_price
    # #             # bdtunit=current_rate*currencyunit
    # #             import pdb
    # #             pdb.set_trace()
    # #
    # #     for record in self.browse(self,cr,uid,ids,context=None):
    # #         unitcalculate[record.id]=bdtunit
    #
    #     return 0

    _columns = {
        'pi_id': fields.many2one('proforma.invoice', 'PI Ids', required=True, ondelete='cascade', select=True,readonly=True),
        'product_id': fields.many2one('product.product', 'Product Name', required=True),
        'uom': fields.selection([('kg', 'KG'), ('pound', 'Pound')], 'UoM'),
        'quantity': fields.float('Quantity/KG'),
        'available_qty': fields.float('Available Quantity'),
        'currencyunit_price':fields.float('Foreign Price/kg'),
        'currencytotal_price': fields.float('Foreign Price(TOTAL)'),
        'bdt_rates': fields.float('Conversion Rate'),
        'bdtunit_price': fields.float('Unit Price (BDT)'),
        'bdttotal_price':fields.float('Total Price (BDT)'),
        'calculated_unit_price':fields.float('Calculated Unit Price'),
        'calculated_total_price':fields.float('Calculated Total Price'),

    }



    def onchange_unit(self,cr,uid,ids,product_id,quantity,currencyunit_price,context=None):
        tests = {'values': {}}
        total_currency=currencyunit_price*quantity
        abc = {'currencytotal_price': total_currency,}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_quantity(self,cr,uid,ids,product_id,quantity,currencyunit_price,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('product.product').browse(cr, uid, product_id, context=None)
        cunit_prices=currencyunit_price
        total=cunit_prices*quantity
        abc = {'currencytotal_price': total}
        tests['value'] = abc

        return tests

    def onchange_conversion(self,cr,uid,ids,product_id,currencytotal_price,quantity,bdt_rates,currencyunit_price,context=None):
        tests = {'values': {}}
        bdtunit_price=bdt_rates*currencyunit_price
        total_bdt_price=currencytotal_price*bdt_rates
        # import pdb
        # pdb.set_trace()
        abc = {'bdtunit_price': bdtunit_price,'bdttotal_price':total_bdt_price}
        tests['value'] = abc


        return tests


class purchase_order(osv.osv):
    _inherit = "purchase.order"

    _columns = {
        'pi_id': fields.many2one('proforma.invoice', string='Purchase Order')
    }




class pi_service_line(osv.osv):
    _name = 'pi.service.line'
    _description = "PI service List"

    def onchange_quantity(self,cr,uid,ids,service_cost,quantity,context=None):
        tests = {'values': {}}
        total_cost = service_cost * quantity
        # import pdb
        # pdb.set_trace()
        abc = {'total_cost': total_cost}
        tests['value'] = abc
        return tests

    _columns = {
        'pi_id': fields.many2one('proforma.invoice', 'PI Ids', ondelete='cascade', select=True, readonly=True),
        'service_name': fields.char('Service name'),
        'service_cost': fields.float('Service cost/KG'),
        'quantity': fields.float('Quantity'),
        'total_cost':fields.float('Total Cost'),
        'add_service_id': fields.many2one('add.service')

    }

class pi_payment(osv.osv):
    _name = 'pi.payment.line'
    _description = "Pi Payment"


    _columns = {
        'pi_id': fields.many2one('proforma.invoice', 'PI ID', ondelete='cascade', select=True,required=True, readonly=True),
        'amount': fields.float('Amount', required=True),
        'date': fields.datetime('Date',required=True),
        'type': fields.char('Type'),
        'comments': fields.text('Description/Comments'),
        'usd_amount': fields.float('USD')
    }
    # def create(self,cr,uid,vals,context=None):
    #     import pdb
    #     pdb.set_trace()


