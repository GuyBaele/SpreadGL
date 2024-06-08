const resolve = require('path').resolve;
const join = require('path').join;
const webpack = require('webpack');
const WEBPACK_ENV_VARIABLES = require('./shared-webpack-configuration').WEBPACK_ENV_VARIABLES;

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
        type: 'javascript/auto'
      }
    ]
  },

  devServer: {
    host: '0.0.0.0',
    port: 8080,
    historyApiFallback: true
  },

  stats: {
    errorDetails: true
  },

  plugins: [
    new webpack.EnvironmentPlugin(WEBPACK_ENV_VARIABLES),
    new webpack.DefinePlugin({
      'process.env':{
        NODE_ENV: JSON.stringify("development")
      }
    })
  ]
};

module.exports = CONFIG;
