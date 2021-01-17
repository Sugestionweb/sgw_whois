# -*- coding: utf-8 -*-

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WhoisResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    sgwwhois_available_indicators = fields.Char('Available indicators', help=u"Generic List of available indicators separated by ,")
