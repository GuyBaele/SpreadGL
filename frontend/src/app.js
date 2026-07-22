// SPDX-License-Identifier: MIT
// Copyright contributors to the kepler.gl project

import React, { Component, useRef, useCallback } from 'react';
import AutoSizer from 'react-virtualized/dist/commonjs/AutoSizer';
import styled, { ThemeProvider } from 'styled-components';
import window from 'global/window';
import { connect, useDispatch } from 'react-redux';

import { theme } from '@kepler.gl/styles';
import Banner from './components/banner';
import Announcement, { FormLink } from './components/announcement';
import DataPipelineControl from './components/DataPipelineControl';
import { replaceLoadDataModal } from './factories/load-data-modal';
import { replaceMapControl } from './factories/map-control';
import { replacePanelHeader } from './factories/panel-header';
import { CLOUD_PROVIDERS_CONFIGURATION, DEFAULT_FEATURE_FLAGS } from './constants/default-settings';
import { messages } from './constants/localization';

import {
  loadRemoteMap,
  loadSampleConfigurations,
  onExportFileSuccess,
  onLoadCloudMapSuccess
} from './actions';

import { loadCloudMap, addDataToMap, addNotification, replaceDataInMap, loadMapStyles, wrapTo, mapStyleChange, toggleModal } from '@kepler.gl/actions';
import { CLOUD_PROVIDERS } from './cloud-providers';
import { DEFAULT_LAYER_GROUPS } from '@kepler.gl/constants';
import { injectComponents, FileUploadFactory } from '@kepler.gl/components';
import { processGeojson, processCsvData } from '@kepler.gl/processors';
import KeplerGlSchema from '@kepler.gl/schemas';

const SPREADGL_DEFAULT_CONFIG = {
  version: 'v1',
  config: {
    mapState: {
      latitude: 35.0,
      longitude: 105.0,
      zoom: 3.8
    },
    visState: {
      layers: [
        {
          id: 'dynamic_pathway_trip',
          type: 'trip',
          config: {
            dataId: 'dynamic_pathway',
            label: 'Dynamic Pathway',
            isVisible: true,
            columns: {
              geojson: '_geojson'
            },
            visConfig: {
              opacity: 0.8,
              thickness: 2.0,
              trailLength: 180
            }
          }
        },
        {
          id: 'hpd_polygons_geojson',
          type: 'geojson',
          config: {
            dataId: 'hpd_polygons',
            label: 'HPD Polygons',
            isVisible: true,
            columns: {
              geojson: '_geojson'
            },
            visConfig: {
              opacity: 0.2,
              filled: true,
              stroked: false,
              colorRange: {
                name: 'Colorblind Friendly',
                type: 'sequential',
                category: 'Custom',
                colors: ['#D6DEBF', '#95C590', '#58A690', '#49828A', '#415F79', '#383C65']
              }
            },
            visualChannels: {
              colorField: {
                name: 'hpd_level',
                type: 'integer'
              },
              colorScale: 'quantile'
            }
          }
        },
        {
          id: 'aggregated_migration_network_arc',
          type: 'arc',
          config: {
            dataId: 'aggregated_migration_network',
            label: 'Aggregated Migration Network',
            isVisible: true,
            color: [18, 147, 154],
            columns: {
              lat0: 'start_lat',
              lng0: 'start_lon',
              lat1: 'end_lat',
              lng1: 'end_lon'
            },
            visConfig: {
              targetColor: [224, 58, 62],
              opacity: 0.8,
              strokeWidthRange: [0, 10]
            },
            visualChannels: {
              sizeField: {
                name: 'jump_weight',
                type: 'integer'
              },
              sizeScale: 'linear'
            }
          }
        }
      ]
    }
  }
};

const CustomDropzoneContainer = styled.div`
  border: 2px dashed rgba(16, 107, 163, 0.4);
  background: #f8fafc;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;

  &:hover {
    border-color: #1e88e5;
    background: rgba(16, 107, 163, 0.04);
  }
`;

const CustomDropzoneText = styled.p`
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 600;
  color: #2D3748;
  font-family: 'Outfit', sans-serif;
`;

const CustomDropzoneSubtext = styled.span`
  font-size: 12px;
  color: #64748b;
  font-family: 'Inter', sans-serif;
`;

