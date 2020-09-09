# -*- coding: utf-8 -*-

from suds.sudsobject import asdict
from OpenSSL import crypto
from subprocess import check_output, CalledProcessError
import subprocess

from odoo import models, fields, api
from odoo.exceptions import Warning

from suds.client import Client, WebFault
import tempfile
import base64
import requests
import json
import logging

_logger = logging.getLogger("========= TIMBRADO =========")


class PacConfig(models.Model):
    _name = 'cfdi.pac.config'

    name = fields.Char('Identificador del Registro', required=True, help="Ponga un nombre a este registro para identificarlo de manera simple.")
    user = fields.Char('Usuario', required=True)
    password = fields.Char('Contraseña', required=True)
    url = fields.Char('URL del Servicio de Timbrado', required=True)
    cer = fields.Binary('Certificado (CER)', required=True)
    cer_name = fields.Char('Cer file name')
    key = fields.Binary('Llave (KEY)', required=True)
    key_name = fields.Char('Key file name')
    key_pem = fields.Char('KEY PEM', compute='_compute_key_pem', store=True)
    contrasena = fields.Char('Contraseña de la llave', required=True)
    no_cer = fields.Char('No. Certificado', compute='_compute_cer', store=True)
    start_date = fields.Date('Inicio Vigencia', compute='_compute_cer', store=True)
    end_date = fields.Date('Fin Vigencia', compute='_compute_cer', store=True)
    active = fields.Boolean('Activo', default=True)
    timbres = fields.Integer('Timbres usados')
    cancelaciones = fields.Integer('Cancelaciones usadas')

    def timbrar_xml(self,json_invoice):
        json_invoice['Cliente'] = {'Usuario':self.user,'Password':self.password}
        json_invoice['Service'] = 'Timbrar'
        url = self.url
        try:
            response = requests.post(url,auth=None, verify=False, data=json.dumps({'params':json_invoice}),headers={"Content-type": "application/json"})
        except Exception as e:
            return {
                'validate': False,
                'code': e,
                'description': "hubo un error",
            }
        result = json.loads(response.content.decode()).get('result')
        return result

    @api.onchange('url')
    def _check_url(self):
        if self.url and len(self.url) > 0:
            try:
                response = requests.post(self.url,auth=None, verify=False, data=json.dumps({'params':'Disponible'}),headers={"Content-type": "application/json"})
            except:
                raise Warning('No es posible conectarse con el PAC en la URL especificada.')
            if '404' in response:
                raise Warning('No es posible conectarse con el PAC en la URL especificada.')

    @api.depends('cer')
    def _compute_cer(self):
        for r in self:
            if r.cer and len(r.cer) > 0:
                cer = crypto.load_certificate(crypto.FILETYPE_ASN1, base64.b64decode(r.cer))
                no_cer = "%x" % cer.get_serial_number()
                _logger.warning(no_cer)
                r.no_cer = no_cer.replace('33', '@').replace('3', '').replace('@', '3')
                _logger.warning(no_cer)
                _logger.warning(cer.get_notBefore()[:4])
                _logger.warning(cer.get_notBefore()[4:6])
                _logger.warning(cer.get_notBefore()[6:8])
                _logger.warning("%s-%s-%s" %((cer.get_notBefore()[:4]).decode(),(cer.get_notBefore()[4:6]).decode(),(cer.get_notBefore()[6:8]).decode()))
                r.start_date = "%s-%s-%s" %((cer.get_notBefore()[:4]).decode(),(cer.get_notBefore()[4:6]).decode(),(cer.get_notBefore()[6:8]).decode())
                _logger.warning(r.start_date )
                r.end_date = "%s-%s-%s" %((cer.get_notBefore()[:4]).decode(),(cer.get_notBefore()[4:6]).decode(),(cer.get_notBefore()[6:8]).decode())

    @api.depends('key', 'contrasena')
    def _compute_key_pem(self):
        for r in self:
            if r.key and r.contrasena and len(r.key) > 0 and len(r.contrasena) > 0:
                fname_key = tempfile.NamedTemporaryFile().name
                file_key = open(fname_key, "wb")
                file_key.write(base64.b64decode(r.key))
                file_key.flush()
                file_key.close()
                fname_password = tempfile.NamedTemporaryFile().name
                file_password = open(fname_password, "w")
                file_password.write(r.contrasena)
                file_password.flush()
                file_password.close()
                cmd = 'openssl pkcs8 -inform DER -outform PEM -in %s -passin file:%s' % (
                    fname_key, fname_password)
                _logger.warning(cmd)
                args = cmd.split(' ')
                _logger.warning(args)
                try:
                    output = check_output(args, stderr=subprocess.STDOUT)
                except CalledProcessError as e:
                    raise Warning("No se puede abrir la llave (key) con la contraseña proporcionada.\n"
                                  "¿Selecciono el archivo correcto?\n"
                                  "¿La contraseña es correcta, incluyendo mayúsculas y minúsculas?\n"
                                  "%s" % e.output)
                r.key_pem = output

    def _to_dict(self, d):
        out = {}
        for k, v in asdict(d).iteritems():
            if hasattr(v, '__keylist__'):
                out[k] = self._to_dict(v)
            elif isinstance(v, list):
                out[k] = []
                for item in v:
                    if hasattr(item, '__keylist__'):
                        out[k].append(self._to_dict(item))
                    else:
                        out[k].append(item)
            else:
                if isinstance(v, str):
                    v = v.decode('utf-8', errors='ignore')
                if isinstance(v, unicode):
                    v = v.encode('utf-8', errors='ignore')
                out[k] = v
        return out
