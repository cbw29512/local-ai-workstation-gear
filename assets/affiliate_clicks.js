(function () {
  "use strict";

  function safeText(value) {
    return String(value || "").trim();
  }

  function buildPayload(link) {
    return {
      event: "affiliate_click",
      merchant: safeText(link.dataset.merchant || "amazon"),
      slot: safeText(link.dataset.slot),
      slug: safeText(link.dataset.slug),
      asin: safeText(link.dataset.asin),
      product_name: safeText(link.dataset.productName),
      destination: safeText(link.href),
      clicked_at: new Date().toISOString()
    };
  }

  function storeLocalDebug(payload) {
    try {
      const key = "local_ai_gear_affiliate_click_debug";
      const oldValue = window.localStorage.getItem(key);
      const rows = oldValue ? JSON.parse(oldValue) : [];
      rows.push(payload);
      window.localStorage.setItem(key, JSON.stringify(rows.slice(-25)));
    } catch (error) {
      // Local debug storage is best-effort only.
    }
  }

  function sendAnalytics(payload) {
    storeLocalDebug(payload);

    if (typeof window.gtag === "function") {
      window.gtag("event", "affiliate_click", {
        merchant: payload.merchant,
        slot: payload.slot,
        slug: payload.slug,
        asin: payload.asin,
        product_name: payload.product_name
      });
    }
  }

  function onClick(event) {
    const link = event.target.closest("[data-affiliate-click='amazon']");
    if (!link) {
      return;
    }

    sendAnalytics(buildPayload(link));
  }

  document.addEventListener("click", onClick);
})();