const CustomFileUpload = () => {
  const dispatch = useDispatch();
  const fileInputRef = useRef(null);

  const handleFile = useCallback((file) => {
    if (!file) return;
    const name = file.name.toLowerCase();

    if (name.endsWith('.tif') || name.endsWith('.tiff') || name.endsWith('.tree') || name.endsWith('.trees')) {
      alert('Please upload raw tree and raster files through the Setup tab pipeline, not directly to the map.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const fileContent = event.target.result;
        const dataId = file.name.replace(/\.[^/.]+$/, "");

        if (name.endsWith('.geojson') || name.endsWith('.json')) {
          const parsedJson = JSON.parse(fileContent);
          
          if (parsedJson.datasets && parsedJson.config) {
            // 1. Unpack the serialized Kepler map state
            const loadedMap = KeplerGlSchema.load(
              parsedJson.datasets,
              parsedJson.config
            );
            // 2. Dispatch the unpacked state
            dispatch(addDataToMap(loadedMap));
          } else {
            // It's a standard raw GeoJSON file.
            const processedData = processGeojson(parsedJson);
            dispatch(addDataToMap({
              datasets: [{ info: { id: dataId, label: file.name }, data: processedData }],
              options: { keepExistingConfig: true }
            }));
          }
        } else if (name.endsWith('.csv')) {
          const processedData = processCsvData(fileContent);
          dispatch(addDataToMap({
            datasets: [{
              info: {
                id: dataId,
                label: file.name
              },
              data: processedData
            }],
            options: {
              keepExistingConfig: true
            },
            config: SPREADGL_DEFAULT_CONFIG
          }));
        } else {
          alert('Unsupported file format. Please upload a .geojson, .json, or .csv file.');
          return;
        }

        // Close the modal
        dispatch(wrapTo('map', toggleModal(null)));
      } catch (err) {
        alert(`Failed to parse file: ${err.message}`);
      }
    };

    reader.onerror = () => {
      alert('Error reading file.');
    };

    reader.readAsText(file);
  }, [dispatch]);

  const onDragOver = useCallback((e) => {
    e.preventDefault();
  }, []);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, [handleFile]);

  const onInputChange = useCallback((e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  }, [handleFile]);

  return (
    <CustomDropzoneContainer 
      onClick={() => fileInputRef.current?.click()}
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      <input 
        type="file" 
        ref={fileInputRef} 
        style={{ display: 'none' }} 
        accept=".geojson,.json,.csv"
        onChange={onInputChange}
      />
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#106ba3" strokeWidth="2" style={{ marginBottom: '12px' }}>
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="17 8 12 3 7 8"></polyline>
        <line x1="12" y1="3" x2="12" y2="15"></line>
      </svg>
      <CustomDropzoneText>
        Drop spread.gl data (.geojson, .csv) or saved maps (.json) here, or click to upload.
      </CustomDropzoneText>
      <CustomDropzoneSubtext>
        File size limit: 250MB
      </CustomDropzoneSubtext>
    </CustomDropzoneContainer>
  );
};

const CustomFileUploadFactory = () => {
  return CustomFileUpload;
};
CustomFileUploadFactory.deps = FileUploadFactory.deps;

const KeplerGl = injectComponents([
  replaceLoadDataModal(),
  replaceMapControl(),
  replacePanelHeader(),
  [FileUploadFactory, CustomFileUploadFactory]
]);

// Sample data
/* eslint-disable no-unused-vars */
import sampleTripData, { testCsvData, sampleTripDataConfig } from './data/sample-trip-data';
import sampleGeojson from './data/sample-small-geojson';
import sampleGeojsonPoints from './data/sample-geojson-points';
import sampleGeojsonConfig from './data/sample-geojson-config';
import sampleH3Data, { config as h3MapConfig } from './data/sample-hex-id-csv';
import sampleS2Data, { config as s2MapConfig, dataId as s2DataId } from './data/sample-s2-data';
import sampleAnimateTrip, { animateTripDataId } from './data/sample-animate-trip-data';
import sampleIconCsv, { config as savedMapConfig } from './data/sample-icon-csv';
import sampleGpsData from './data/sample-gps-data';
/* eslint-enable no-unused-vars */

const BannerHeight = 48;
const BannerKey = `banner-${FormLink}`;
const keplerGlGetState = state => state.demo.keplerGl;

const GlobalStyle = styled.div`
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-weight: 400;
  font-size: 0.95rem;
  line-height: 1.6;

  *,
  *:before,
  *:after {
    -webkit-box-sizing: border-box;
    -moz-box-sizing: border-box;
    box-sizing: border-box;
  }

  ul {
    margin: 0;
    padding: 0;
  }

  li {
    margin: 0;
  }

  a {
    text-decoration: none;
    color: ${props => props.theme.labelColor};
  }
`;

