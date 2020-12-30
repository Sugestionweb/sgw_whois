# Created on 2020-12-27
# author: Javier https://www.sugestionweb.com
# email: javier@sugestionweb.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'SGW Whois',
    'version': '12.0.0.0.1',
    'author': 'Sugestionweb.com',
    'category': 'Productivity',
    'website': 'https://www.sugestionweb.com',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': """
    Query Whois Servers from website
    """,
    'description': """

    """,
    'images': ['static/description/banner.gif'],
    'depends': ['sale', 'website_sale'],
    'data': [
            'data/sgw_hosting_actions.xml',
            'data/sgw_hosting_menu.xml',
            'security/ir.model.access.csv',
            'security/sgw_groups_whois.xml',
            'views/sgw_hosting_views.xml',
            'views/sgw_hosting_whois_web.xml',
            'views/product.xml',
            'views/assets.xml',
            'views/snippets.xml',
            'views/sgw_portal_templates.xml'
            ],
    'qweb': [

    ],
    'demo': [],
    'test': [],
    'css': [],
    'js': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}