from odoo import fields, models


class SgwWhoisQuery(models.Model):
    _name = "sgw.whoisquery"
    _order = "date_query desc"
    _description = "Model to save the queries made using the whois module"

    date_query = fields.Datetime(
        "Date Whois Query",
        required=False,
        readonly=False,
        default=lambda self: fields.datetime.now(),
    )
    sld = fields.Char("Name of domain", required=True)
    tld = fields.Char("tld", required=True)
    is_taken = fields.Boolean("is_taken")
    whois_raw = fields.Text("Whois raw of domain")

