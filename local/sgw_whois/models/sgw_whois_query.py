import logging
import re
import socket
from codecs import encode

from odoo import fields, models

_logger = logging.getLogger(__name__)

grammar = {
    "_data": {
        "status": [
            r"^state:\s*(?P<val>.+)",
            r"Status\s*:\s?(?P<val>.+)",
            r"\[Status\]\s*(?P<val>.+)",
            r"Status:\s?(?P<val>.+)",
            r"\[State\]\s*(?P<val>.+)",
        ],
    }
}


class SgwWhoisLogQuery(models.Model):
    _name = "sgw.whois.logquery"
    _order = "date_query desc"
    _description = "Model to save the queries made using the whois module"

    date_query = fields.Datetime(
        "Date Whois Query",
        required=False,
        readonly=False,
        default=lambda self: fields.datetime.now(),
    )
    sld = fields.Char("Second Level Domain", required=True)
    tld = fields.Char("Top Level Domain", required=True)
    is_taken = fields.Boolean("is taken?")
    whois_raw = fields.Text("Raw Whois")

    grammar["_data"]["status"] = [
        re.compile(regex, re.IGNORECASE) for regex in grammar["_data"]["status"]
    ]

    def parse_raw_whois(self, raw_data, name_domain, server):
        """Gets the raw_data and parses it in dictionary data.

        Args:
            raw_data ([type]): [description]
            name_domain (str, optional): [description]. Defaults to "".
            server (str, optional): [description]. Defaults to "".

        Returns:
            data [type]: [description]
        """
        data = {}

        raw_data = [segment.replace("\r", "") for segment in raw_data]

        for segment in raw_data:
            for rule_key, rule_regexes in grammar["_data"].items():
                if (rule_key in data) is False:
                    for line in segment.splitlines():
                        for regex in rule_regexes:
                            result = re.search(regex, line)
                            if result is not None:
                                val = result.group("val").strip()
                                if val != "":
                                    try:
                                        data[rule_key].append(val)
                                    except KeyError:
                                        data[rule_key] = [val]

        for key in list(data.keys()):
            if data[key] is None or len(data[key]) == 0:
                del data[key]

        data["raw"] = raw_data

        # Set a bool value that indicates whether the domain is already registered.
        SgwWhoisLogQuery.set_flag_is_taken(self, data, server)

        return data

    def set_flag_is_taken(self, data, server):
        data["is_taken"] = True
        list_free_domain = [
            "free",
            "available",
            "not found",
            "no match",
            "no object found",
        ]

        if "status" in data:
            data["is_taken"] = not data["status"][0].lower() in list_free_domain
        else:
            stop = False
            list_stop = [
                r"The registration of this domain is restricted",
                r"This name is not available for registration",
                r"Reserved Domain Name",
            ]

            for regex in list_stop:
                if re.search(regex, data["raw"][0], re.IGNORECASE) is not None:
                    stop = True
                    break

            if not stop:
                list_ex = [
                    r"%ERROR:101: no entries found",
                    r"No Data Found",
                    r"NOT FOUND",
                    r"Available",
                    r"This query returned 0 objects.",
                    r"No match",
                    r"is free",
                    r"No Object Found",
                    r"Object does not exist",
                    r"no entries found",
                    r"nothing found",
                    r"This domain name has not been registered.",
                    r"%ERROR:103: Domain is not registered",
                    r"El dominio no se encuentra registrado en NIC Argentina",
                    r"Invalid query or domain name not known in Dot CF Domain Registry",
                    r"The domain has not been registered.",
                    r"No such domain",
                    r"domain name not known",
                    r"Object_Not_Found",
                    r"No found",
                ]
                for regex in list_ex:
                    if re.search(regex, data["raw"][0], re.IGNORECASE) is not None:
                        data["is_taken"] = False
                        break

                # Read the specifics indicators for "available" for this whois server
                whois_server_indicators_available = self.env[
                    "sgw.whois.serverindicator"
                ].search(
                    [
                        ("whois_server", "=", server),
                        ("type_indicator", "=", "Available"),
                    ]
                )

                if whois_server_indicators_available:
                    for indicator in whois_server_indicators_available:
                        if (
                            re.search(indicator.word, data["raw"][0], re.IGNORECASE)
                            is not None
                        ):
                            data["is_taken"] = False
                            break

                # Read the specifics indicators for "unavailable" for this whois server.
                # If some rule has put data["is_taken"] = False, this is the last
                # oportunity to put a True
                whois_server_indicators_unavailable = self.env[
                    "sgw.whois.serverindicator"
                ].search(
                    [
                        ("whois_server", "=", server),
                        ("type_indicator", "=", "Not available"),
                    ]
                )
                if whois_server_indicators_unavailable:
                    for indicator in whois_server_indicators_unavailable:
                        if (
                            re.search(indicator.word, data["raw"][0], re.IGNORECASE)
                            is not None
                        ):
                            data["is_taken"] = True
                            break
        return

    def whois(self, domain):

        raw_data, server_list = SgwWhoisLogQuery.get_whois_raw(
            self, domain, with_server_list=True
        )
        result = SgwWhoisLogQuery.parse_raw_whois(self, raw_data, domain, server_list[0])
        return result

    def get_root_server_from_db(self, full_name):
        """Obtains the Whois Server for a tld, querying the database

        Args:
            full_name ([string]): [Full name of Domain including TLD,
            for example google.com]

        Returns:
            [whois_server]: [Whois Server for querying the TLD ]
        """
        tld = full_name.split(".")[-1]
        whois_server = (
            self.env["sgw.whois.tld"]
            .search([("tld", "=", tld)], limit=1)
            .whois_server.whois_server
        )

        if not whois_server:
            whois_server = SgwWhoisLogQuery.get_root_server_from_iana(self, full_name)

        return whois_server

    def get_root_server_from_iana(self, domain, server="whois.iana.org"):

        # get the record first
        data = SgwWhoisLogQuery.whois_request(self, domain, server, timeout=5)

        # try to find it from the record
        for line in [x.strip() for x in data.splitlines()]:
            match = re.match(r"refer:\s*([^\s]+)", line)
            if match is None:
                continue
            else:
                return match.group(1)

        # case where no result was found
        try:
            tld = domain.split(".")[-1]
            result = self.env["sgw.whois.tld"].search([("tld", "=", tld)]).whois_server
            return result
        except (ValueError, KeyError):
            return server

        # or then raise error if nothing worked
        # error_string = "No root whois found for " + str(domain)
        # raise sgw_shared.WhoisException(error_string)

    def get_whois_raw(
        self,
        domain,
        server=None,
        rfc3490=True,
        never_cut=False,
        with_server_list=False,
        server_list=None,
        whois_timeout=5,
    ):

        """Gets the raw data for the domain"""

        new_list = []

        server_list = server_list or []
        # Sometimes IANA simply won't give us the right root WHOIS server

        if rfc3490:
            domain = encode(domain, "idna").decode("ascii")

        if server is None:
            target_server = SgwWhoisLogQuery.get_root_server_from_db(self, domain)
        # elif "." + domain.split(".")[-1] in cc_tld:
        #     target_server = self.get_root_server(self,domain)
        else:
            target_server = server

        # deal with japanese case
        if target_server == "whois.jprs.jp":
            request_domain = "%s/e" % domain  # Suppress Japanese output

        # deal with germany case
        elif domain.endswith(".de") and (
            target_server == "whois.denic.de" or target_server == "de.whois-servers.net"
        ):
            request_domain = "-T dn,ace %s" % domain  # regional specific stuff

        # deal with verisign
        elif target_server == "whois.verisign-grs.com":
            request_domain = "=%s" % domain  # Avoid partial matches

        # all other cases
        else:
            request_domain = domain

        # decide on the
        response = SgwWhoisLogQuery.whois_request(
            self, request_domain, target_server, timeout=whois_timeout
        )

        # gives the whole raw data in return
        if never_cut:
            new_list = [response]
        # deal with verisign separately
        if target_server == "whois.verisign-grs.com":
            for record in response.split("\n\n"):
                if re.search("Domain Name: %s\n" % domain.upper(), record):
                    response = record
                    break

        if never_cut is False:
            new_list = [response]

        server_list.append(target_server)

        for line in [x.strip() for x in response.splitlines()]:
            match = re.match(
                r"""(refer|whois server|referral url|whois server|
                registrar whois):\s*([^\s]+\.[^\s]+)""",
                line,
                re.IGNORECASE,
            )
            if match is not None:
                referal_server = match.group(2)
                if (
                    referal_server != server and "://" not in referal_server
                ):  # We want to ignore anything non-WHOIS (eg. HTTP) for now.
                    # Referal to another WHOIS server...
                    return SgwWhoisLogQuery.get_whois_raw(
                        self,
                        domain,
                        referal_server,
                        new_list,
                        server_list=server_list,
                        with_server_list=with_server_list,
                    )
        if with_server_list:
            return (new_list, server_list)
        else:
            return new_list

    def whois_request(self, domain, server, port=43, timeout=None):
        """Makes the query for domain to WHOIS server and return the result
        in decoded ascii text, ready to read.

        Args:
            domain ([string]): [description]
            server ([string]): [description]
            port (int, optional): [description]. Defaults to 43.
            timeout ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((server, port))
            sock.send(("%s\r\n" % domain).encode("utf-8"))
            buff = b""
            while True:
                data = sock.recv(1024)
                if len(data) == 0:
                    break
                buff += data
            return buff.decode("latin-1")
        except Exception as e:
            return "Whois Error: (%s) " % e
