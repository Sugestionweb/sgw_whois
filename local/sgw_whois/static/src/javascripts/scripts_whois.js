odoo.define("sgw_whois.tools", function(require) {
  "use strict";
  require("web.dom_ready");
  //  Var ajax = require("web.ajax");
  //  var core = require("web.core");
  //  var _t = core._t;
  // Var core = require("web.core");
  const ByID = function(elementId) { 
    return document.getElementById(elementId); 
  }; 
  
  ByID("csrf_token").value = odoo.csrf_token;

  // document.getElementById("csrf_token").value = odoo.csrf_token;

  
  function render(datos, tld, domain_name) {
    const domain = domain_name + "." + tld;
    ByID("tabla_result").style.visibility = "visible";
    ByID("loading_table").style.visibility = "hidden";
    ByID("img_resultado_whois_" + tld).innerHTML = datos;
    if (datos.indexOf("text-danger") !== -1) {
      ByID("link_buy_" + tld).innerHTML = "Not available";
      const to_stroke = document.getElementById("price_" + tld).innerHTML;
      const stroked = "<s>" + to_stroke + "</s>";
      ByID("price_" + tld).innerHTML = stroked;

      const Button_Whois = document.createElement("button");
      Button_Whois.type = "button";
      Button_Whois.className = "btn btn-info btn-sm";
      Button_Whois.setAttribute("data-toggle", "modal");
      Button_Whois.setAttribute("data-target", "#myModal");
      Button_Whois.textContent = "Whois";
      Button_Whois.addEventListener("click", function() {
        ByID("modal_domain_title").innerHTML = domain;
        ByID("whois_raw").innerHTML = "...Consultando...";
        $.ajax({
          type: "POST",
          global: false,
          dataType: "html",
          url: "/get_whois_raw",
          data: {domain: domain, csrf_token: odoo.csrf_token},
          success: function(data) {
            ByID("whois_raw").innerHTML = data;
          },
          error: function(jqxhr, status, exception) {
            // Alert("Exception:", exception);
            ByID("whois_raw").innerHTML = exception;
          },
        });
      });
      ByID("button_whois_" + tld).appendChild(Button_Whois);
    }
  }
  function whois(domain_name, tld) {
    $.ajax({
      type: "POST",
      global: false,
      dataType: "html",
      url: "/get_status",
      data: {
        domain: domain_name,
        tld: tld,
        csrf_token: odoo.csrf_token,
      },
      success: function(data) {
        render(data, tld, domain_name);
      },
    });
  }
  function getStatus2(domain_name) {
    ByID("loading_table").style.visibility = "visible";
    function callback(response) {
      const obj = JSON.parse(response);
      for (var k in obj) {
        whois(domain_name, obj[k]);
      }
    }
    $.ajax({
      type: "POST",
      global: false,
      dataType: "html",
      url: "/get_tlds_exts",
      data: {csrf_token: odoo.csrf_token},
      success: function(data) {
        callback(data);
      },
    });
  }

  if (window.location.pathname === "/whois") {
    const value_domain = ByID("domain").value;
    if (value_domain !== "") {
      getStatus2(value_domain);
    }
  }
});
