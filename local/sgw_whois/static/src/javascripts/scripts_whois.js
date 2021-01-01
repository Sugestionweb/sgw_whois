odoo.define("sgw_whois.tools", function(require) {
  require("web.dom_ready");
  // Var core = require("web.core");
  document.getElementById("csrf_token").value = odoo.csrf_token;

  function getStatus2(domain_name) {
    document.getElementById("loading_table").style.visibility = "visible";
    
    function callback(response) {
      const obj = JSON.parse(response);
      for (var k in obj) {
        whois(domain_name, obj[k]);
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
      function render(data, tld, domain_name) {
        document.getElementById("tabla_result").style.visibility = "visible";
        document.getElementById("loading_table").style.visibility = "hidden";
        document.getElementById("img_resultado_whois_" + tld).innerHTML = data;
        if (data.indexOf("text-danger") != -1) {
          document.getElementById("link_buy_" + tld).innerHTML = "Not available";
          const to_stroke = document.getElementById("price_" + tld).innerHTML;
          const stroked = "<s>" + to_stroke + "</s>";
          document.getElementById("price_" + tld).innerHTML = stroked;

          /* Agregamos el botón para whois */
          elementid = "button_whois_" + tld;
          const button =
            '<button type="button" ' +
            'onclick="get_whois_modal(' +
            "'" +
            domain_name +
            "." +
            tld +
            "')" +
            '" ' +
            'class="btn btn-info btn-sm" data-toggle="modal" data-target="#myModal">Whois</button>';
          document.getElementById(elementid).innerHTML = button;
        }
      }
    }

    function escapeRegExp(text) {
      return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
    }

    function frmValidate() {
      var val = document.form_whois.domain.value;
      if (/^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9](?:[a-zA-Z]{2,})+$/.test(val)) {
        return true;
      }
      alert("Enter Valid Domain Name");
      val.name.focus();
      return false;
    }

    function setText(node, text) {
      const c = node.firstChild;
      if (c && !c.nextSibling && c.nodeType == 3) c.data = text;
      else node.textContent = text;
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

function get_whois_modal(domain) {
  document.getElementById("modal_domain_title").innerHTML = domain;
  document.getElementById("whois_raw").innerHTML = "...Consultando...";
  
  function callback(response) {
    document.getElementById("whois_raw").innerHTML = response;
  }

  $.ajax({
    type: "POST",
    global: false,
    dataType: "html",
    url: "/get_whois_raw",
    data: {domain: domain, csrf_token: odoo.csrf_token},
    success: function(data) {
      callback(data);
    },
  });
}
