
function setcsrf() {
  console.log(odoo.csrf_token);
  document.getElementById("csrf_token").value = odoo.csrf_token;
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

/**
 * @param domain_name
 * @returns
 */
function getStatus2(domain_name) {
  element_loading = "loading_table";
  document.getElementById(element_loading).style.visibility = "visible";
  var tlds;
  function callback(response) {
    tlds = response;
    obj = JSON.parse(tlds);
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
      element_loading = "loading_table";
      document.getElementById(element_loading).style.visibility = "hidden";
      elementid = "img_resultado_whois_" + tld;
      document.getElementById(elementid).innerHTML = data;
      if (data.indexOf("text-danger") != -1) {
        elementid = "link_buy_" + tld;
        document.getElementById(elementid).innerHTML = "Not available";
        elementid = "price_" + tld;
        to_stroke = document.getElementById(elementid).innerHTML;
        stroked = "<s>" + to_stroke + "</s>";
        document.getElementById(elementid).innerHTML = stroked;

        /* Agregamos el botón para whois */
        elementid = "button_whois_" + tld;
        button =
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

function loadDynamicContentModal(modal) {
  var options = {
    modal: true,
    height: 300,
    width: 500,
  };

  $("#demo-modal").html("<img src='LoaderIcon.gif' />");
  $("#demo-modal")
    .load("get-dynamic-content.php?modal=" + modal)
    .dialog(options)
    .dialog("open");
}

function get_whois_modal(domain) {
  elementid = "modal_domain_title";
  document.getElementById(elementid).innerHTML = domain;

  elementid = "whois_raw";
  document.getElementById(elementid).innerHTML = "...Consultando...";

  function callback(response) {
    text_raw = response;
    elementid = "whois_raw";
    document.getElementById(elementid).innerHTML = text_raw;
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
