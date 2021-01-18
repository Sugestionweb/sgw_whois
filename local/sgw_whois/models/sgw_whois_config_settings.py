# -*- coding: utf-8 -*-

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WhoisResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
