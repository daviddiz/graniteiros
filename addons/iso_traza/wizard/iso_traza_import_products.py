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

from osv import osv,fields
import os
import base64

class iso_traza_import_products(osv.osv_memory):
    _name = 'iso.traza.import.products'
    _description = 'Importar productos'
    _columns={
        'file': fields.binary('Fichero con productos a Importar (de tipo csv cuyas líneas están compuestas por un código de 11 caracteres seguidos de una coma y el nombre del producto)'),
    }
    
    _defaults = {
    }
    
    def import_products(self, cr, uid, ids, context=None):
        content = self.browse(cr,uid,ids)[0].file
        decode_content = content.decode('base64')
        for product in decode_content.split('\n'):
            ref = product[0:11]
            product_name = product[12:]
            
            p_template_vals = {
                'supply_method': 'buy',
                'standard_price': 1.00,
                'mes_type': 'fixed',
                'uom_id': 1,
                'uom_po_id': 1,
                'name': product_name,
                'description': product_name,
                'description_purchase': product_name,
                'description_sale': product_name,
                'type': 'consu',
                'procure_method': 'make_to_stock',
                'categ_id': 1,
                'cost_method': 'standard',
                'warranty': 0,
                'purchase_ok': True,
                'company_id': 1,
                'rental': False,
                'sale_ok': True,
                'sale_delay': 7,
                'produce_delay': 1,
            }
             
            product_template_id = self.pool.get('product.template').create(cr, uid, p_template_vals)
              
            p_product_vals = {
                'product_tmpl_id': product_template_id,
                'default_code': ref,
                'valuation': 'manual_periodic',
                'lot_split_type': 'single',
                'price_extra': 0.00,
                'name_template': product_name,
                'active': True,
                'price_margin': 1.00,
                'track_production': False,
                'track_outgoing': False,
                'track_incoming': True,
            }
             
            product_product_id = self.pool.get('product.product').create(cr, uid, p_product_vals)
            
        return False



iso_traza_import_products()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
