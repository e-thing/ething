(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory(require("EThingUI"));
	else if(typeof define === 'function' && define.amd)
		define(["EThingUI"], factory);
	else {
		var a = typeof exports === 'object' ? factory(require("EThingUI")) : factory(root["EThingUI"]);
		for(var i in a) (typeof exports === 'object' ? exports : root)[i] = a[i];
	}
})(window, function(__WEBPACK_EXTERNAL_MODULE_ething_quasar_core__) {
return /******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./src/index.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./node_modules/axios/index.js":
/*!*****************************************************************************!*\
  !*** delegated ./node_modules/axios/index.js from dll-reference vendor_lib ***!
  \*****************************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("module.exports = (__webpack_require__(/*! dll-reference vendor_lib */ \"dll-reference vendor_lib\"))(42);\n\n//# sourceURL=webpack:///delegated_./node_modules/axios/index.js_from_dll-reference_vendor_lib?");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js?!./node_modules/vue-loader/lib/index.js?!./src/components/WOpenWeatherMapForecast.vue?vue&type=script&lang=js&":
/*!***********************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib??ref--1!./node_modules/vue-loader/lib??vue-loader-options!./src/components/WOpenWeatherMapForecast.vue?vue&type=script&lang=js& ***!
  \***********************************************************************************************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var ething_quasar_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ething-quasar-core */ \"ething-quasar-core\");\n/* harmony import */ var ething_quasar_core__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(ething_quasar_core__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _openweathermap__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../openweathermap */ \"./src/openweathermap.js\");\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n\n\nvar weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']; // clear sky -> worst\n\nvar weatherConditionWeightMap = [[800, 899], // Clear + Clouds\n[700, 799], // Atmosphere\n[300, 399], // Drizzle\n[500, 599], // Rain\n[200, 299], // Thunderstorm\n[600, 699]];\n\nfunction weightedWeatherCondition(weatherConditionId) {\n  for (var i in weatherConditionWeightMap) {\n    var minIndex = weatherConditionWeightMap[i][0];\n    var maxIndex = weatherConditionWeightMap[i][1];\n\n    if (weatherConditionId >= minIndex && weatherConditionId <= maxIndex) {\n      return i * 100 + (weatherConditionId - minIndex);\n    }\n  }\n\n  return 0;\n}\n\nfunction windDirection(deg) {\n  if (typeof deg !== 'number') return '';\n  var windDirectionMap = ['N', 'N-E', 'E', 'S-E', 'S', 'S-O', 'O', 'N-O', 'N'];\n  var windDirectionMapStep = 45;\n  var selectedIndex = null;\n  var diff = 0;\n\n  for (var i in windDirectionMap) {\n    var ideg = i * windDirectionMapStep;\n    var d = deg - ideg;\n\n    if (selectedIndex === null || d < diff) {\n      selectedIndex = i;\n      diff = d;\n    }\n  }\n\n  return selectedIndex !== null ? windDirectionMap[selectedIndex] : '';\n}\n\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  name: 'WOpenWeatherMapForecast',\n  extends: ething_quasar_core__WEBPACK_IMPORTED_MODULE_0___default.a.widgets.WWidget,\n  components: {\n    WLayout: ething_quasar_core__WEBPACK_IMPORTED_MODULE_0___default.a.widgets.WLayout\n  },\n  metadata: {\n    label: 'OpenWeatherMap forecast widget',\n    description: 'display weather forecast',\n    minHeight: 120,\n    options: {\n      properties: {\n        location: {\n          type: 'string',\n          minLength: 1\n        },\n        mode: {\n          enum: ['now', '24h', '5d']\n        }\n      }\n    }\n  },\n  props: {\n    location: String,\n    mode: {\n      type: String,\n      default: 'now'\n    }\n  },\n  data: function data() {\n    var appid = null;\n\n    if (ething_quasar_core__WEBPACK_IMPORTED_MODULE_0___default.a.settings && ething_quasar_core__WEBPACK_IMPORTED_MODULE_0___default.a.settings.OpenWeatherMapPlugin) {\n      appid = ething_quasar_core__WEBPACK_IMPORTED_MODULE_0___default.a.settings.OpenWeatherMapPlugin.appid;\n    }\n\n    return {\n      appid: appid,\n      raw: {},\n      timerId: null\n    };\n  },\n  computed: {\n    city: function city() {\n      if (this.raw.city) return this.raw.city.name;\n      if (this.raw.name) return this.raw.name;\n    },\n    twentyFourHoursItems: function twentyFourHoursItems() {\n      var items = [];\n\n      if (this.raw.list && this.raw.cnt) {\n        var now = Date.now();\n        var end = now + 24 * 3600 * 1000;\n        this.raw.list.forEach(function (it) {\n          var dt = it.dt * 1000;\n\n          if (dt <= end) {\n            items.push({\n              date: new Date(dt),\n              temperature: it.main.temp,\n              pressure: it.main.pressure,\n              humidity: it.main.humidity,\n              weather: it.weather.description,\n              icon: it.weather[0].icon,\n              iconUrl: _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"iconPath\"] + '/' + it.weather[0].icon + '.' + _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"iconExt\"],\n              windSpeed: it.wind.speed,\n              windDirection: windDirection(it.wind.deg)\n            });\n          }\n        });\n      }\n\n      return items;\n    },\n    fiveDaysItems: function fiveDaysItems() {\n      var items = [];\n\n      if (this.raw.list && this.raw.cnt) {\n        var initItem = function initItem() {\n          item = {\n            cnt: 0,\n            date: [],\n            temperature: [],\n            humidity: [],\n            weatherConditionWeight: [],\n            icon: []\n          };\n        };\n\n        var endItem = function endItem() {\n          var sum = function sum(accumulator, currentValue) {\n            return accumulator + currentValue;\n          };\n\n          var min = function min(accumulator, currentValue) {\n            return accumulator < currentValue ? accumulator : currentValue;\n          };\n\n          var max = function max(accumulator, currentValue) {\n            return accumulator > currentValue ? accumulator : currentValue;\n          };\n\n          if (item.cnt >= 1) {\n            item.minTemperature = item.temperature.reduce(min);\n            item.maxTemperature = item.temperature.reduce(max);\n            item.temperature = item.temperature.reduce(sum) / item.cnt;\n            item.humidity = item.humidity.reduce(sum) / item.cnt; // select only hour beetween 9h and 18h(excluded)\n\n            var startd = new Date(item.date[0]);\n            startd.setHours(9, 0, 0, 0);\n            startd = startd.getTime();\n            var endd = new Date(item.date[0]);\n            endd.setHours(17, 0, 0, 0);\n            endd = endd.getTime();\n            var selectedIcon = null;\n            var selectedW = null;\n\n            for (var i in item.date) {\n              var dt = item.date[i];\n\n              if (dt >= startd && dt < endd) {\n                var w = item.weatherConditionWeight[i];\n\n                if (selectedW === null || selectedW > w) {\n                  selectedW = w;\n                  selectedIcon = item.icon[i];\n                }\n              }\n            }\n\n            if (selectedW === null) {\n              for (var i in item.date) {\n                var w = item.weatherConditionWeight[i];\n\n                if (selectedW === null || selectedW > w) {\n                  selectedW = w;\n                  selectedIcon = item.icon[i];\n                }\n              }\n            }\n\n            item.date = new Date(item.date[0]);\n            item.weekday = weekdays[item.date.getDay()];\n\n            if (selectedW !== null && items.length < 5) {\n              item.icon = selectedIcon;\n              item.weatherConditionWeight = selectedW;\n              item.iconUrl = _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"iconPath\"] + '/' + item.icon + '.' + _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"iconExt\"];\n              items.push(item);\n            }\n          }\n        };\n\n        var midnight = new Date();\n        midnight.setHours(24, 0, 0, 0);\n        midnight = midnight.getTime();\n        var item;\n        initItem();\n        this.raw.list.forEach(function (it) {\n          var dt = it.dt * 1000;\n\n          if (dt > midnight) {\n            midnight += 24 * 3600 * 1000;\n            endItem(); // new day\n\n            initItem();\n          }\n\n          item.cnt += 1;\n          item.date.push(dt);\n          item.temperature.push(it.main.temp);\n          item.humidity.push(it.main.humidity);\n          item.weatherConditionWeight.push(weightedWeatherCondition(it.weather[0].id));\n          item.icon.push(it.weather[0].icon);\n        });\n        endItem();\n      }\n\n      return items;\n    },\n    nowItems: function nowItems() {\n      var items = [];\n\n      if (this.raw.main) {\n        items.push({\n          date: new Date(this.raw.dt * 1000),\n          temperature: this.raw.main.temp,\n          pressure: this.raw.main.pressure,\n          humidity: this.raw.main.humidity,\n          weather: this.raw.weather.description,\n          icon: this.raw.weather[0].icon,\n          iconUrl: _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"iconPath\"] + '/' + this.raw.weather[0].icon + '.' + _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"iconExt\"],\n          windSpeed: this.raw.wind.speed,\n          windDirection: windDirection(this.raw.wind.deg)\n        });\n      }\n\n      return items;\n    },\n    items: function items() {\n      if (this.mode === '24h') {\n        return this.twentyFourHoursItems;\n      }\n\n      if (this.mode === '5d') {\n        return this.fiveDaysItems;\n      }\n\n      if (this.mode === 'now') {\n        return this.nowItems;\n      }\n\n      return [];\n    }\n  },\n  methods: {\n    load: function load() {\n      var _this = this;\n\n      var fncall = this.mode === 'now' ? _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"getWeather\"] : _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"getWeatherForecast\"];\n      fncall(this.appid, this.location, function (data) {\n        _this.raw = data;\n      });\n    },\n    rounded: function rounded(value) {\n      var digits = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 0;\n      return parseFloat(value).toFixed(digits);\n    }\n  },\n  mounted: function mounted() {\n    var _this2 = this;\n\n    if (this.appid) {\n      this.load();\n      this.timerId = setInterval(function () {\n        _this2.load();\n      }, 300000);\n    } else {\n      this.setError('no appid set in the plugin settings');\n    }\n  },\n  beforeDestroy: function beforeDestroy() {\n    if (this.timerId !== null) {\n      clearInterval(this.timerId);\n    }\n  }\n});\n\n//# sourceURL=webpack:///./src/components/WOpenWeatherMapForecast.vue?./node_modules/babel-loader/lib??ref--1!./node_modules/vue-loader/lib??vue-loader-options");

