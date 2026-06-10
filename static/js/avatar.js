/* ══════════════════════════════════════════════════
   RUÍDO — Avatar composto (preview ao vivo)
   ESPELHA a geometria de avatar.py. Mantenha os dois em sincronia.
   Requer window.CHAR_OPTIONS (injetado pelo template).
══════════════════════════════════════════════════ */
(function () {
  const SHOULDER = "#2E2A45";

  function color(cat, id, fallback) {
    const opts = (window.CHAR_OPTIONS || {})[cat] || [];
    const o = opts.find(x => x.id === id);
    return (o && o.color) || fallback;
  }

  function face(shape, skin) {
    if (shape === "redondo")    return `<circle cx="100" cy="94" r="46" fill="${skin}"/>`;
    if (shape === "quadrado")   return `<rect x="56" y="50" width="88" height="92" rx="24" fill="${skin}"/>`;
    if (shape === "triangular") return `<path d="M58,74 Q58,50 100,50 Q142,50 142,74 L116,130 Q100,146 84,130 Z" fill="${skin}"/>`;
    return `<ellipse cx="100" cy="94" rx="42" ry="50" fill="${skin}"/>`;
  }

  function hairBack(style, hair) {
    if (style === "liso_longo") return `<rect x="48" y="52" width="104" height="108" rx="46" fill="${hair}"/>`;
    if (style === "cacheado")   return `<rect x="50" y="50" width="100" height="96" rx="48" fill="${hair}"/>`;
    return "";
  }

  function hairFront(style, hair) {
    const cap = `<path d="M56,82 C56,42 144,42 144,82 C144,64 126,56 100,56 C74,56 56,64 56,82 Z" fill="${hair}"/>`;
    if (style === "careca") return "";
    if (style === "liso_curto" || style === "liso_longo") return cap;
    if (style === "coque") return cap + `<circle cx="100" cy="40" r="15" fill="${hair}"/>`;
    if (style === "cacheado") {
      return [[64, 60, 14], [84, 50, 16], [104, 48, 16], [124, 52, 15], [140, 62, 13]]
        .map(([cx, cy, r]) => `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${hair}"/>`).join("");
    }
    if (style === "moicano") return `<path d="M89,42 Q100,32 111,42 L105,90 Q100,96 95,90 Z" fill="${hair}"/>`;
    return cap;
  }

  function accessory(acc) {
    if (acc === "oculos")
      return '<g><rect x="72" y="88" width="22" height="17" rx="8" fill="rgba(255,255,255,0.18)" stroke="#222" stroke-width="3"/>'
           + '<rect x="106" y="88" width="22" height="17" rx="8" fill="rgba(255,255,255,0.18)" stroke="#222" stroke-width="3"/>'
           + '<line x1="94" y1="96" x2="106" y2="96" stroke="#222" stroke-width="3"/></g>';
    if (acc === "bone")
      return '<path d="M56,68 Q100,30 144,68 Q120,56 100,56 Q80,56 56,68 Z" fill="#C0392B"/>'
           + '<path d="M138,66 Q164,62 162,72 Q142,74 128,70 Z" fill="#922B1E"/>';
    if (acc === "chapeu")
      return '<ellipse cx="100" cy="58" rx="60" ry="12" fill="#1A1A1A"/>'
           + '<rect x="74" y="24" width="52" height="36" rx="6" fill="#1A1A1A"/>';
    if (acc === "brinco")
      return '<circle cx="143" cy="110" r="4.5" fill="#F4D03F"/>';
    if (acc === "headphone")
      return '<path d="M54,94 Q54,40 100,40 Q146,40 146,94" fill="none" stroke="#222" stroke-width="7"/>'
           + '<rect x="46" y="88" width="16" height="26" rx="7" fill="#222"/>'
           + '<rect x="138" y="88" width="16" height="26" rx="7" fill="#222"/>';
    return "";
  }

  window.buildAvatarSVG = function (c) {
    const skin = color("pele", c.pele, "#F1C27D");
    const hair = color("cor_cabelo", c.cor_cabelo, "#1A1A1A");
    const bg = color("fundo", c.fundo, "#6C3483");
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">'
      + '<defs><clipPath id="c"><circle cx="100" cy="100" r="100"/></clipPath></defs>'
      + `<circle cx="100" cy="100" r="100" fill="${bg}"/>`
      + '<g clip-path="url(#c)">'
      + `<ellipse cx="100" cy="200" rx="72" ry="56" fill="${SHOULDER}"/>`
      + hairBack(c.cabelo, hair)
      + face(c.rosto, skin)
      + `<ellipse cx="57" cy="98" rx="8" ry="12" fill="${skin}"/><ellipse cx="143" cy="98" rx="8" ry="12" fill="${skin}"/>`
      + hairFront(c.cabelo, hair)
      + '<ellipse cx="84" cy="96" rx="5.5" ry="6.5" fill="#1A1A1A"/><ellipse cx="116" cy="96" rx="5.5" ry="6.5" fill="#1A1A1A"/>'
      + '<path d="M86,118 Q100,130 114,118" fill="none" stroke="#1A1A1A" stroke-width="3.5" stroke-linecap="round"/>'
      + accessory(c.acessorio)
      + '</g></svg>';
  };
})();
