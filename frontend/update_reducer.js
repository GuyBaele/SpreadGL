const fs = require('fs');
const content = fs.readFileSync('/Users/u0150975/Downloads/SpreadGL/frontend/src/reducers/index.js', 'utf8');

const newContent = content.replace(
  /if \(action\.type === 'CLEANUP_TIANDITU'\) \{[\s\S]*?return nextState;\n  \}/,
  `if (action.type === 'CLEANUP_TIANDITU') {
    const nextState = { ...state };
    if (nextState.keplerGl && nextState.keplerGl.map && nextState.keplerGl.map.mapStyle) {
      const mapStyle = { ...nextState.keplerGl.map.mapStyle };
      const mapStyles = { ...mapStyle.mapStyles };
      delete mapStyles['tianditu_satellite_cn'];
      delete mapStyles['tianditu_vector_cn'];
      delete mapStyles['tianditu_terrain_cn'];
      mapStyle.mapStyles = mapStyles;
      nextState.keplerGl = {
        ...nextState.keplerGl,
        map: {
          ...nextState.keplerGl.map,
          mapStyle: mapStyle
        }
      };
    }
    return nextState;
  }`
).replace(
  /if \(action\.type === 'CLEANUP_MAPBOX_STYLES'\) \{[\s\S]*?return nextState;\n  \}/,
  `if (action.type === 'CLEANUP_MAPBOX_STYLES') {
    const nextState = { ...state };
    if (nextState.keplerGl && nextState.keplerGl.map && nextState.keplerGl.map.mapStyle) {
      const mapStyle = { ...nextState.keplerGl.map.mapStyle };
      const mapStyles = { ...mapStyle.mapStyles };
      const mapboxStyleIds = ['dark', 'light', 'muted', 'muted_night', 'satellite'];
      mapboxStyleIds.forEach(id => {
        delete mapStyles[id];
      });
      mapStyle.mapStyles = mapStyles;
      nextState.keplerGl = {
        ...nextState.keplerGl,
        map: {
          ...nextState.keplerGl.map,
          mapStyle: mapStyle
        }
      };
    }
    return nextState;
  }`
).replace(
  /if \(action\.type === 'SET_MAP_STYLES'\) \{[\s\S]*?return nextState;\n  \}/,
  ``
);

fs.writeFileSync('/Users/u0150975/Downloads/SpreadGL/frontend/src/reducers/index.js', newContent);
