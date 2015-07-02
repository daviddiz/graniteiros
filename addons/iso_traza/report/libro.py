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

from report import report_sxw

class libro(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(libro, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'process':self.process_lines,
        })
        
    def process_lines(self,form):
        obra_id = form['obra_id']
        date_from = form['date_from']
        date_to = form['date_to']
        obra_id = form['obra_id']
        
        
        lineas = []
        
        
        return lineas
#         acta_obj = pooler.get_pool(self.cr.dbname).get('iso.traza.acta')
#         move_obj = pooler.get_pool(self.cr.dbname).get('stock.move')
#         moves_id = move_obj.search(self.cr,self.uid, [('acta_id', '=', acta_id)])

#         movimientos = []
#         for move_id in moves_ids:
#             m = {}
#             m['nombre'] = move_id.product_id.name
#             m['serial'] = move_id.serial
#             m['cantidad'] = move_id.product_qty
#             m['unidad'] = move_id.product_uom.name
#             movimientos.append(m)
#         movimientos.sort(key=lambda d:(d['nombre'],d['serial']))

#         nombre = ""
#         aux = 0
#         serial_anterior = 0
#         lineas = []
#         data = {}
#         for movimiento in movimientos:
#             if nombre <> movimiento['nombre']:
#                 if data:
#                     if aux==2 and serial_anterior:
#                         data['serial'] = data['serial'] + "\n" + serial_anterior
#                     data['entregado'] = float("%1.f" % data['entregado'])
#                     data['sobrante'] = float("%1.f" % data['sobrante'])
#                     data['consumido'] = float("%1.f" % data['consumido'])
#                     lineas.append(data)
#                     data = {}
#                 aux = 0
#                 nombre = movimiento['nombre']
#                 data['nombre'] = movimiento['nombre']
#                 data['unidad'] = movimiento['unidad']    
#                 data['serial'] = movimiento['serial']
#                 serial_anterior = movimiento['serial']
#                 data['entregado'] = 0.0
#                 data['sobrante'] = 0.0
#                 if movimiento['cantidad']>0:
#                     data['entregado'] = movimiento['cantidad']
#                 else:
#                     data['sobrante'] = abs(movimiento['cantidad'])
#                 data['consumido'] = data['entregado'] - data['sobrante']  
#                 data['consumido'] = abs(data['consumido'])
#             else:
#                 if int(movimiento['serial'][-6:]) == ( int(serial_anterior[-6:]) + 1 ):
#                     if aux==0:
#                         data['serial'] = data['serial'] + "\n" + "          al"
#                         aux = 2
#                         serial_anterior = movimiento['serial']
#                     elif aux>0:
#                         serial_anterior = movimiento['serial']
#                         aux = 2
#                 else:
#                     if aux>0:
#                         data['serial'] = data['serial'] + "\n" + serial_anterior + "\n" + "    ----------------" + "\n" + movimiento['serial']
#                         serial_anterior = movimiento['serial']
#                         aux = 0
#                     else:
#                         data['serial'] = data['serial'] + "\n" + movimiento['serial']
#                         serial_anterior = movimiento['serial']
#                         aux = 0
#                 if movimiento['cantidad']>0:
#                     data['entregado'] = data['entregado'] + movimiento['cantidad']
#                 else:
#                     data['sobrante'] = data['sobrante'] + abs(movimiento['cantidad'])
#                 data['consumido'] = data['entregado'] - data['sobrante']
#                 data['consumido'] = abs(data['consumido'])
#         if aux==2 and serial_anterior:
#             data['serial'] = data['serial'] + "\n" + serial_anterior
#         data['entregado'] = float("%1.f" % data['entregado'])
#         data['sobrante'] = float("%1.f" % data['sobrante'])
#         data['consumido'] = float("%1.f" % data['consumido'])
#         lineas.append(data)
#         return lineas

report_sxw.report_sxw('report.libro', 'iso.traza.libro.report', 'addons/iso_traza/report/libro.rml', parser=libro, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