/***/ }),

/***/ "./node_modules/vue-loader/lib/loaders/templateLoader.js?!./node_modules/vue-loader/lib/index.js?!./src/components/WOpenWeatherMapForecast.vue?vue&type=template&id=0d43a424&":
/*!*****************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/vue-loader/lib/loaders/templateLoader.js??vue-loader-options!./node_modules/vue-loader/lib??vue-loader-options!./src/components/WOpenWeatherMapForecast.vue?vue&type=template&id=0d43a424& ***!
  \*****************************************************************************************************************************************************************************************************************/
/*! exports provided: render, staticRenderFns */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return render; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"staticRenderFns\", function() { return staticRenderFns; });\nvar render = function() {\n  var _vm = this\n  var _h = _vm.$createElement\n  var _c = _vm._self._c || _h\n  return _c(\"w-layout\", { attrs: { noFooter: \"\", title: _vm.city } }, [\n    _c(\"div\", { staticClass: \"overflow-hidden\" }, [\n      _c(\n        \"div\",\n        { staticClass: \"row gutter-xs\" },\n        _vm._l(_vm.items, function(item) {\n          return _c(\"div\", { staticClass: \"col text-center\" }, [\n            _vm.mode !== \"now\"\n              ? _c(\"div\", { staticClass: \"date text-faded\" }, [\n                  _c(\n                    \"small\",\n                    [\n                      _vm.mode === \"5d\"\n                        ? [\n                            _vm._v(\n                              \"\\n                            \" +\n                                _vm._s(item.weekday) +\n                                \"\\n                        \"\n                            )\n                          ]\n                        : [\n                            _vm._v(\n                              \"\\n                            \" +\n                                _vm._s(item.date.getHours()) +\n                                \"h\\n                        \"\n                            )\n                          ]\n                    ],\n                    2\n                  )\n                ])\n              : _vm._e(),\n            _vm._v(\" \"),\n            _c(\"img\", { attrs: { src: item.iconUrl } }),\n            _vm._v(\" \"),\n            _c(\"div\", [\n              _c(\"span\", { staticClass: \"temperature text-faded\" }, [\n                _vm._v(\n                  _vm._s(\n                    _vm.rounded(\n                      _vm.mode === \"5d\" ? item.maxTemperature : item.temperature\n                    )\n                  ) + \"°C\"\n                )\n              ]),\n              _vm._v(\" \"),\n              _c(\"span\", { staticClass: \"humidity text-blue q-ml-xs\" }, [\n                _vm._v(_vm._s(_vm.rounded(item.humidity)) + \"%\")\n              ])\n            ]),\n            _vm._v(\" \"),\n            item.pressure\n              ? _c(\"div\", { staticClass: \"pressure text-faded\" }, [\n                  _vm._v(_vm._s(_vm.rounded(item.pressure)) + \" Pa\")\n                ])\n              : _vm._e(),\n            _vm._v(\" \"),\n            item.windSpeed\n              ? _c(\n                  \"div\",\n                  { staticClass: \"wind text-faded\" },\n                  [\n                    item.windDirection\n                      ? [_vm._v(_vm._s(item.windDirection))]\n                      : _vm._e(),\n                    _vm._v(\" \" + _vm._s(_vm.rounded(item.windSpeed)) + \" m/s\")\n                  ],\n                  2\n                )\n              : _vm._e()\n          ])\n        }),\n        0\n      )\n    ])\n  ])\n}\nvar staticRenderFns = []\nrender._withStripped = true\n\n\n\n//# sourceURL=webpack:///./src/components/WOpenWeatherMapForecast.vue?./node_modules/vue-loader/lib/loaders/templateLoader.js??vue-loader-options!./node_modules/vue-loader/lib??vue-loader-options");

