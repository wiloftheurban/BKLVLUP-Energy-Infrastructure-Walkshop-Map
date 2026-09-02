// Copy to config.js and fill in. config.js is gitignored — never commit a real token.
// Use a URL-restricted public token (pk.), scoped to your deploy domain + localhost.
window.TOUR_CONFIG = {
  MAPBOX_TOKEN: "pk.REPLACE_ME",

  // Custom Mapbox Studio styles, one per theme. Paste the Studio "Style URL"
  // (mapbox://styles/<user>/<styleid>) — index.html rewrites it to the HTTPS
  // Styles API URL, since MapLibre does not resolve the mapbox:// protocol.
  // Leave null to use the CARTO fallback for that theme.
  STYLE_URL_LIGHT: null,
  STYLE_URL_DARK: null,

  // Token-free CARTO fallbacks — also used if a Mapbox style fails to load.
  FALLBACK_STYLE_LIGHT: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
  FALLBACK_STYLE_DARK: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
};
