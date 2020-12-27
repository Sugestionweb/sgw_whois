# -*- coding: utf-8 -*-
from odoo import _, http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        is_admin = request.env.user.id <= 2
        sgw_service = request.env['sgw.service']
        service_count = sgw_service.sudo().search_count(
            [('partner_id', '=', partner.id)])
        if is_admin:
            service_count = sgw_service.sudo().search_count([('id', '>', 0)])
        values.update({
            'service_count': service_count
        })
        return values

    @http.route(['/my/services', '/my/services/page/<int:page>'], type='http',
                auth="user", website=True)
    def portal_my_services(self, page=1, date_begin=None, date_end=None,
                           sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        service = request.env['sgw.service'].sudo()
        is_admin = request.env.user.id <= 2

        domain = [
            ('partner_id', '=', [partner.id])
        ]

        if is_admin:
            domain = [
                ('id', '>', 0)
            ]

        # next_expiration_date is a calculated field and the order
        # is not working
        searchbar_sortings = {
            'date': {'label': _(
                'Próxima Renovación'), 'order': 'next_expiration_date asc'},
            'name': {'label': _(
                'Nombre'), 'order': 'name'},
            'id': {'label': _('ID#'), 'order': 'id'}
        }

        # default sortby order
        if not sortby:
            sortby = 'id'

        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sgw.service', domain)

        if date_begin and date_end:
            domain += [('next_expiration_date', '>', date_begin), (
                'next_expiration_date', '<=', date_end)]

        # count for pager
        service_count = service.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/services",
            url_args={'date_begin': date_begin,
                      'date_end': date_end,
                      'sortby': sortby},
            total=service_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        services = service.search(
            domain, order=sort_order,
            limit=self._items_per_page,
            offset=pager['offset'])
        request.session['my_services_history'] = services.ids[:100]

        values.update({
            'date': date_begin,
            'services': services.sudo(),
            'page_name': 'service',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/services',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return request.render("sgw_hosting.portal_my_listservices", values)

    @http.route(['/my/services/<int:id>'], type='http', auth="public",
                website=True)
    def portal_service_page(self, id, **kw):
        values = {}
        partner = request.env.user.partner_id
        is_admin = request.env.user.id <= 2

        sgw_service = request.env['sgw.service']

        domain = [('id', '=', id)]

        service = sgw_service.search(domain, limit=1)

        if (service.partner_id == partner) or is_admin:
            values = {
                'service': service.sudo(),
                'return_url': '/shop/payment/validate',
                'bootstrap_formatting': True,
                'partner_id': service.partner_id.id,
                'page_name': 'service'
            }

        return request.render('sgw_hosting.portal_service_template', values)

    @http.route(['/panel'], type='http', auth="public", website=True)
    def portal_panel_page(self, **kw):

        sgw_server = request.env['sgw.server']
        domain = [('control_panel_visible', '=', 'True')]
        servers = sgw_server.search(domain)
        values = {'servers': servers.sudo()}

        return request.render(
            'sgw_hosting.portal_panel_webmail_template', values)