/***/ }),

/***/ "./node_modules/vue-loader/lib/runtime/componentNormalizer.js":
/*!********************************************************************!*\
  !*** ./node_modules/vue-loader/lib/runtime/componentNormalizer.js ***!
  \********************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"default\", function() { return normalizeComponent; });\n/* globals __VUE_SSR_CONTEXT__ */\n\n// IMPORTANT: Do NOT use ES2015 features in this file (except for modules).\n// This module is a runtime utility for cleaner component module output and will\n// be included in the final webpack user bundle.\n\nfunction normalizeComponent (\n  scriptExports,\n  render,\n  staticRenderFns,\n  functionalTemplate,\n  injectStyles,\n  scopeId,\n  moduleIdentifier, /* server only */\n  shadowMode /* vue-cli only */\n) {\n  // Vue.extend constructor export interop\n  var options = typeof scriptExports === 'function'\n    ? scriptExports.options\n    : scriptExports\n\n  // render functions\n  if (render) {\n    options.render = render\n    options.staticRenderFns = staticRenderFns\n    options._compiled = true\n  }\n\n  // functional template\n  if (functionalTemplate) {\n    options.functional = true\n  }\n\n  // scopedId\n  if (scopeId) {\n    options._scopeId = 'data-v-' + scopeId\n  }\n\n  var hook\n  if (moduleIdentifier) { // server build\n    hook = function (context) {\n      // 2.3 injection\n      context =\n        context || // cached call\n        (this.$vnode && this.$vnode.ssrContext) || // stateful\n        (this.parent && this.parent.$vnode && this.parent.$vnode.ssrContext) // functional\n      // 2.2 with runInNewContext: true\n      if (!context && typeof __VUE_SSR_CONTEXT__ !== 'undefined') {\n        context = __VUE_SSR_CONTEXT__\n      }\n      // inject component styles\n      if (injectStyles) {\n        injectStyles.call(this, context)\n      }\n      // register component module identifier for async chunk inferrence\n      if (context && context._registeredComponents) {\n        context._registeredComponents.add(moduleIdentifier)\n      }\n    }\n    // used by ssr in case component is cached and beforeCreate\n    // never gets called\n    options._ssrRegister = hook\n  } else if (injectStyles) {\n    hook = shadowMode\n      ? function () { injectStyles.call(this, this.$root.$options.shadowRoot) }\n      : injectStyles\n  }\n\n  if (hook) {\n    if (options.functional) {\n      // for template-only hot-reload because in that case the render fn doesn't\n      // go through the normalizer\n      options._injectStyles = hook\n      // register for functioal component in vue file\n      var originalRender = options.render\n      options.render = function renderWithStyleInjection (h, context) {\n        hook.call(context)\n        return originalRender(h, context)\n      }\n    } else {\n      // inject component registration as beforeCreate hook\n      var existing = options.beforeCreate\n      options.beforeCreate = existing\n        ? [].concat(existing, hook)\n        : [hook]\n    }\n  }\n\n  return {\n    exports: scriptExports,\n    options: options\n  }\n}\n\n\n//# sourceURL=webpack:///./node_modules/vue-loader/lib/runtime/componentNormalizer.js?");

