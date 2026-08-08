/**
 * Embeddable Lead-Capture Widget Loader
 *
 * Usage (one line, added to any website):
 * <script src="https://your-backend.com/widget.js" data-widget-key="PUBLIC_KEY" async></script>
 *
 * This script:
 *  1. Reads its own <script> tag to find the widget's public key and API base URL.
 *  2. Fetches the widget's configuration from the backend.
 *  3. Renders a form (or popup) based on that configuration.
 *  4. Submits form data to the public submission endpoint, including a hidden
 *     honeypot field for spam protection.
 */
(function () {
  "use strict";

  function getCurrentScript() {
    // document.currentScript works in modern browsers; fallback for older ones.
    if (document.currentScript) return document.currentScript;
    var scripts = document.getElementsByTagName("script");
    for (var i = scripts.length - 1; i >= 0; i--) {
      if (scripts[i].src && scripts[i].src.indexOf("widget.js") !== -1) {
        return scripts[i];
      }
    }
    return null;
  }

  var thisScript = getCurrentScript();
  if (!thisScript) {
    console.error("[LeadWidget] Could not locate widget script tag.");
    return;
  }

  var widgetKey = thisScript.getAttribute("data-widget-key");
  if (!widgetKey) {
    console.error("[LeadWidget] Missing data-widget-key attribute.");
    return;
  }

  // Derive API base URL from the script's own src, so this works on any deployment.
  var scriptUrl = new URL(thisScript.src);
  var apiBase = scriptUrl.origin;

  var CONFIG_URL = apiBase + "/api/public/widgets/" + widgetKey + "/config";
  var SUBMIT_URL = apiBase + "/api/public/widgets/" + widgetKey + "/submit";

  var FIELD_LABELS = {
    name: "Name",
    email: "Email",
    phone: "Phone",
    message: "Message",
    company: "Company"
  };

  function injectStyles(primaryColor) {
    var style = document.createElement("style");
    style.textContent =
      ".lw-widget{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;" +
      "max-width:360px;border:1px solid #e5e7eb;border-radius:12px;padding:20px;" +
      "box-shadow:0 4px 14px rgba(0,0,0,0.08);background:#fff;box-sizing:border-box;}" +
      ".lw-widget *{box-sizing:border-box;}" +
      ".lw-title{font-size:18px;font-weight:600;margin:0 0 4px 0;color:#111827;}" +
      ".lw-desc{font-size:13px;color:#6b7280;margin:0 0 14px 0;}" +
      ".lw-field{margin-bottom:10px;}" +
      ".lw-field label{display:block;font-size:12px;color:#374151;margin-bottom:4px;}" +
      ".lw-field input,.lw-field textarea{width:100%;padding:8px 10px;border:1px solid #d1d5db;" +
      "border-radius:6px;font-size:14px;}" +
      ".lw-field textarea{min-height:70px;resize:vertical;}" +
      ".lw-btn{width:100%;padding:10px;border:none;border-radius:6px;color:#fff;" +
      "font-size:14px;font-weight:600;cursor:pointer;margin-top:4px;background:" + primaryColor + ";}" +
      ".lw-btn:disabled{opacity:0.6;cursor:not-allowed;}" +
      ".lw-msg{font-size:13px;margin-top:10px;text-align:center;}" +
      ".lw-msg.success{color:#059669;}" +
      ".lw-msg.error{color:#dc2626;}" +
      // Honeypot: hidden from real users via off-screen positioning, not display:none
      // (some bots skip fields that are display:none, but still fill offscreen ones).
      ".lw-honeypot{position:absolute;left:-9999px;top:-9999px;opacity:0;height:0;width:0;}";
    document.head.appendChild(style);
  }

  function buildForm(config, container) {
    var wrapper = document.createElement("div");
    wrapper.className = "lw-widget";

    var title = document.createElement("p");
    title.className = "lw-title";
    title.textContent = config.title;
    wrapper.appendChild(title);

    if (config.description) {
      var desc = document.createElement("p");
      desc.className = "lw-desc";
      desc.textContent = config.description;
      wrapper.appendChild(desc);
    }

    var form = document.createElement("form");

    config.fields.forEach(function (fieldName) {
      var fieldWrap = document.createElement("div");
      fieldWrap.className = "lw-field";

      var label = document.createElement("label");
      label.textContent = FIELD_LABELS[fieldName] || fieldName;
      label.setAttribute("for", "lw-" + fieldName);
      fieldWrap.appendChild(label);

      var input;
      if (fieldName === "message") {
        input = document.createElement("textarea");
      } else {
        input = document.createElement("input");
        input.type = fieldName === "email" ? "email" : "text";
      }
      input.id = "lw-" + fieldName;
      input.name = fieldName;
      input.required = true;
      fieldWrap.appendChild(input);

      form.appendChild(fieldWrap);
    });

    // Honeypot field — real users never see or fill this.
    var honeypotWrap = document.createElement("div");
    honeypotWrap.className = "lw-honeypot";
    var honeypotLabel = document.createElement("label");
    honeypotLabel.setAttribute("for", "lw-website");
    honeypotLabel.textContent = "Leave this field empty";
    var honeypotInput = document.createElement("input");
    honeypotInput.type = "text";
    honeypotInput.id = "lw-website";
    honeypotInput.name = "website";
    honeypotInput.tabIndex = -1;
    honeypotInput.autocomplete = "off";
    honeypotWrap.appendChild(honeypotLabel);
    honeypotWrap.appendChild(honeypotInput);
    form.appendChild(honeypotWrap);

    var submitBtn = document.createElement("button");
    submitBtn.type = "submit";
    submitBtn.className = "lw-btn";
    submitBtn.textContent = config.button_text;
    form.appendChild(submitBtn);

    var msg = document.createElement("div");
    msg.className = "lw-msg";
    form.appendChild(msg);

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      submitBtn.disabled = true;
      msg.textContent = "";
      msg.className = "lw-msg";

      var data = {};
      config.fields.forEach(function (fieldName) {
        data[fieldName] = document.getElementById("lw-" + fieldName).value;
      });

      fetch(SUBMIT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data: data,
          website: honeypotInput.value // honeypot value, should be empty
        })
      })
        .then(function (res) {
          return res.json().then(function (body) {
            return { ok: res.ok, body: body };
          });
        })
        .then(function (result) {
          submitBtn.disabled = false;
          if (result.ok && result.body.success) {
            msg.textContent = result.body.message || "Thank you!";
            msg.className = "lw-msg success";
            form.reset();
          } else {
            msg.textContent = (result.body && result.body.detail) || "Something went wrong.";
            msg.className = "lw-msg error";
          }
        })
        .catch(function () {
          submitBtn.disabled = false;
          msg.textContent = "Network error. Please try again.";
          msg.className = "lw-msg error";
        });
    });

    wrapper.appendChild(form);
    container.appendChild(wrapper);
  }

  function mount(config) {
    if (!config.is_active) {
      console.warn("[LeadWidget] Widget is inactive.");
      return;
    }
    injectStyles(config.primary_color || "#4f46e5");

    var container = document.createElement("div");
    container.id = "lw-container-" + widgetKey;

    // Insert right after the script tag's position in the DOM.
    thisScript.parentNode.insertBefore(container, thisScript.nextSibling);

    buildForm(config, container);
  }

  fetch(CONFIG_URL)
    .then(function (res) {
      if (!res.ok) throw new Error("Failed to load widget config");
      return res.json();
    })
    .then(mount)
    .catch(function (err) {
      console.error("[LeadWidget] Failed to initialize widget:", err);
    });
})();
