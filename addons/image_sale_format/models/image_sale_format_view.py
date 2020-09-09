# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

# class sale_order_inherit(models.Model):
    # _inherit = 'sale.order'