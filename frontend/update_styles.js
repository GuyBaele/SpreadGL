const fs = require('fs');
const content = fs.readFileSync('/Users/u0150975/Downloads/SpreadGL/frontend/src/app.js', 'utf8');

const newContent = content.replace(
  /const freeStyles = \[[\s\S]*?\];/,
  `import { DEFAULT_MAPLIBRE_STYLES } from '@kepler.gl/constants';
    const freeStyles = [
      ...DEFAULT_MAPLIBRE_STYLES,
      noBasemapStyle
    ];`
).replace(/import \{ DEFAULT_MAPLIBRE_STYLES \} from '@kepler\.gl\/constants';\n    const freeStyles/, 'const freeStyles'); // we must import at top

fs.writeFileSync('/Users/u0150975/Downloads/SpreadGL/frontend/src/app.js', newContent);
