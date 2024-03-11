// SPDX-License-Identifier: MIT
// Copyright contributors to the kepler.gl project

const {resolve} = require('path');
const NODE_MODULES_DIR = resolve('./node_modules');

const resolveAlias = {
  react: `${NODE_MODULES_DIR}/react`,
  'react-dom': `${NODE_MODULES_DIR}/react-dom`,
  'react-redux': `${NODE_MODULES_DIR}/react-redux/lib`,
  'styled-components': `${NODE_MODULES_DIR}/styled-components`,
  'react-intl': `${NODE_MODULES_DIR}/react-intl`,
  'apache-arrow': `${NODE_MODULES_DIR}/apache-arrow`
};

const ENV_VARIABLES_WITH_INSTRUCTIONS = {
  MapboxAccessToken: 'You can get the token at https://www.mapbox.com/help/how-access-tokens-work/',
  DropboxClientId: 'z35apgncl4fpc6s',
  CartoClientId: 'You can get the token at https://www.mapbox.com/help/how-access-tokens-work/',
  MapboxExportToken: 'You can get the token at https://location.foursquare.com/developer',
  FoursquareClientId: 'You can get the token at https://location.foursquare.com/developer',
  FoursquareDomain: 'You can get the token at https://location.foursquare.com/developer',
  FoursquareAPIURL: 'You can get the token at https://location.foursquare.com/developer',
  FoursquareUserMapsURL: 'You can get the token at https://location.foursquare.com/developer',
};

const WEBPACK_ENV_VARIABLES = Object.keys(ENV_VARIABLES_WITH_INSTRUCTIONS).reduce((acc, key) => ({
  ...acc,
  [key]: ENV_VARIABLES_WITH_INSTRUCTIONS[key] || null
}), {});

module.exports = {
  ENV_VARIABLES_WITH_INSTRUCTIONS,
  WEBPACK_ENV_VARIABLES,
  RESOLVE_ALIASES: resolveAlias
}
