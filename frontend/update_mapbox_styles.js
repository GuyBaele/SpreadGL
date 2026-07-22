const fs = require('fs');
const content = fs.readFileSync('/Users/u0150975/Downloads/SpreadGL/frontend/src/app.js', 'utf8');

const newContent = content.replace(
  /import \{ DEFAULT_LAYER_GROUPS, DEFAULT_MAP_STYLES, DEFAULT_MAPLIBRE_STYLES \} from '@kepler.gl\/constants';/,
  `import { DEFAULT_LAYER_GROUPS, DEFAULT_MAP_STYLES, DEFAULT_MAPLIBRE_STYLES, DEFAULT_MAPBOX_STYLES, DEFAULT_MAPBOX_SATELITE_STYLES } from '@kepler.gl/constants';`
).replace(
  /const mapboxStyles = userMapboxToken \? DEFAULT_MAP_STYLES : \[\];/,
  `const mapboxStyles = userMapboxToken ? [...DEFAULT_MAPBOX_STYLES, ...DEFAULT_MAPBOX_SATELITE_STYLES] : [];`
);

fs.writeFileSync('/Users/u0150975/Downloads/SpreadGL/frontend/src/app.js', newContent);
