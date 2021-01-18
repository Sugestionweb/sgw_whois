from odoo import fields, models


class SgwWhoisServer(models.Model):
    _name = "sgw.whois.server"
    _order = "whois_server asc"
    _description = "Whois Servers"
    _rec_name = "whois_server"

    #TODO: Valores por defecto en los formularios al agregar relacionados
    
    whois_server = fields.Char("Whois server", required=True, context={})

    tld_id = fields.One2many(
        "sgw.whois.tld", "whois_server", string="Tld", ondelete="set null"
    )
    word_id = fields.One2many(
        "sgw.whois.serverindicator",
        "whois_server",
        string="Word",
        ondelete="set null",
    )


class SgwWhoisServerIndicator(models.Model):

    _name = "sgw.whois.serverindicator"
    _order = "word"
    _description = "Indicators of availabality of domain"
    _rec_name = "word"

    word = fields.Char("Word", required=True)
    whois_server = fields.Many2one("sgw.whois.server")

    type_indicator = fields.Selection(
        [
            ("Available", "Available"),
            ("Not available", "Not available"),
            ("Error", "Error"),
        ],
        "Indicator Type",
        default="Available",
        required=True,
    )
