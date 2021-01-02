odoo.define("sgw_whois.tools", function(require) {
  "use strict";
  require("web.dom_ready");
  //  Var ajax = require("web.ajax");
  //  var core = require("web.core");
  //  var _t = core._t;
  // Var core = require("web.core");
  document.getElementById("csrf_token").value = odoo.csrf_token;
  function render(datos, tld, domain_name) {
    const domain = domain_name + "." + tld;
    document.getElementById("tabla_result").style.visibility = "visible";
    document.getElementById("loading_table").style.visibility = "hidden";
    document.getElementById("img_resultado_whois_" + tld).innerHTML = datos;
    if (datos.indexOf("text-danger") !== -1) {
      document.getElementById("link_buy_" + tld).innerHTML = "Not available";
      const to_stroke = document.getElementById("price_" + tld).innerHTML;
      const stroked = "<s>" + to_stroke + "</s>";
      document.getElementById("price_" + tld).innerHTML = stroked;

      const button2 = document.createElement("button");
      button2.type = "button";
      button2.className = "btn btn-info btn-sm";
      button2.setAttribute("data-toggle", "modal");
      button2.setAttribute("data-target", "#myModal");
      button2.textContent = "Whois";
      button2.addEventListener("click", function() {
        document.getElementById("modal_domain_title").innerHTML = domain;
        document.getElementById("whois_raw").innerHTML = "...Consultando...";
        $.ajax({
          type: "POST",
          global: false,
          dataType: "html",
          url: "/get_whois_raw",
          data: {domain: domain, csrf_token: odoo.csrf_token},
          success: function(data) {
            document.getElementById("whois_raw").innerHTML = data;
          },
          error: function(jqxhr, status, exception) {
            // Alert("Exception:", exception);
            document.getElementById("whois_raw").innerHTML = exception;
          },
        });
      });
      document.getElementById("button_whois_" + tld).appendChild(button2);
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
    document.getElementById("loading_table").style.visibility = "visible";
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
    const value_domain = document.getElementById("domain").value;
    if (value_domain !== "") {
      getStatus2(value_domain);
    }
  }
});