/***/ }),

/***/ "./src/components/WOpenWeatherMapDevice.js":
/*!*************************************************!*\
  !*** ./src/components/WOpenWeatherMapDevice.js ***!
  \*************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var ething_quasar_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ething-quasar-core */ \"ething-quasar-core\");\n/* harmony import */ var ething_quasar_core__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(ething_quasar_core__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _openweathermap__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../openweathermap */ \"./src/openweathermap.js\");\n\n\nvar WDeviceMultiLabel = ething_quasar_core__WEBPACK_IMPORTED_MODULE_0___default.a.widgets.WDeviceMultiLabel;\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  name: 'WOpenWeatherMapDevice',\n  extends: WDeviceMultiLabel,\n  metadata: {\n    label: 'default widget',\n    description: 'display the current weather informations',\n    minHeight: 250\n  },\n  props: {\n    items: {\n      default: function _default() {\n        return [{\n          label: 'temperature',\n          unit: '°C',\n          attr: 'temperature'\n        }, {\n          label: 'humidity',\n          unit: '%',\n          attr: 'humidity'\n        }, {\n          label: 'pressure',\n          unit: 'Pa',\n          attr: 'pressure'\n        }, {\n          label: 'weather',\n          attr: 'weather',\n          done: function done() {\n            for (var i in _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"weatherMap\"]) {\n              if (this.value === _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"weatherMap\"][i].description) {\n                if (_openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"weatherMap\"][i].icon) {\n                  var icon;\n\n                  if (Array.isArray(_openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"weatherMap\"][i].icon)) {\n                    var now = new Date();\n                    var hours = now.getHours();\n                    var index = hours >= 21 ? 1 : 0;\n                    icon = _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"weatherMap\"][i].icon[index];\n                  } else {\n                    icon = _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"weatherMap\"][i].icon;\n                  }\n\n                  this.icon = true;\n                  this.value = _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"iconPath\"] + '/' + icon + '.' + _openweathermap__WEBPACK_IMPORTED_MODULE_1__[\"iconExt\"];\n                }\n\n                return;\n              }\n            }\n          }\n        }, {\n          label: 'wind speed',\n          attr: 'wind_speed',\n          unit: 'm/s'\n        }, {\n          label: 'wind direction',\n          attr: 'wind_direction',\n          skipIfNull: true,\n          map: [{\n            key: 0,\n            value: 'N'\n          }, {\n            key: 45,\n            value: 'N-E'\n          }, {\n            key: 90,\n            value: 'E'\n          }, {\n            key: 135,\n            value: 'S-E'\n          }, {\n            key: 180,\n            value: 'S'\n          }, {\n            key: 225,\n            value: 'S-O'\n          }, {\n            key: 270,\n            value: 'O'\n          }, {\n            key: 315,\n            value: 'N-O'\n          }, {\n            key: 360,\n            value: 'N'\n          }]\n        }];\n      }\n    }\n  }\n});\n\n//# sourceURL=webpack:///./src/components/WOpenWeatherMapDevice.js?");