/* BEAST palette:
  bg-darkest:  #001822  (near-black teal)
  bg-dark:     #00303A  (dark teal = --darker-color)
  bg-mid:      #3B6F84  (medium teal = --background-color)
  accent-gold: #CBB944  (amber highlight = --hilite-color)
  accent-blue: #68A3BB  (steel blue = --lighter-color)
  text-body:   #D6E8EE  (light teal-white)
  text-muted:  #8AAFBD  (muted blue-grey)
*/

const PageWrapper = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background: #ffffff;
  color: #2D3748;
  overflow: hidden;
  position: relative;
`;

const TopNavBar = styled.div`
  display: flex;
  background: linear-gradient(90deg, #0f4c81 0%, #1e88e5 100%);
  border-bottom: 2px solid #EDD96A;
  height: 52px;
  align-items: center;
  padding: 0 20px;
  z-index: 1001;
  flex-shrink: 0;
  box-shadow: 0 3px 20px rgba(15, 76, 129, 0.3);
`;

const NavTab = styled.div`
  padding: 0 24px;
  height: 100%;
  display: flex;
  align-items: center;
  color: ${props => props.$active ? '#EDD96A' : '#a3c8dc'};
  border-bottom: 2px solid ${props => props.$active ? '#EDD96A' : 'transparent'};
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.5px;
  transition: all 0.2s ease;
  user-select: none;
  font-family: 'Outfit', sans-serif;

  &:hover {
    color: #EDD96A;
  }

  @media (max-width: 600px) {
    padding: 0 12px;
    font-size: 13px;
  }
`;

const MainContentArea = styled.div`
  flex: 1;
  position: relative;
  width: 100%;
  height: calc(100% - 50px);
`;

const KeplerContainerWrapper = styled.div`
  position: absolute;
  left: ${props => props.$active ? 0 : '-9999px'};
  top: 0;
  width: 100%;
  height: 100%;
  visibility: ${props => props.$active ? 'visible' : 'hidden'};
  z-index: ${props => props.$active ? 1 : 0};
`;

const PipelineContainerWrapper = styled.div`
  position: absolute;
  left: ${props => props.$active ? 0 : '-9999px'};
  top: 0;
  width: 100%;
  height: 100%;
  visibility: ${props => props.$active ? 'visible' : 'hidden'};
  z-index: ${props => props.$active ? 2 : 0};
  overflow-y: auto;
  background: #ffffff;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 40px 20px;
  box-sizing: border-box;

  @media (max-width: 600px) {
    padding: 16px 8px;
  }
`;

const LogoWrapper = styled.div`
  margin-right: auto;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const LogoText = styled.span`
  font-weight: 800;
  font-size: 20px;
  letter-spacing: 1px;
  color: #ffffff;
  font-family: 'Outfit', sans-serif;

  @media (max-width: 480px) {
    font-size: 16px;
  }
`;

const LogoImage = styled.img`
  height: 28px;
  width: auto;
  object-fit: contain;
  margin-left: 8px;
`;


const LogoVersion = styled.span`
  font-size: 10px;
  color: #EDD96A;
  margin-left: 6px;
  padding: 2px 8px;
  border: 1px solid #EDD96A;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 1px;

  @media (max-width: 480px) {
    display: none;
  }
`;

const DropdownContainer = styled.div`
  position: absolute;
  top: 70px;
  right: 20px;
  z-index: 1000;
  background: rgba(0, 24, 34, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(203, 185, 68, 0.4);
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
  font-family: 'Outfit', sans-serif;
`;

const DropdownLabel = styled.span`
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: #CBB944;
  font-weight: 700;
`;

const StyledSelect = styled.select`
  background: rgba(0, 24, 34, 0.6);
  border: 1px solid rgba(203, 185, 68, 0.2);
  color: #ffffff;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s;
  &:hover, &:focus {
    border-color: #CBB944;
  }
`;

class App extends Component {
  state = {
    showBanner: false,
    width: window.innerWidth,
    height: window.innerHeight,
    activeTab: 'config',
    mapboxLimitExceeded: false,
    mapboxLoadsThisMonth: 0,
    userMapboxToken: '',
    enableTianditu: false,
    pipelineResults: null,
    selectedHpdLevel: '80'
  };

  componentDidMount() {
    // Mapbox load limit safeguard (50k/month limit)
    let limitExceeded = false;
    let count = 0;
    let savedMapboxToken = '';
    try {
      savedMapboxToken = window.localStorage.getItem('user_mapbox_token') || '';
      const currentMonth = new Date().toISOString().slice(0, 7); // e.g. "2026-06"
      const storedMonth = window.localStorage.getItem('mapbox_load_month');
      count = parseInt(window.localStorage.getItem('mapbox_load_count') || '0', 10);
      
      if (storedMonth !== currentMonth) {
        count = 0;
        window.localStorage.setItem('mapbox_load_month', currentMonth);
        window.localStorage.setItem('mapbox_load_count', '0');
      }

      limitExceeded = count >= 50000;
      
      if (!limitExceeded) {
        count += 1;
        window.localStorage.setItem('mapbox_load_count', count.toString());
      }
    } catch (e) {
      console.warn('LocalStorage is not available, skipping Mapbox monthly tracking safeguard.');
    }

    this.setState({
      mapboxLimitExceeded: limitExceeded,
      mapboxLoadsThisMonth: count,
      userMapboxToken: savedMapboxToken
    });

    // if we pass an id as part of the url
    // we try to fetch along map configurations
    const { params: { id, provider } = {}, location: { query = {} } = {} } = this.props;

    const cloudProvider = CLOUD_PROVIDERS.find(c => c.name === provider);
    if (cloudProvider) {
      this.props.dispatch(
        loadCloudMap({
          loadParams: query,
          provider: cloudProvider,
          onSuccess: onLoadCloudMapSuccess
        })
      );
      return;
    }

    // Load sample using its id
    if (id) {
      this.props.dispatch(loadSampleConfigurations(id));
    }

    // Load map using a custom
    if (query.mapUrl) {
      // TODO?: validate map url
      this.props.dispatch(loadRemoteMap({ dataUrl: query.mapUrl }));
    }

    // Suppress Kepler's native "Add Data" modal with a lifecycle timeout hack
    setTimeout(() => {
      this.props.dispatch(wrapTo('map', toggleModal(null)));
    }, 250);
  }

  _resetMapboxCounter = () => {
    if (window.confirm('Reset the Mapbox monthly load counter? (Useful if your billing cycle restarted)')) {
      try {
        const currentMonth = new Date().toISOString().slice(0, 7);
        window.localStorage.setItem('mapbox_load_month', currentMonth);
        window.localStorage.setItem('mapbox_load_count', '0');
        this.setState({
          mapboxLimitExceeded: false,
          mapboxLoadsThisMonth: 0
        });
      } catch (e) {
        console.error(e);
      }
    }
  };

  setUserMapboxToken = (token) => {
    try {
      window.localStorage.setItem('user_mapbox_token', token);
    } catch (e) {
      console.warn(e);
    }

    // Check if we need to fallback style before cleaning up Mapbox styles
    const { demo } = this.props;
    const keplerGl = demo && demo.keplerGl && demo.keplerGl.map;
    const currentStyle = keplerGl && keplerGl.mapStyle && keplerGl.mapStyle.styleType;

    // If Mapbox token is being removed, and current style is Mapbox-only, revert to carto_positron
    if (!token && currentStyle && ['dark', 'light', 'muted', 'muted_night', 'satellite'].includes(currentStyle)) {
      this.props.dispatch(wrapTo('map', mapStyleChange('carto_positron')));
    }

    this.setState({ userMapboxToken: token });
  };

  setEnableTianditu = (val) => {
    // Check if we need to fallback style before cleaning up Tianditu styles
    const { demo } = this.props;
    const keplerGl = demo && demo.keplerGl && demo.keplerGl.map;
    const currentStyle = keplerGl && keplerGl.mapStyle && keplerGl.mapStyle.styleType;

    if (!val && currentStyle && currentStyle.startsWith('tianditu_')) {
      this.props.dispatch(wrapTo('map', mapStyleChange('carto_positron')));
    }

    this.setState({ enableTianditu: val }, () => {
      // Kepler.gl only reads the mapStyles prop once on componentDidMount.
      // We must dispatch loadMapStyles ourselves — and it must be wrapped
      // with wrapTo('map') so it reaches the correct Kepler.gl instance reducer.
      const customStyles = this.getCustomMapStyles();

      // Grab existing registered styles from Redux state (includes already-loaded defaults)
      const existingStyles =
        (this.props.demo && this.props.demo.keplerGl && this.props.demo.keplerGl.map &&
         this.props.demo.keplerGl.map.mapStyle && this.props.demo.keplerGl.map.mapStyle.mapStyles)
        ? this.props.demo.keplerGl.map.mapStyle.mapStyles
        : {};

      // Merge: custom styles override existing by id
      const customById = customStyles.reduce((acc, s) => ({ ...acc, [s.id]: s }), {});
      const merged = { ...existingStyles, ...customById };

      // When disabling Tianditu, strip out any tianditu_* entries
      if (!val) {
        Object.keys(merged).forEach(id => {
          if (id.startsWith('tianditu_')) delete merged[id];
        });
      }

      // wrapTo('map') is required — without it the action goes to the root reducer
      // and is ignored by the Kepler.gl 'map' instance reducer.
      this.props.dispatch(wrapTo('map', loadMapStyles(merged)));
    });
  };

  // Builds the full custom style list passed to <KeplerGl mapStyles={}>.
  // When mapStylesReplaceDefault={true} (no user Mapbox token) these styles ARE
  // the entire basemap list.  When the user has a Mapbox token these are appended.
  // All styles use inline GL style objects (not data: URIs) so hasStyleObject()
  // returns true and Kepler.gl skips the URL-fetch step entirely.
  getCustomMapStyles = () => {
    const { enableTianditu } = this.state;

    const noBasemapStyle = {
      id: 'no_basemap',
      label: 'No Basemap (Light)',
      style: {
        version: 8,
        name: 'No Basemap (Light)',
        sources: {},
        layers: [
          {
            id: 'background',
            type: 'background',
            paint: {
              'background-color': 'rgba(0,0,0,0)'
            }
          }
        ]
      },
      icon: "data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='60' viewBox='0 0 80 60'%3E%3Crect width='80' height='60' fill='%23e2e8f0' rx='5'/%3E%3Ctext x='40' y='35' font-family='sans-serif' font-size='8' font-weight='bold' fill='%2364748b' text-anchor='middle'%3ENo Basemap (Light)%3C/text%3E%3C/svg%3E",
      layerGroups: []
    };

    // ── Free CartoDB styles — always included so the list is never empty ──────
    // These are exactly what Kepler's built-in "positron", "dark-matter" and
    // "voyager" styles point to, but supplied as inline objects so they work
    // even when mapStylesReplaceDefault=true strips built-ins.
    // NOTE: CartoDB styles are fetched by URL; Kepler will request them once and
    // cache in Redux.  Using the URL approach here is fine because CartoDB HTTPS
    // responses are cacheable and CORS-enabled.
    const freeStyles = [
      { id: 'carto_positron',    label: 'Positron (Light)',  url: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',    icon: 'https://basemaps.cartocdn.com/rastertiles/light_all/2/2/1.png',                   layerGroups: DEFAULT_LAYER_GROUPS },
      { id: 'carto_dark_matter', label: 'Dark Matter',       url: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', icon: 'https://basemaps.cartocdn.com/rastertiles/dark_all/2/2/1.png',                   layerGroups: DEFAULT_LAYER_GROUPS },
      { id: 'carto_voyager',     label: 'Voyager',           url: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',     icon: 'https://basemaps.cartocdn.com/rastertiles/voyager_labels_under/2/2/1.png',        layerGroups: DEFAULT_LAYER_GROUPS },
      noBasemapStyle
    ];

    if (!enableTianditu) return freeStyles;

    // ── Tianditu raster WMTS styles ───────────────────────────────────────────
    const token = '35a252740e435c4f754a18b08301ee3c';

    const buildRasterStyleObj = (name, layerCodes) => {
      const sources = {};
      const layers = [
        { id: 'background', type: 'background', paint: { 'background-color': 'rgba(0,0,0,0)' } }
      ];
      layerCodes.forEach(code => {
        sources[`src-${code}`] = {
          type: 'raster',
          tiles: [
            `https://t0.tianditu.gov.cn/${code}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=${code}&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=${token}`,
            `https://t1.tianditu.gov.cn/${code}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=${code}&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=${token}`,
            `https://t2.tianditu.gov.cn/${code}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=${code}&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=${token}`,
            `https://t3.tianditu.gov.cn/${code}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=${code}&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=${token}`
          ],
          tileSize: 256
        };
        layers.push({ id: `lyr-${code}`, type: 'raster', source: `src-${code}`, minzoom: 0, maxzoom: 18 });
      });
      return { version: 8, name, sources, layers };
    };

    const SATELLITE_ICON = "data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='60' viewBox='0 0 80 60'%3E%3Crect width='80' height='60' fill='%23152238' rx='5'/%3E%3Ccircle cx='40' cy='25' r='12' fill='%231d3557'/%3E%3Cpath d='M40,5 A20,20 0 0,1 60,25' stroke='%23e63946' stroke-width='2' fill='none'/%3E%3Ccircle cx='60' cy='25' r='3' fill='%23f1faee'/%3E%3Ctext x='40' y='44' font-family='sans-serif' font-size='9' font-weight='bold' fill='%23ffffff' text-anchor='middle'%3ETD Satellite%3C/text%3E%3C/svg%3E";
    const VECTOR_ICON   = "data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='60' viewBox='0 0 80 60'%3E%3Crect width='80' height='60' fill='%23f1faee' rx='5'/%3E%3Cline x1='10' y1='20' x2='70' y2='20' stroke='%23a8dadc' stroke-width='2'/%3E%3Cline x1='10' y1='40' x2='70' y2='40' stroke='%23a8dadc' stroke-width='2'/%3E%3Ccircle cx='40' cy='25' r='8' fill='%23457b9d'/%3E%3Ctext x='40' y='48' font-family='sans-serif' font-size='9' font-weight='bold' fill='%231d3557' text-anchor='middle'%3ETD Vector%3C/text%3E%3C/svg%3E";
    const TERRAIN_ICON  = "data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='60' viewBox='0 0 80 60'%3E%3Crect width='80' height='60' fill='%23e9c46a' rx='5'/%3E%3Cpath d='M10,45 L25,25 L40,35 L60,15 L70,30' fill='none' stroke='%23264653' stroke-width='2' stroke-linecap='round'/%3E%3Ctext x='40' y='52' font-family='sans-serif' font-size='9' font-weight='bold' fill='%23264653' text-anchor='middle'%3ETD Terrain%3C/text%3E%3C/svg%3E";

    // All labels in English. codes: [base-imagery, annotation-overlay]
    const tiandituDefs = [
      { id: 'tianditu_satellite_cn', label: 'Tianditu Satellite',   codes: ['img', 'cia'], icon: SATELLITE_ICON },
      { id: 'tianditu_vector_cn',    label: 'Tianditu Vector',      codes: ['vec', 'cva'], icon: VECTOR_ICON   },
      { id: 'tianditu_terrain_cn',   label: 'Tianditu Terrain',     codes: ['ter', 'cta'], icon: TERRAIN_ICON  },
    ];

    const tiandituStyles = tiandituDefs.map(d => ({
      id: d.id,
      label: d.label,
      // Inline style object — hasStyleObject() true → no URL fetch, renders immediately
      style: buildRasterStyleObj(d.label, d.codes),
      icon: d.icon,
      layerGroups: []
    }));

    return [...freeStyles, ...tiandituStyles];
  };

  _showBanner = () => {
    this.setState({ showBanner: true });
  };

  _hideBanner = () => {
    this.setState({ showBanner: false });
  };

  _disableBanner = () => {
    this._hideBanner();
    window.localStorage.setItem(BannerKey, 'true');
  };

  _loadMockNotifications = () => {
    const notifications = [
      [{ message: 'Welcome to Kepler.gl' }, 3000],
      [{ message: 'Something is wrong', type: 'error' }, 1000],
      [{ message: 'I am getting better', type: 'warning' }, 1000],
      [{ message: 'Everything is fine', type: 'success' }, 1000]
    ];

    this._addNotifications(notifications);
  };

  _addNotifications(notifications) {
    if (notifications && notifications.length) {
      const [notification, timeout] = notifications[0];

      window.setTimeout(() => {
        this.props.dispatch(addNotification(notification));
        this._addNotifications(notifications.slice(1));
      }, timeout);
    }
  }

  _loadSampleData() {
    this._loadPointData();
    this._loadGeojsonData();
    // this._loadTripGeoJson();
    // this._loadIconData();
    // this._loadH3HexagonData();
    // this._loadS2Data();
    // this._loadScenegraphLayer();
    // this._loadGpsData();
  }

  _loadPointData() {
    this.props.dispatch(
      addDataToMap({
        datasets: {
          info: {
            label: 'Sample Taxi Trips in New York City',
            id: 'test_trip_data',
            format: 'csv'
          },
          data: sampleTripData
        },
        options: {
          // centerMap: true,
          keepExistingConfig: true
        },
        config: sampleTripDataConfig
      })
    );
  }

  _loadScenegraphLayer() {
    this.props.dispatch(
      addDataToMap({
        datasets: {
          info: {
            label: 'Sample Scenegraph Ducks',
            id: 'test_trip_data',
            format: 'csv'
          },
          data: processCsvData(testCsvData)
        },
        config: {
          version: 'v1',
          config: {
            visState: {
              layers: [
                {
                  type: '3D',
                  config: {
                    dataId: 'test_trip_data',
                    columns: {
                      lat: 'gps_data.lat',
                      lng: 'gps_data.lng'
                    },
                    isVisible: true
                  }
                }
              ]
            }
          }
        }
      })
    );
  }

  _loadIconData() {
    // load icon data and config and process csv file
    this.props.dispatch(
      addDataToMap({
        datasets: [
          {
            info: {
              label: 'Icon Data',
              id: 'test_icon_data',
              format: 'csv'
            },
            data: processCsvData(sampleIconCsv)
          }
        ]
      })
    );
  }

  _loadTripGeoJson() {
    this.props.dispatch(
      addDataToMap({
        datasets: [
          {
            info: { label: 'Trip animation', id: animateTripDataId, format: 'geojson' },
            data: processGeojson(sampleAnimateTrip)
          }
        ]
      })
    );
  }

  _replaceData = () => {
    // add geojson data
    const sliceData = processGeojson({
      type: 'FeatureCollection',
      features: sampleGeojsonPoints.features.slice(0, 5)
    });
    this._loadGeojsonData();
    window.setTimeout(() => {
      this.props.dispatch(
        replaceDataInMap({
          datasetToReplaceId: 'bart-stops-geo',
          datasetToUse: {
            info: { label: 'Bart Stops Geo Replaced', id: 'bart-stops-geo-2', format: 'geojson' },
            data: sliceData
          }
        })
      );
    }, 1000);
  };

  _loadGeojsonData() {
    // load geojson
    this.props.dispatch(
      addDataToMap({
        datasets: [
          {
            info: { label: 'Bart Stops Geo', id: 'bart-stops-geo', format: 'geojson' },
            data: processGeojson(sampleGeojsonPoints)
          },
          {
            info: { label: 'SF Zip Geo', id: 'sf-zip-geo', format: 'geojson' },
            data: processGeojson(sampleGeojson)
          }
        ],
        options: {
          keepExistingConfig: true
        },
        config: sampleGeojsonConfig
      })
    );
  }

  _loadH3HexagonData() {
    // load h3 hexagon
    this.props.dispatch(
      addDataToMap({
        datasets: [
          {
            info: {
              label: 'H3 Hexagons V2',
              id: 'h3-hex-id',
              format: 'csv'
            },
            data: processCsvData(sampleH3Data)
          }
        ],
        config: h3MapConfig,
        options: {
          keepExistingConfig: true
        }
      })
    );
  }

  _loadS2Data() {
    // load s2
    this.props.dispatch(
      addDataToMap({
        datasets: [
          {
            info: {
              label: 'S2 Data',
              id: s2DataId,
              format: 'csv'
            },
            data: processCsvData(sampleS2Data)
          }
        ],
        config: s2MapConfig,
        options: {
          keepExistingConfig: true
        }
      })
    );
  }

  _loadGpsData() {
    this.props.dispatch(
      addDataToMap({
        datasets: [
          {
            info: {
              label: 'Gps Data',
              id: 'gps-data',
              format: 'csv'
            },
            data: processCsvData(sampleGpsData)
          }
        ],
        options: {
          keepExistingConfig: true
        }
      })
    );
  }
  _toggleCloudModal = () => {
    // TODO: this lives only in the demo hence we use the state for now
    // REFCOTOR using redux
    this.setState({
      cloudModalOpen: !this.state.cloudModalOpen
    });
  };

  _getMapboxRef = (mapbox, index) => {
    if (!mapbox) {
      // The ref has been unset.
      // https://reactjs.org/docs/refs-and-the-dom.html#callback-refs
      // console.log(`Map ${index} has closed`);
    } else {
      // We expect an InteractiveMap created by KeplerGl's MapContainer.
      // https://uber.github.io/react-map-gl/#/Documentation/api-reference/interactive-map
      const map = mapbox.getMap();
      map.on('zoomend', e => {
        // console.log(`Map ${index} zoom level: ${e.target.style.z}`);
      });
    }
  };

  _handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  _handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      const name = file.name.toLowerCase();

      if (name.endsWith('.tif') || name.endsWith('.tiff') || name.endsWith('.tree') || name.endsWith('.trees')) {
        alert('Please upload raw tree and raster files through the Setup tab pipeline, not directly to the map.');
        return;
      }

      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const fileContent = event.target.result;
          let processedData;

          if (name.endsWith('.geojson') || name.endsWith('.json')) {
            const rawJson = JSON.parse(fileContent);
            processedData = processGeojson(rawJson);
          } else if (name.endsWith('.csv')) {
            processedData = processCsvData(fileContent);
          } else {
            alert('Unsupported file format. Please drop a .geojson, .json, or .csv file.');
            return;
          }

          this.props.dispatch(addDataToMap({
            datasets: {
              info: {
                id: file.name,
                label: file.name
              },
              data: processedData
            }
          }));

          // Close the native modal immediately
          this.props.dispatch(wrapTo('map', toggleModal(null)));
        } catch (err) {
          alert(`Failed to parse dropped file: ${err.message}`);
        }
      };

      reader.onerror = () => {
        alert('Error reading dropped file.');
      };

      reader.readAsText(file);
    }
  };

  // Removed getAvailableHpdLevels and updateHpdFilter as filtering is now done before parsing.

  render() {
    const { activeTab } = this.state;
    return (
      <ThemeProvider theme={theme}>
        <GlobalStyle
          // this is to apply the same modal style as kepler.gl core
          // because styled-components doesn't always return a node
          // https://github.com/styled-components/styled-components/issues/617
          ref={node => {
            node ? (this.root = node) : null;
          }}
        >
          <PageWrapper>
            <TopNavBar>
              <LogoWrapper>
                <LogoText>spread.gl</LogoText>
                <LogoImage src="/logo.png" alt="logo" />
              </LogoWrapper>
              <NavTab $active={activeTab === 'config'} onClick={() => this.setState({ activeTab: 'config' })}>Setup</NavTab>
              <NavTab $active={activeTab === 'staging'} onClick={() => this.setState({ activeTab: 'staging' })}>Workspace</NavTab>
              <NavTab $active={activeTab === 'render'} onClick={() => this.setState({ activeTab: 'render' })}>Map</NavTab>
            </TopNavBar>

            <MainContentArea>
              {/* Kepler.gl: Always mounted but offscreen if not active */}
              <KeplerContainerWrapper 
                $active={activeTab === 'render'}
                onDragOverCapture={this._handleDragOver}
                onDropCapture={this._handleDrop}
              >
                <AutoSizer>
                  {({ height, width }) => (
                    <KeplerGl
                      mapboxApiAccessToken={this.state.userMapboxToken || ""}
                      id="map"
                      /*
                       * Specify path to keplerGl state, because it is not mount at the root
                       */
                      getState={keplerGlGetState}
                      width={width}
                      height={height}
                      cloudProviders={CLOUD_PROVIDERS}
                      localeMessages={messages}
                      onExportToCloudSuccess={onExportFileSuccess}
                      onLoadCloudMapSuccess={onLoadCloudMapSuccess}
                      featureFlags={DEFAULT_FEATURE_FLAGS}
                      mapStyles={this.getCustomMapStyles()}
                      mapStylesReplaceDefault={!this.state.userMapboxToken}
                    />
                  )}
                </AutoSizer>
              </KeplerContainerWrapper>

              {/* DataPipelineControl (Config and Staging): Always mounted but hidden offscreen if activeTab is render */}
              <PipelineContainerWrapper $active={activeTab !== 'render'}>
                <div style={{ width: '100%', maxWidth: '800px' }}>
                  <DataPipelineControl 
                    dispatch={this.props.dispatch}
                    activeTab={activeTab}
                    setActiveTab={(tab) => this.setState({ activeTab: tab })}
                    userMapboxToken={this.state.userMapboxToken}
                    setUserMapboxToken={this.setUserMapboxToken}
                    enableTianditu={this.state.enableTianditu}
                    setEnableTianditu={this.setEnableTianditu}
                    onResultsChange={(results) => this.setState({ pipelineResults: results })}
                  />
                </div>
              </PipelineContainerWrapper>
            </MainContentArea>
          </PageWrapper>
        </GlobalStyle>
      </ThemeProvider>
    );
  }
}

const mapStateToProps = state => state;
const dispatchToProps = dispatch => ({ dispatch });

export default connect(mapStateToProps, dispatchToProps)(App);
