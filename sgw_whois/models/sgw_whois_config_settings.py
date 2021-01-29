import logging

from odoo import models

_logger = logging.getLogger(__name__)


class WhoisResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
