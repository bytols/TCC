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

  function face(skin) {
    return `<circle cx="100" cy="94" r="46" fill="${skin}"/>`;
  }

  function hairBack(style, hair) {
    // Desenhado ANTES dos ombros: cabelo comprido cai por trás do corpo.
    if (style === "liso_longo") return `<rect x="46" y="58" width="108" height="118" rx="52" fill="${hair}"/>`;
    return "";
  }

  function hairFront(style, hair) {
    const cap = `<path d="M52,94 A48,48 0 0 1 148,94 Q126,74 100,74 Q74,74 52,94 Z" fill="${hair}"/>`;
    if (style === "careca") return "";
    if (style === "liso_curto" || style === "liso_longo") return cap;
    if (style === "coque") return cap + `<circle cx="100" cy="40" r="15" fill="${hair}"/>`;
    if (style === "cacheado") {
      const bumps = [[58, 82, 15], [70, 56, 17], [96, 44, 18], [124, 46, 18], [142, 60, 16], [146, 84, 14]]
        .map(([cx, cy, r]) => `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${hair}"/>`).join("");
      return cap + bumps;
    }
    if (style === "moicano") return `<path d="M86,50 Q100,22 114,50 L108,82 Q100,88 92,82 Z" fill="${hair}"/>`;
    return cap;
  }

  function accessory(acc) {
    if (acc === "oculos")
      return '<g><rect x="72" y="88" width="22" height="17" rx="8" fill="rgba(255,255,255,0.18)" stroke="#222" stroke-width="3"/>'
           + '<rect x="106" y="88" width="22" height="17" rx="8" fill="rgba(255,255,255,0.18)" stroke="#222" stroke-width="3"/>'
           + '<line x1="94" y1="96" x2="106" y2="96" stroke="#222" stroke-width="3"/></g>';
    if (acc === "bone")
      return '<path d="M50,86 Q50,38 100,38 Q150,38 150,86 Z" fill="#C0392B"/>'
           + '<rect x="48" y="78" width="104" height="15" rx="7.5" fill="#A93226"/>'
           + '<circle cx="100" cy="34" r="9" fill="#F2F2F2"/>';
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
    // Chapéu e gorro cobrem a cabeça — escondem o cabelo para não conflitar.
    const hideHair = c.acessorio === "chapeu" || c.acessorio === "bone";
    const hairBackSvg = hideHair ? "" : hairBack(c.cabelo, hair);
    const hairFrontSvg = hideHair ? "" : hairFront(c.cabelo, hair);
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">'
      + '<defs><clipPath id="c"><circle cx="100" cy="100" r="100"/></clipPath></defs>'
      + `<circle cx="100" cy="100" r="100" fill="${bg}"/>`
      + '<g clip-path="url(#c)">'
      + hairBackSvg
      + `<ellipse cx="100" cy="200" rx="72" ry="56" fill="${SHOULDER}"/>`
      + face(skin)
      + `<ellipse cx="57" cy="98" rx="8" ry="12" fill="${skin}"/><ellipse cx="143" cy="98" rx="8" ry="12" fill="${skin}"/>`
      + hairFrontSvg
      + '<ellipse cx="84" cy="96" rx="5.5" ry="6.5" fill="#1A1A1A"/><ellipse cx="116" cy="96" rx="5.5" ry="6.5" fill="#1A1A1A"/>'
      + '<path d="M86,118 Q100,130 114,118" fill="none" stroke="#1A1A1A" stroke-width="3.5" stroke-linecap="round"/>'
      + accessory(c.acessorio)
      + '</g></svg>';
  };
})();
