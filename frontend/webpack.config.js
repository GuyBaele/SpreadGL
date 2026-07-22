const resolve = require('path').resolve;
const join = require('path').join;
const path = require('path');
const webpack = require('webpack');
const { WEBPACK_ENV_VARIABLES, RESOLVE_ALIASES } = require('./shared-webpack-configuration');

// Create an empty stub module for optional deps that don't exist at our locked versions
const EMPTY_MODULE = path.resolve(__dirname, 'src/empty-module.js');

const CONFIG = {

  entry: {
    app: resolve('./src/main.js')
  },
  output: {
    path: resolve(__dirname, 'build'),
    filename: 'bundle.js',
    publicPath: '/'
  },

  resolve: {
    extensions: ['.tsx', '.ts', '.jsx', '.js'],
    fallback: {
      "path": require.resolve("path-browserify")
    },
    // Stub out optional/unavailable transitive dependencies
    alias: {
      '@loaders.gl/schema-utils': EMPTY_MODULE,
      ...RESOLVE_ALIASES,
      '@loaders.gl/core': path.resolve(__dirname, 'node_modules/@loaders.gl/core'),
      '@loaders.gl/csv': path.resolve(__dirname, 'node_modules/@loaders.gl/csv'),
      '@loaders.gl/json': path.resolve(__dirname, 'node_modules/@loaders.gl/json'),
      '@loaders.gl/arrow': path.resolve(__dirname, 'node_modules/@loaders.gl/arrow'),
    }
  },

  devtool: 'source-map',

  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        include: [join(__dirname, 'src')],
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-react", "@babel/preset-env", "@babel/preset-typescript"],
          }
        }
      },

      {
        test: /\.mjs$/,
        include: /node_modules/,
        type: 'javascript/auto',
        resolve: {
          fullySpecified: false
        }
      },
      {
        test: /\.js$/,
        resolve: {
          fullySpecified: false
        }
      }
    ]
  },

  devServer: {
    historyApiFallback: true,
    contentBase: resolve(__dirname, '.'),
    watchContentBase: true
  },

  stats: {
    errorDetails: true
  },

  plugins: [
    new webpack.EnvironmentPlugin(WEBPACK_ENV_VARIABLES),
    new webpack.DefinePlugin({
      'process.env': JSON.stringify({
        NODE_ENV: 'development',
        ...WEBPACK_ENV_VARIABLES
      })
    })
  ]
};

module.exports = CONFIG;
