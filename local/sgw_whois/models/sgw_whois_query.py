from odoo import fields, models
from . import sgw_net, sgw_parse


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

    def whois(domain, normalized=None):
        if normalized is None:
            normalized = []
        raw_data, server_list = sgw_net.get_whois_raw(domain, with_server_list=True)
        return sgw_parse.parse_raw_whois(
            raw_data,
            normalized=normalized,
            never_query_handles=False,
            handle_server=server_list[-1],
            name_domain=domain,
        )9
