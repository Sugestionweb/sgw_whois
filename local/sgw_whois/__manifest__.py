# Created on 2020-12-27
# author: Javier https://www.sugestionweb.com
# email: javier@sugestionweb.com
# License: Odoo Proprietary License v1.0 (see LICENSE file)


{
    "name": "SGW Whois",
    'version': '1.0',
    "author": "Sugestionweb.com",
    "support": "sugestionweb@gmail.com",
    "category": "website",
    "website": "https://www.sugestionweb.com",
    "license": "OPL-1",
    "price": 100.00,
    "currency": "EUR",
    "summary": """
    With this module you can make domain name queries to Whois databases.
    """,
    "images": ["static/description/main_screenshot.png"],
    "depends": ["website_sale"],
    "data": [
        "data/sgw_whois_actions.xml",
        "data/sgw_whois_menu.xml",
        "security/ir.model.access.csv",
        "data/sgw.whois.server.csv",
        "data/sgw.whois.tld.csv",
        "security/sgw_groups_whois.xml",
        "views/sgw_whois_views.xml",
        "views/sgw_whois_web.xml",
        "views/product.xml",
        "views/assets.xml",
        "views/snippets.xml",
    ],
    "qweb": [],
    "demo": [],
    "test": [],
    "css": [],
    "js": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