/***/ }),

/***/ "./src/components/WOpenWeatherMapForecast.vue":
/*!****************************************************!*\
  !*** ./src/components/WOpenWeatherMapForecast.vue ***!
  \****************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _WOpenWeatherMapForecast_vue_vue_type_template_id_0d43a424___WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./WOpenWeatherMapForecast.vue?vue&type=template&id=0d43a424& */ \"./src/components/WOpenWeatherMapForecast.vue?vue&type=template&id=0d43a424&\");\n/* harmony import */ var _WOpenWeatherMapForecast_vue_vue_type_script_lang_js___WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./WOpenWeatherMapForecast.vue?vue&type=script&lang=js& */ \"./src/components/WOpenWeatherMapForecast.vue?vue&type=script&lang=js&\");\n/* empty/unused harmony star reexport *//* harmony import */ var _node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../node_modules/vue-loader/lib/runtime/componentNormalizer.js */ \"./node_modules/vue-loader/lib/runtime/componentNormalizer.js\");\n\n\n\n\n\n/* normalize component */\n\nvar component = Object(_node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_2__[\"default\"])(\n  _WOpenWeatherMapForecast_vue_vue_type_script_lang_js___WEBPACK_IMPORTED_MODULE_1__[\"default\"],\n  _WOpenWeatherMapForecast_vue_vue_type_template_id_0d43a424___WEBPACK_IMPORTED_MODULE_0__[\"render\"],\n  _WOpenWeatherMapForecast_vue_vue_type_template_id_0d43a424___WEBPACK_IMPORTED_MODULE_0__[\"staticRenderFns\"],\n  false,\n  null,\n  null,\n  null\n  \n)\n\n/* hot reload */\nif (false) { var api; }\ncomponent.options.__file = \"src/components/WOpenWeatherMapForecast.vue\"\n/* harmony default export */ __webpack_exports__[\"default\"] = (component.exports);\n\n//# sourceURL=webpack:///./src/components/WOpenWeatherMapForecast.vue?");

