from odoo import fields, models


class SgwWhoisQuery(models.Model):
    _name = "sgw.whoisquery"
    _order = "date_query desc"

    date_query = fields.Datetime(
        "Date Whois Query",
        required=False,
        readonly=False,
        select=True,
        default=lambda self: fields.datetime.now(),
    )
    sld = fields.Char("Name of domain", required=True)
    tld = fields.Char("tld", required=True)
    free = fields.Boolean("free")
    whois_raw = fields.Text("Whois raw of domain")
