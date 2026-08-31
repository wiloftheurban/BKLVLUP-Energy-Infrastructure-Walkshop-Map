// Copy to config.js and fill in. config.js is gitignored — never commit a real token.
// Use a URL-restricted public token (pk.), scoped to your deploy domain + localhost.
window.TOUR_CONFIG = {
  MAPBOX_TOKEN: "pk.REPLACE_ME",
  STYLE_URL: "mapbox://styles/YOUR_ACCOUNT/YOUR_STYLE_ID",
  // Fallback if the Mapbox style is unavailable (offline, blocked, token issue).
  FALLBACK_STYLE: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
};
