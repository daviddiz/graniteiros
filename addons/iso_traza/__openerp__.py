# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Software de Trazabilidad de Explosivos',
    'version': '0.15',
    'category': 'Stock',
    'description': """Software para la trazabilidad de productos explosivos.""",
    'author': 'David Diz Martínez (daviddiz@gmail.com)',
    'website': '',
    'depends': ['stock',
                 ],
    'init_xml': [],
    'update_xml': ['security/iso_traza_security.xml',
                   'security/ir.model.access.csv',
                   'iso_traza_sequence.xml',
                   'iso_traza_view.xml',
                   'iso_traza_report.xml',
                   'board_iso_traza_view.xml',
                   'wizard/iso_traza_report_acta_view.xml',
                   'wizard/iso_traza_report_libro_view.xml',
                   'wizard/iso_traza_acta_new_view.xml',
                   'wizard/iso_traza_libro_new_view.xml',
                   'wizard/iso_traza_import_picking.xml',
                   'wizard/iso_traza_import_products.xml',
                   'wizard/iso_traza_import_products_epc.xml',
                   'wizard/iso_traza_albaran_to_acta_view.xml',
                   'data/iso_traza_data_uom.xml',
                   'data/iso_traza_data_trad_draft.xml',
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