/***/ }),

/***/ "./src/components/WOpenWeatherMapForecast.vue?vue&type=script&lang=js&":
/*!*****************************************************************************!*\
  !*** ./src/components/WOpenWeatherMapForecast.vue?vue&type=script&lang=js& ***!
  \*****************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_babel_loader_lib_index_js_ref_1_node_modules_vue_loader_lib_index_js_vue_loader_options_WOpenWeatherMapForecast_vue_vue_type_script_lang_js___WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib??ref--1!../../node_modules/vue-loader/lib??vue-loader-options!./WOpenWeatherMapForecast.vue?vue&type=script&lang=js& */ \"./node_modules/babel-loader/lib/index.js?!./node_modules/vue-loader/lib/index.js?!./src/components/WOpenWeatherMapForecast.vue?vue&type=script&lang=js&\");\n/* empty/unused harmony star reexport */ /* harmony default export */ __webpack_exports__[\"default\"] = (_node_modules_babel_loader_lib_index_js_ref_1_node_modules_vue_loader_lib_index_js_vue_loader_options_WOpenWeatherMapForecast_vue_vue_type_script_lang_js___WEBPACK_IMPORTED_MODULE_0__[\"default\"]); \n\n//# sourceURL=webpack:///./src/components/WOpenWeatherMapForecast.vue?");

/***/ }),

/***/ "./src/components/WOpenWeatherMapForecast.vue?vue&type=template&id=0d43a424&":
/*!***********************************************************************************!*\
  !*** ./src/components/WOpenWeatherMapForecast.vue?vue&type=template&id=0d43a424& ***!
  \***********************************************************************************/
/*! exports provided: render, staticRenderFns */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_vue_loader_lib_loaders_templateLoader_js_vue_loader_options_node_modules_vue_loader_lib_index_js_vue_loader_options_WOpenWeatherMapForecast_vue_vue_type_template_id_0d43a424___WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/vue-loader/lib/loaders/templateLoader.js??vue-loader-options!../../node_modules/vue-loader/lib??vue-loader-options!./WOpenWeatherMapForecast.vue?vue&type=template&id=0d43a424& */ \"./node_modules/vue-loader/lib/loaders/templateLoader.js?!./node_modules/vue-loader/lib/index.js?!./src/components/WOpenWeatherMapForecast.vue?vue&type=template&id=0d43a424&\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return _node_modules_vue_loader_lib_loaders_templateLoader_js_vue_loader_options_node_modules_vue_loader_lib_index_js_vue_loader_options_WOpenWeatherMapForecast_vue_vue_type_template_id_0d43a424___WEBPACK_IMPORTED_MODULE_0__[\"render\"]; });\n\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"staticRenderFns\", function() { return _node_modules_vue_loader_lib_loaders_templateLoader_js_vue_loader_options_node_modules_vue_loader_lib_index_js_vue_loader_options_WOpenWeatherMapForecast_vue_vue_type_template_id_0d43a424___WEBPACK_IMPORTED_MODULE_0__[\"staticRenderFns\"]; });\n\n\n\n//# sourceURL=webpack:///./src/components/WOpenWeatherMapForecast.vue?");

/***/ }),

/***/ "./src/index.js":
/*!**********************!*\
  !*** ./src/index.js ***!
  \**********************/
