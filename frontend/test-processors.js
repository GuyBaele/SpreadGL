const { processGeojson, processCsvData } = require('@kepler.gl/processors');
const geojson = { type: "FeatureCollection", features: [{ type: "Feature", properties: { a: 1 }, geometry: { type: "Point", coordinates: [0, 0] } }] };
try {
  console.log("processGeojson result:", processGeojson(geojson));
} catch (e) {
  console.error("processGeojson error:", e);
}
