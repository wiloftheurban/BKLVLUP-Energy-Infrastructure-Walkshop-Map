// Copy to config.js and fill in the token. config.js is gitignored.
// Use a URL-restricted PUBLIC token (pk.), scoped to:
//    localhost:*
//    wiloftheurban.github.io/*
// Never use the default/unrestricted token, and never commit an sk. token.

window.TOUR_CONFIG = {
  MAPBOX_TOKEN: "pk.REPLACE_ME",

  // LIGHT is the default theme — used by the web map AND the print basemap.
  STYLE_LIGHT: "mapbox://styles/wiljones/cmth7gjh500d201s04i6j0wa3",

  // Dark style — optional dark-mode toggle only. Build this last, or leave blank.
  STYLE_DARK: "",

  // Active style for the web map. Points at LIGHT.
  STYLE_URL: "mapbox://styles/wiljones/cmth7gjh500d201s04i6j0wa3",

  // Used if STYLE_URL fails to load (offline, blocked, bad token).
  FALLBACK_STYLE: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
};