/*! no exports provided */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _components_WOpenWeatherMapDevice__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./components/WOpenWeatherMapDevice */ \"./src/components/WOpenWeatherMapDevice.js\");\n/* harmony import */ var _components_WOpenWeatherMapForecast__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./components/WOpenWeatherMapForecast */ \"./src/components/WOpenWeatherMapForecast.vue\");\n/* harmony import */ var ething_quasar_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ething-quasar-core */ \"ething-quasar-core\");\n/* harmony import */ var ething_quasar_core__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(ething_quasar_core__WEBPACK_IMPORTED_MODULE_2__);\n\n\n\nconsole.log('loading plugin OpenWeatherMap...');\nething_quasar_core__WEBPACK_IMPORTED_MODULE_2___default.a.registerWidget(_components_WOpenWeatherMapDevice__WEBPACK_IMPORTED_MODULE_0__[\"default\"]);\nething_quasar_core__WEBPACK_IMPORTED_MODULE_2___default.a.registerWidget(_components_WOpenWeatherMapForecast__WEBPACK_IMPORTED_MODULE_1__[\"default\"]);\nething_quasar_core__WEBPACK_IMPORTED_MODULE_2___default.a.extend('resources/OpenWeatherMapDevice', {\n  icon: 'mdi-weather-partlycloudy',\n  widgets: {\n    'default': 'WOpenWeatherMapDevice'\n  }\n});\n\n//# sourceURL=webpack:///./src/index.js?");

/***/ }),

/***/ "./src/openweathermap.js":
/*!*******************************!*\
  !*** ./src/openweathermap.js ***!
  \*******************************/
