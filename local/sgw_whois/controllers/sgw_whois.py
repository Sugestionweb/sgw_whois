import imp
import json
from logging import error
import re

from odoo import conf, http
from odoo.http import Response, request

from odoo.addons.website.controllers.main import Website


fp, pathname, description = imp.find_module("sgw_whois", conf.addons_paths)
sgw_whois = imp.load_module("sgw_whois", fp, pathname, description)


class WhoisController(Website):
    def _get_tlds_exts(self):
        """Return a new list containing all tlds in ascending order."""
        tlds_exts = []
        tlds_ids = self._get_all_tlds_ids()
        for p in tlds_ids:
            tlds_exts += p.list_tlds.split(",")
        return sorted(tlds_exts)

    def _get_tld_id(self, tld):
        """Returns the record of the tld passed

        Args:
            tld ([string]): [tld to search]

        Returns:
            [records]: [record of the tld]
        """
        app_obj = request.env["product.template"].sudo()
        domain = [
            "&",
            ["is_tld", "=", True],
            "|",
            "|",
            ["list_tlds", "ilike", ",com"],
            ["list_tlds", "ilike", "com,"],
            ["list_tlds", "=", "com"],
        ]
        tlds_ids = app_obj.search(domain, limit=1)
        return tlds_ids

    def _get_all_tlds_ids(self):
        """ Return a records list of all products marked as tld"""
        app_obj = request.env["product.template"].sudo()
        tlds_ids = app_obj.search([("is_tld", "!=", False)])
        return tlds_ids

    @http.route(["/get_tlds_exts"], auth="public", type="http", website=True)
    def get_tlds_exts(self):
        """ Public method, Return all tlds"""
        results = self._get_tlds_exts()
        return json.dumps(results)

    def _get_full_name(self, domain, tld):
        """Returns the fullname of domain with name, a dot, and tld

        Args:
            domain ([string], required): [description]. Defaults to None.
            tld ([string], required): [description]. Defaults to None.

        Returns:
            [string]: [full name of domain eg. google.com]
        """
        if domain is not None and tld is not None:
            full_name = domain + "." + tld
            return full_name

    def _log_whois(self, domain, tld, is_taken, whois_raw):
        """
        Log the whois action and result in table log_whois

        Args:
            domain ([string]): [description]
            tld ([string]): [description]
            is_taken (bool): [description]
            whois_raw ([string]): [description]

        Returns:
            [None]: This function not returns nothing
        """
        obj_log = request.env["sgw.whoisquery"].sudo()
        obj_log.create(
            {"sld": domain, "tld": tld, "is_taken": is_taken, "whois_raw": whois_raw}
        )

        return None

    def _chk_domain_free(self, domain=None, tld=None):
        """
        This function get domain + tld and makes a query to whois servers.
        Then, it determines if the domain is taken or available to register.

        Args:
            [domain] ([string], optional): [name of domain eg. 'google']. Defaults to None.
            [tld] ([type], optional): [tld of domain eg. '.com']. Defaults to None.

        Returns:
            Literal['Free', 'Taken', 'Error']
        """

        # result = "Taken"
        r = None
        whois_txt = ""
        result = ""
        name = self._get_full_name(domain, tld)

        try:
            w = http.request.env["sgw.whoisquery"].whois(name)
            whois_txt = w.get("raw")[0]
            if not w["is_taken"]:
                result = "Free"
                r = False
        except Exception:
            result = "Error"
            r = None

        self._log_whois(name, tld, r, whois_txt)

        # obj_log = request.env["sgw.whoisquery"].sudo()
        # obj_log.create(
        #     {"sld": domain, "tld": tld, "is_taken": r, "whois_raw": whois_txt}
        # )

        return result

    @http.route(["/get_status"], auth="public", type="http", website=True, csrf=True)
    def get_status(self, domain, tld):
        result = '<i class="fa fa-times-circle fa-lg text-danger"></i><span style ="margin-left:10px;" class="text-danger">Not available</span>'
        status = self._chk_domain_free(domain, tld)
        if status == "Free":
            result = '<i class="fa fa-check-circle fa-lg text-success"></i><span style ="margin-left:10px;" class="text-success">Available</span> '
        if status == "Error":
            result = '<i class="fa exclamation-circle fa-lg text-warning"></i><span style ="margin-left:10px;" class="text-warning">Error</span> '
        return Response(result, content_type="text/html;charset=utf-8")

    def _validate_domain(self, domain_name):
        domain_regex = r"(([\da-zA-Z])([_\w-]{,62})\.){,127}(([\da-zA-Z])[_\w-]{,61})?([\da-zA-Z]\.((xn\-\-[a-zA-Z\d]+)|([a-zA-Z\d]{2,})))"
        domain_regex = "{0}$".format(domain_regex)
        valid_domain_name_regex = re.compile(domain_regex, re.IGNORECASE)
        # domain_name = domain_name.lower().strip().encode('ascii')
        if re.match(valid_domain_name_regex, domain_name):
            return True
        else:
            return False

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
                if self._validate_domain(domain):
                    domain_name = domain.split(".")[0]
                    validated_domain = domain_name
            else:  # Caso google (viene sin .) buscamos todas
                domain = domain + ".com"  # Temporary add ext. for validation purposes only
                if self._validate_domain(domain):
                    domain = domain.split(".")[0]
                    validated_domain = domain
            tlds_ids = self._get_all_tlds_ids()
            for p in tlds_ids:
                tlds_exts = p.list_tlds.split(",")
                for i in tlds_exts:
                    results.update({i: [p, "placeholder1", "placeholder2"]})

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
            w = http.request.env["sgw.whoisquery"].whois(name)
            result = w.get("raw")[0].replace("\n", "<br/>")
            errs = ["Errno 104", "Errno -2"]

            if any(errors in result for errors in errs):
                raise Exception(name, w, result)

        except Exception:
            result = ("Error: %s ") % result

        return Response(result, content_type="text/html;charset=utf-8")
