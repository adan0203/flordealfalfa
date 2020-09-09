# -*- coding: utf-8 -*-

from odoo import fields, models,api
import csv
import base64
import io
import re
import sys
import logging
_logger = logging.getLogger(__name__)


class AccountwizardLine(models.TransientModel):
    _name = 'account.invoice.wizard.line'
    fac_id = fields.Many2one('account.invoice.wizard','Origen')
    meli_id = fields.Char('ID ML')
    razon = fields.Char('Razon')
    rfc = fields.Char('RFC')
    facturado = fields.Boolean('Facturado')
    email = fields.Char('Correo')
    uso = fields.Char('Uso')
    pago = fields.Char('Pago')


class Accountwizard(models.TransientModel):
    _name = 'account.invoice.wizard'

    archivo = fields.Binary('Csv')
    linea_ids = fields.One2many('account.invoice.wizard.line','fac_id','Lineas')
    fecha_factura = fields.Datetime('Fecha facturacion')

    @api.onchange('archivo')
    def get_datos(self):
        self.ensure_one()
        if self.archivo:
            lineas = []
            csv_data = base64.b64decode(self.archivo)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            csv_reader = csv.reader(data_file, delimiter=',')
            file_reader.extend(csv_reader)

            for r in file_reader:
                if r[0]:
                    dat = {
                        'meli_id': r[0].strip(),
                        'razon': r[2].strip().upper(),
                        'rfc': ''.join(r[3].strip().upper().split(' ')),
                        'email': ''.join(r[4].strip().split(' ')),
                        'facturado': True if r[5] and r[5]!='' else False,
                        'uso': 'G01' if 'merca' in r[6].lower() else 'G03',
                        'pago': '01' if 'efecti' in r[7].lower() else '04' if 'credito' in r[7].lower() else '28' if 'debito' in r[7].lower() else '03'
                    }
                    lineas.append((0,0,dat))
            self.linea_ids = lineas
        else:
            self.linea_ids = None


    def create_fac(self):
        self.ensure_one()
        perdidos = []
        for l in self.linea_ids:
            if l.facturado or not l.razon:
                continue
            pedido = self.env['sale.order'].search([('meli_order_id','=',l.meli_id)])
            if len(pedido)!=1 and (l.razon or l.rfc):
                perdidos.append(l.meli_id)
            else:
                cliente = pedido.partner_id
                cliente.write({'name': l.razon, 'email': l.email, 'vat': l.rfc})
                if pedido.state == 'draft':
                    pedido.action_confirm()
                if pedido.state == 'sale':
                    if pedido.invoice_count == 0:
                        account = pedido._create_invoices()
                        for a in account:
                            a.write({'methodo_pago':'PUE','uso_cfdi':l.uso,'forma_pago':l.pago,'invoice_date_timbrar':self.fecha_factura})
                else:
                    perdidos.append(l.meli_id)

        _logger.warning('#############################')
        _logger.warning(perdidos)