/*! exports provided: OPEN_WEATHER_MAP_WEATHER_URL, OPEN_WEATHER_MAP_FORECAST_URL, iconPath, iconExt, weatherMap, getWeather, getWeatherForecast */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"OPEN_WEATHER_MAP_WEATHER_URL\", function() { return OPEN_WEATHER_MAP_WEATHER_URL; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"OPEN_WEATHER_MAP_FORECAST_URL\", function() { return OPEN_WEATHER_MAP_FORECAST_URL; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"iconPath\", function() { return iconPath; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"iconExt\", function() { return iconExt; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"weatherMap\", function() { return weatherMap; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"getWeather\", function() { return getWeather; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"getWeatherForecast\", function() { return getWeatherForecast; });\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! axios */ \"./node_modules/axios/index.js\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_0__);\n\nvar OPEN_WEATHER_MAP_WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?units=metric';\nvar OPEN_WEATHER_MAP_FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast?units=metric';\nvar iconPath = 'http://openweathermap.org/img/w';\nvar iconExt = 'png';\nvar weatherMap = [{\n  id: '200',\n  description: 'thunderstorm with light rain',\n  icon: '11d'\n}, {\n  id: '201',\n  description: 'thunderstorm with rain',\n  icon: '11d'\n}, {\n  id: '202',\n  description: 'thunderstorm with heavy rain',\n  icon: '11d'\n}, {\n  id: '210',\n  description: 'light thunderstorm',\n  icon: '11d'\n}, {\n  id: '211',\n  description: 'thunderstorm',\n  icon: '11d'\n}, {\n  id: '212',\n  description: 'heavy thunderstorm',\n  icon: '11d'\n}, {\n  id: '221',\n  description: 'ragged thunderstorm',\n  icon: '11d'\n}, {\n  id: '230',\n  description: 'thunderstorm with light drizzle',\n  icon: '11d'\n}, {\n  id: '231',\n  description: 'thunderstorm with drizzle',\n  icon: '11d'\n}, {\n  id: '232',\n  description: 'thunderstorm with heavy drizzle',\n  icon: '11d'\n}, {\n  id: '300',\n  description: 'light intensity drizzle',\n  icon: '09d'\n}, {\n  id: '301',\n  description: 'drizzle',\n  icon: '09d'\n}, {\n  id: '302',\n  description: 'heavy intensity drizzle',\n  icon: '09d'\n}, {\n  id: '310',\n  description: 'light intensity drizzle rain',\n  icon: '09d'\n}, {\n  id: '311',\n  description: 'drizzle rain',\n  icon: '09d'\n}, {\n  id: '312',\n  description: 'heavy intensity drizzle rain',\n  icon: '09d'\n}, {\n  id: '313',\n  description: 'shower rain and drizzle',\n  icon: '09d'\n}, {\n  id: '314',\n  description: 'heavy shower rain and drizzle',\n  icon: '09d'\n}, {\n  id: '321',\n  description: 'shower drizzle',\n  icon: '09d'\n}, {\n  id: '500',\n  description: 'light rain',\n  icon: '10d'\n}, {\n  id: '501',\n  description: 'moderate rain',\n  icon: '10d'\n}, {\n  id: '502',\n  description: 'heavy intensity rain',\n  icon: '10d'\n}, {\n  id: '503',\n  description: 'very heavy rain',\n  icon: '10d'\n}, {\n  id: '504',\n  description: 'extreme rain',\n  icon: '10d'\n}, {\n  id: '511',\n  description: 'freezing rain',\n  icon: '13d'\n}, {\n  id: '520',\n  description: 'light intensity shower rain',\n  icon: '09d'\n}, {\n  id: '521',\n  description: 'shower rain',\n  icon: '09d'\n}, {\n  id: '522',\n  description: 'heavy intensity shower rain',\n  icon: '09d'\n}, {\n  id: '531',\n  description: 'ragged shower rain',\n  icon: '09d'\n}, {\n  id: '600',\n  description: 'light snow',\n  icon: '13d'\n}, {\n  id: '601',\n  description: 'snow',\n  icon: '13d'\n}, {\n  id: '602',\n  description: 'heavy snow',\n  icon: '13d'\n}, {\n  id: '611',\n  description: 'sleet',\n  icon: '13d'\n}, {\n  id: '612',\n  description: 'shower sleet',\n  icon: '13d'\n}, {\n  id: '615',\n  description: 'light rain and snow',\n  icon: '13d'\n}, {\n  id: '616',\n  description: 'rain and snow',\n  icon: '13d'\n}, {\n  id: '620',\n  description: 'light shower snow',\n  icon: '13d'\n}, {\n  id: '621',\n  description: 'shower snow',\n  icon: '13d'\n}, {\n  id: '622',\n  description: 'heavy shower snow',\n  icon: '13d'\n}, {\n  id: '701',\n  description: 'mist',\n  icon: '50d'\n}, {\n  id: '711',\n  description: 'smoke',\n  icon: '50d'\n}, {\n  id: '721',\n  description: 'haze',\n  icon: '50d'\n}, {\n  id: '731',\n  description: 'sand, dust whirls',\n  icon: '50d'\n}, {\n  id: '741',\n  description: 'fog',\n  icon: '50d'\n}, {\n  id: '751',\n  description: 'sand',\n  icon: '50d'\n}, {\n  id: '761',\n  description: 'dust',\n  icon: '50d'\n}, {\n  id: '762',\n  description: 'volcanic ash',\n  icon: '50d'\n}, {\n  id: '771',\n  description: 'squalls',\n  icon: '50d'\n}, {\n  id: '781',\n  description: 'tornado',\n  icon: '50d'\n}, {\n  id: '800',\n  description: 'clear sky',\n  icon: ['01d', '01n']\n}, {\n  id: '801',\n  description: 'few clouds',\n  icon: ['02d', '02n']\n}, {\n  id: '802',\n  description: 'scattered clouds',\n  icon: ['03d', '03n']\n}, {\n  id: '803',\n  description: 'broken clouds',\n  icon: ['04d', '04n']\n}, {\n  id: '804',\n  description: 'overcast clouds',\n  icon: ['04d', '04n']\n}];\n\nfunction apicall(url, appId, location, done) {\n  var requestUrl = url + '&q=' + encodeURIComponent(location) + '&appid=' + encodeURIComponent(appId);\n  return axios__WEBPACK_IMPORTED_MODULE_0___default.a.get(requestUrl).then(function (res) {\n    var cod = res.data.cod ? Number(res.data.cod) : 200;\n\n    if (cod >= 400 && res.data.message) {\n      throw new Error(res.data.message);\n    } else {\n      if (done) done(res.data);\n      return res.data;\n    }\n  }).catch(function (res) {\n    console.error(res);\n    throw new Error(res.data.message);\n  });\n}\n\nfunction getWeather(appId, location, done) {\n  return apicall(OPEN_WEATHER_MAP_WEATHER_URL, appId, location, done);\n}\nfunction getWeatherForecast(appId, location, done) {\n  return apicall(OPEN_WEATHER_MAP_FORECAST_URL, appId, location, done);\n}\n\n//# sourceURL=webpack:///./src/openweathermap.js?");

/***/ }),

/***/ "dll-reference vendor_lib":
/*!*****************************!*\
  !*** external "vendor_lib" ***!
  \*****************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("module.exports = vendor_lib;\n\n//# sourceURL=webpack:///external_%22vendor_lib%22?");

/***/ }),

/***/ "ething-quasar-core":
/*!***************************!*\
  !*** external "EThingUI" ***!
  \***************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("module.exports = __WEBPACK_EXTERNAL_MODULE_ething_quasar_core__;\n\n//# sourceURL=webpack:///external_%22EThingUI%22?");

/***/ })

/******/ });
});