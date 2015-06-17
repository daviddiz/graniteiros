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
import pooler
from report import report_sxw

class acta(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(acta, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'process':self.process,
        })
        
    def process(self,moves_ids):
#         acta_obj = pooler.get_pool(self.cr.dbname).get('iso.traza.acta')
#         move_obj = pooler.get_pool(self.cr.dbname).get('stock.move')
#         moves_id = move_obj.search(self.cr,self.uid, [('acta_id', '=', acta_id)])

        movimientos = []
        for move_id in moves_ids:
            m = {}
            m['nombre'] = move_id.product_id.name
            m['serial'] = move_id.serial
            m['cantidad'] = move_id.product_qty
            movimientos.append(m)
        movimientos.sort(key=lambda d:(d['nombre'],d['serial']))

        nombre = ""
        lineas = []
        data = {}
        for movimiento in movimientos:
            if nombre <> movimiento['nombre']:
                if data:
                    lineas.append(data)
                nombre = movimiento['nombre']
                data['nombre'] = movimiento['nombre']
                data['serial'] = movimiento['serial']
                data['entregado'] = 0.0
                data['sobrante'] = 0.0
                if movimiento['cantidad']>0:
                    data['entregado'] = movimiento['cantidad']
                else:
                    data['sobrante'] = abs(movimiento['cantidad'])
            else:
                data['serial'] = data['serial'] + "\n" + movimiento['serial']
                if movimiento['cantidad']>0:
                    data['entregado'] = data['entregado'] + movimiento['cantidad']
                else:
                    data['sobrante'] = data['sobrante'] + abs(movimiento['cantidad'])
        lineas.append(data)
        return lineas

report_sxw.report_sxw('report.acta', 'iso.traza.acta', 'addons/iso_traza/report/acta.rml', parser=acta, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

