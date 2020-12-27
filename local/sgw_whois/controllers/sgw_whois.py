# -*- coding: utf-8 -*-

# Instalar este módulo python
## sudo pip install git+https://github.com/botlabio/pywhois.git
#
# Esto instalará el módulo en la carpeta "/usr/local/lib/python2.7/dist-packages/pywhois/"
# una vez instalado comprobar que funciona ejecutando python e introduciendo:
#    import pywhois
    
#  Si da algun error relacionado con los imports de los ficheros parse.py y net.py 
# modificamos esos ficheros para que hagan import net import en lugar de from . import net (para todos los errores)

# Instalar zeep --> para consultas en Arsys 
# sudo pip3 install zeep

import pywhois

import json
import datetime

from odoo import http
from zeep import Client, Settings
from odoo.http import Controller, Response, request, route
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.exceptions import ValidationError
from odoo.addons.website.controllers.main import Website
from odoo.addons.sale.controllers.product_configurator import ProductConfiguratorController
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression

arsys_url = 'https://webservice.nicline.com/WebServices/ws_apinl.php?wsdl' 
arsys_usr = ""
arsys_pass = "" 


class WhoisController(Website):

    def _get_tlds_exts(self):
        
        tlds_exts = []
        tlds_ids = self._get_tlds_ids()

        for p in tlds_ids:
            
            tlds_exts += p.list_tlds.split(",")
        return tlds_exts
    
    def _get_tlds_ids(self):
        
        app_obj = request.env['product.template'].sudo()
        tlds_ids = app_obj.search([('is_tld','!=', False)])
  
        return tlds_ids
   
    @http.route(['/get_tlds_exts'], auth='public',type='http', website=True)
    def get_tlds_exts(self):
        results = self._get_tlds_exts()
        return json.dumps(results)

    def chk_domain_name(self, domain=None, tld=None):
        result = ''
        whois_txt = ""
        if domain != None and tld !=None :
            if tld != 'es':
                try:
                    name = domain + "." + tld
                    w = pywhois.whois(name) 
                    whois_txt = w.get("raw")[0]
                    
                    if "status" in w:
                        if 'available' in w.get('status')[0].lower():   
                            result ="Free"
                        else:
                            result = 'Taken'
                            
                    else:
                        # Puede ser un dominio -eu el cual no tiene status
                        if tld == 'eu':
                            if "raw" in w:
                                if w.get('raw')[0].lower().__contains__('status: available'):
                                    result="Free"
                                else:
                                    result = "Taken"
                                
                        else:
                            result = 'Free'
                except:
                    result = 'Error'
            # los dominios .es se consultan en Arsys por SOAP
            elif tld == 'es': 
                #settings = Settings(strict=False, xml_huge_tree=True)
                client = Client(arsys_url)
                response = client.service.checkDomain({'sld': domain,
                                                       'tld':tld})
                whois_txt = response
                if response.lower().__contains__('<es>0</es>'):
                    result="Taken"
                elif response.lower().__contains__('<es>1</es>'):
                    result ="Free"
                elif response.lower().__contains__('<es>2</es>'):
                    result ="Taken"
                elif response.lower().__contains__('<es>3</es>'):
                    result ="Free"
        
            # log de la consulta
            r = False
            if result=='Free':
                r = True

            obj_log = request.env['sgw.whoisquery'].sudo()
            obj_log .create({
                'sld': domain,
                'tld': tld,
                'free': r,
                'whois_raw': whois_txt
            })
        
        return result
                 
    @http.route(['/get_status'], auth='public',type='http', website=True,csrf=False)
    def get_status(self,domain,tld):
        # llamando a esta funcion por javascript nos devuelve una imagen con 
        # el resultado
        #
        
        result = '<img style="float:left;" src="/sgw_theme/static/images/whois/delete.png" /> <span style ="margin-left:10px;" class="text-warning">No disponible</span>'
        status = self.chk_domain_name(domain, tld)
        if status == "Free":
            result = '<img style="float:left;" src="/sgw_theme/static/images/whois/accept.png" /><span style ="margin-left:10px;" class="text-success">Disponible</span> '
        if status == "Error":
            result = '<img style="float:left;" src="/sgw_theme/static/images/whois/delete.png" /><span style ="margin-left:10px;" class="text-warning">Error</span> '

#         else:
#             txt_alt = status[1][0].replace("'","")
#             txt_alt = status[1][0].replace('"',"")
#             
#             result = "<img alt='" + txt_alt + "'" + ' style="float:left;" src="/sgw_theme/static/images/whois/delete.png" >'
                
        return Response(result,content_type='text/html;charset=utf-8')
    
    @http.route('/whois', auth='public',website=True)
    def whoisdomain(self, domain=None, **kwargs):
        results = {} #tmp 
        values = {} # values to return
        validated_domain = ''
        domain = None
        
        obj_form = http.request.httprequest.form
        if 'domain' in obj_form :
            domain = obj_form['domain']
 
        if domain != None:
            if domain.__contains__('.'):
                domain = domain.split(".")[0]
            tlds_ids = self._get_tlds_ids()
                         
            for p in tlds_ids:
                tlds_exts = p.list_tlds.split(",")
                for i in tlds_exts:
                    results.update({i:[p,'placeholder1','placeholder2']}) 

            # validation of syntax for domain
            valid = ('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')
            validated_domain = domain
            for c in list(domain):
                if c not in valid:
                    validated_domain = validated_domain.replace(c, '')
            
        values = {
            'domain':validated_domain,
            'results':results,
            }        
                       
        return http.request.render('sgw_theme.whois_check',values)
    
   
    def check_domain(self, domain=None, tld=None,p=None):
        result = ''
        whois_txt = ""
        if domain != None and tld !=None and p !=None :
            try:
                name = domain + "." + tld
                w = whois.whois(name,True)
                whois_txt = w.text
                result = 'Taken'
            except:
                result = 'Free'
        
        return result, whois_txt,p
    

    @http.route(['/get_whois_raw'], auth='public', type='http', website=True,csrf=False)
    def get_whois_raw(self, domain=None, **kwargs):
        result = ""
        try:
            name = domain 
            w = pywhois.whois(name) 
            result = w.get("raw")[0].replace("\n", "<br/>")
        except:
            result = 'Error'
                
        return Response(result,content_type='text/html;charset=utf-8')
