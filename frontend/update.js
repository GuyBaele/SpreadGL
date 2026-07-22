const fs = require('fs');
const content = fs.readFileSync('/Users/u0150975/Downloads/SpreadGL/frontend/src/app.js', 'utf8');

const newContent = content.replace(
  /setUserMapboxToken = \(token\) => \{[\s\S]*?setEnableTianditu = \(val\) => \{[\s\S]*?\};\n/g,
  `setUserMapboxToken = (token) => {
    try {
      window.localStorage.setItem('user_mapbox_token', token);
    } catch (e) {
      console.warn(e);
    }
    
    // Check if we need to fallback style before cleaning up Mapbox styles
    const { keplerGl } = this.props.demo || {};
    const mapStyleObj = keplerGl && keplerGl.map && keplerGl.map.mapStyle;
    if (!token && mapStyleObj) {
      const mapboxStyleIds = ['dark', 'light', 'muted', 'muted_night', 'satellite'];
      if (mapboxStyleIds.includes(mapStyleObj.styleType)) {
        this.props.dispatch(wrapTo('map', mapStyleChange('dark-matter')));
      }
    }

    this.setState({ userMapboxToken: token }, () => {
      this.props.dispatch(wrapTo('map', setUserMapboxAccessToken(token || null)));
      if (!token) {
        this.props.dispatch({ type: 'CLEANUP_MAPBOX_STYLES' });
      }
    });
  };

  setEnableTianditu = (val) => {
    // Check if we need to fallback style before cleaning up Tianditu styles
    const { keplerGl } = this.props.demo || {};
    const mapStyleObj = keplerGl && keplerGl.map && keplerGl.map.mapStyle;
    if (!val && mapStyleObj) {
      const tiandituStyleIds = ['tianditu_satellite_cn', 'tianditu_vector_cn', 'tianditu_terrain_cn'];
      if (tiandituStyleIds.includes(mapStyleObj.styleType)) {
        this.props.dispatch(wrapTo('map', mapStyleChange('dark-matter')));
      }
    }

    this.setState({ enableTianditu: val }, () => {
      if (!val) {
        this.props.dispatch({ type: 'CLEANUP_TIANDITU' });
      }
    });
  };
`
);

fs.writeFileSync('/Users/u0150975/Downloads/SpreadGL/frontend/src/app.js', newContent);
