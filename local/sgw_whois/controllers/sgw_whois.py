import imp
import json

from odoo import conf, http
from odoo.http import Response, request

from odoo.addons.website.controllers.main import Website


fp, pathname, description = imp.find_module("sgw_whois", conf.addons_paths)
sgw_whois = imp.load_module("sgw_whois", fp, pathname, description)


class WhoisController(Website):
    def _get_tlds_exts(self):
        tlds_exts = []
        tlds_ids = self._get_tlds_ids()
        for p in tlds_ids:
            tlds_exts += p.list_tlds.split(",")
        return sorted(tlds_exts)

    def _get_tlds_ids(self):
        app_obj = request.env["product.template"].sudo()
        tlds_ids = app_obj.search([("is_tld", "!=", False)])

        return tlds_ids

    @http.route(["/get_tlds_exts"], auth="public", type="http", website=True)
    def get_tlds_exts(self):
        results = self._get_tlds_exts()
        return json.dumps(results)

    def chk_domain_free(self, domain=None, tld=None):
        # @returns "Taken", "Free" or "Error"
        result = "Taken"
        r = True
        whois_txt = ""
        if domain is not None and tld is not None:
            try:
                name = domain + "." + tld
                w = http.request.env['sgw.whoisquery'].whois(name)
                if not w["is_taken"]:
                    result = "Free"
                    r = False
            except Exception:
                result = "Error"
                r = True
            obj_log = request.env["sgw.whoisquery"].sudo()
            obj_log.create(
                {"sld": domain, "tld": tld, "is_taken": r, "whois_raw": whois_txt}
            )
        return result

    @http.route(["/get_status"], auth="public", type="http", website=True, csrf=True)
    def get_status(self, domain, tld):
        result = '<i class="fa fa-times-circle fa-lg text-danger"></i><span style ="margin-left:10px;" class="text-danger">Not available</span>'
        status = self.chk_domain_free(domain, tld)
        if status == "Free":
            result = '<i class="fa fa-check-circle fa-lg text-success"></i><span style ="margin-left:10px;" class="text-success">Available</span> '
        if status == "Error":
            result = '<i class="fa exclamation-circle fa-lg text-warning"></i><span style ="margin-left:10px;" class="text-warning">Error</span> '
        return Response(result, content_type="text/html;charset=utf-8")

    @http.route("/whois", auth="public", website=True, csrf=True)
    def whoisdomain(self, domain=None, **kwargs):
        results = {}  # tmp
        values = {}  # values to return
        validated_domain = ""
        domain = None
        obj_form = http.request.httprequest.form
        if "domain" in obj_form:
            domain = obj_form["domain"]
        if domain is not None:
            if domain.__contains__("."):
                domain = domain.split(".")[0]
            tlds_ids = self._get_tlds_ids()
            for p in tlds_ids:
                tlds_exts = p.list_tlds.split(",")
                for i in tlds_exts:
                    results.update({i: [p, "placeholder1", "placeholder2"]})
            valid = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
            validated_domain = domain
            for c in list(domain):
                if c not in valid:
                    validated_domain = validated_domain.replace(c, "")
        values = {
            "domain": validated_domain,
            "results": results,
        }
        return http.request.render("sgw_whois.whois_check", values)

    @http.route("/get_whois_raw", auth="public", type="http", website=True, csrf=True)
    def get_whois_raw(self, domain=None, **kwargs):
        result = ""
        try:
            name = domain
            w = http.request.env['sgw.whoisquery'].whois(name)
            result = w.get("raw")[0].replace("\n", "<br/>")
        except Exception:
            result = "Error"
        return Response(result, content_type="text/html;charset=utf-8")
