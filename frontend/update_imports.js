const fs = require('fs');
const content = fs.readFileSync('/Users/u0150975/Downloads/SpreadGL/frontend/src/app.js', 'utf8');

const newContent = content.replace(
  /import \{ DEFAULT_LAYER_GROUPS, DEFAULT_MAP_STYLES \} from '@kepler.gl\/constants';/,
  `import { DEFAULT_LAYER_GROUPS, DEFAULT_MAP_STYLES, DEFAULT_MAPLIBRE_STYLES } from '@kepler.gl/constants';`
);

fs.writeFileSync('/Users/u0150975/Downloads/SpreadGL/frontend/src/app.js', newContent);
