'use strict'

const { VueLoaderPlugin } = require('vue-loader')
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const { resolve } = require('path')
const webpack = require('webpack');

module.exports = {
  mode: 'development',
  entry: './src/index.js',
  output: {
    filename: 'index.js',
    libraryTarget: 'umd',
    path: resolve(__dirname)
  },
  resolve: {
    extensions: ['.js', '.vue', '.css'],
    alias: {
        'quasar': resolve(__dirname, './node_modules/quasar-framework/dist/quasar.mat.esm.js'), // https://github.com/quasarframework/quasar/issues/1576
        'variables': resolve(__dirname, './node_modules/quasar-framework/dist/quasar.mat.styl')
    }
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        use: 'vue-loader'
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      },
      {
        test: /\.css$/,
        use: [
          'vue-style-loader',
          'css-loader'
        ]
      },
      {
        test: /\.styl(us)?$/,
        use: [
          'vue-style-loader',
          'css-loader',
          'stylus-loader'
        ]
      }
    ]
  },
  plugins: [
    new VueLoaderPlugin(),
    new webpack.DllReferencePlugin({
        context: ".",
        manifest: require("./node_modules/ething-quasar-dll/dist/vendor-manifest.json")
    }),
    new BundleAnalyzerPlugin()
  ],
  externals: [
      'vue',
      'quasar',
      'axios',
      {
        'ething-quasar-core': 'EThingUI',
        'ething-js': 'EThing'
      }
  ]
}
