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

/***/ "./src/components/WOpenWeatherMapDevice.js":
/*!*************************************************!*\
  !*** ./src/components/WOpenWeatherMapDevice.js ***!
  \*************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var ething_quasar_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ething-quasar-core */ \"ething-quasar-core\");\n/* harmony import */ var ething_quasar_core__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(ething_quasar_core__WEBPACK_IMPORTED_MODULE_0__);\n\nvar WDeviceMultiLabel = ething_quasar_core__WEBPACK_IMPORTED_MODULE_0___default.a.widgets.WDeviceMultiLabel;\nvar iconPath = 'http://openweathermap.org/img/w';\nvar iconExt = 'png';\nvar weatherMap = [{\n  id: '200',\n  description: 'thunderstorm with light rain',\n  icon: '11d'\n}, {\n  id: '201',\n  description: 'thunderstorm with rain',\n  icon: '11d'\n}, {\n  id: '202',\n  description: 'thunderstorm with heavy rain',\n  icon: '11d'\n}, {\n  id: '210',\n  description: 'light thunderstorm',\n  icon: '11d'\n}, {\n  id: '211',\n  description: 'thunderstorm',\n  icon: '11d'\n}, {\n  id: '212',\n  description: 'heavy thunderstorm',\n  icon: '11d'\n}, {\n  id: '221',\n  description: 'ragged thunderstorm',\n  icon: '11d'\n}, {\n  id: '230',\n  description: 'thunderstorm with light drizzle',\n  icon: '11d'\n}, {\n  id: '231',\n  description: 'thunderstorm with drizzle',\n  icon: '11d'\n}, {\n  id: '232',\n  description: 'thunderstorm with heavy drizzle',\n  icon: '11d'\n}, {\n  id: '300',\n  description: 'light intensity drizzle',\n  icon: '09d'\n}, {\n  id: '301',\n  description: 'drizzle',\n  icon: '09d'\n}, {\n  id: '302',\n  description: 'heavy intensity drizzle',\n  icon: '09d'\n}, {\n  id: '310',\n  description: 'light intensity drizzle rain',\n  icon: '09d'\n}, {\n  id: '311',\n  description: 'drizzle rain',\n  icon: '09d'\n}, {\n  id: '312',\n  description: 'heavy intensity drizzle rain',\n  icon: '09d'\n}, {\n  id: '313',\n  description: 'shower rain and drizzle',\n  icon: '09d'\n}, {\n  id: '314',\n  description: 'heavy shower rain and drizzle',\n  icon: '09d'\n}, {\n  id: '321',\n  description: 'shower drizzle',\n  icon: '09d'\n}, {\n  id: '500',\n  description: 'light rain',\n  icon: '10d'\n}, {\n  id: '501',\n  description: 'moderate rain',\n  icon: '10d'\n}, {\n  id: '502',\n  description: 'heavy intensity rain',\n  icon: '10d'\n}, {\n  id: '503',\n  description: 'very heavy rain',\n  icon: '10d'\n}, {\n  id: '504',\n  description: 'extreme rain',\n  icon: '10d'\n}, {\n  id: '511',\n  description: 'freezing rain',\n  icon: '13d'\n}, {\n  id: '520',\n  description: 'light intensity shower rain',\n  icon: '09d'\n}, {\n  id: '521',\n  description: 'shower rain',\n  icon: '09d'\n}, {\n  id: '522',\n  description: 'heavy intensity shower rain',\n  icon: '09d'\n}, {\n  id: '531',\n  description: 'ragged shower rain',\n  icon: '09d'\n}, {\n  id: '600',\n  description: 'light snow',\n  icon: '13d'\n}, {\n  id: '601',\n  description: 'snow',\n  icon: '13d'\n}, {\n  id: '602',\n  description: 'heavy snow',\n  icon: '13d'\n}, {\n  id: '611',\n  description: 'sleet',\n  icon: '13d'\n}, {\n  id: '612',\n  description: 'shower sleet',\n  icon: '13d'\n}, {\n  id: '615',\n  description: 'light rain and snow',\n  icon: '13d'\n}, {\n  id: '616',\n  description: 'rain and snow',\n  icon: '13d'\n}, {\n  id: '620',\n  description: 'light shower snow',\n  icon: '13d'\n}, {\n  id: '621',\n  description: 'shower snow',\n  icon: '13d'\n}, {\n  id: '622',\n  description: 'heavy shower snow',\n  icon: '13d'\n}, {\n  id: '701',\n  description: 'mist',\n  icon: '50d'\n}, {\n  id: '711',\n  description: 'smoke',\n  icon: '50d'\n}, {\n  id: '721',\n  description: 'haze',\n  icon: '50d'\n}, {\n  id: '731',\n  description: 'sand, dust whirls',\n  icon: '50d'\n}, {\n  id: '741',\n  description: 'fog',\n  icon: '50d'\n}, {\n  id: '751',\n  description: 'sand',\n  icon: '50d'\n}, {\n  id: '761',\n  description: 'dust',\n  icon: '50d'\n}, {\n  id: '762',\n  description: 'volcanic ash',\n  icon: '50d'\n}, {\n  id: '771',\n  description: 'squalls',\n  icon: '50d'\n}, {\n  id: '781',\n  description: 'tornado',\n  icon: '50d'\n}, {\n  id: '800',\n  description: 'clear sky',\n  icon: ['01d', '01n']\n}, {\n  id: '801',\n  description: 'few clouds',\n  icon: ['02d', '02n']\n}, {\n  id: '802',\n  description: 'scattered clouds',\n  icon: ['03d', '03n']\n}, {\n  id: '803',\n  description: 'broken clouds',\n  icon: ['04d', '04n']\n}, {\n  id: '804',\n  description: 'overcast clouds',\n  icon: ['04d', '04n']\n}];\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  name: 'WOpenWeatherMapDevice',\n  extends: WDeviceMultiLabel,\n  metadata: {\n    label: 'default widget',\n    description: 'display the current weather informations',\n    minHeight: 250\n  },\n  props: {\n    items: {\n      default: function _default() {\n        return [{\n          label: 'temperature',\n          unit: '°C',\n          attr: 'temperature'\n        }, {\n          label: 'humidity',\n          unit: '%',\n          attr: 'humidity'\n        }, {\n          label: 'pressure',\n          unit: 'Pa',\n          attr: 'pressure'\n        }, {\n          label: 'weather',\n          attr: 'weather',\n          done: function done() {\n            for (var i in weatherMap) {\n              if (this.value === weatherMap[i].description) {\n                if (weatherMap[i].icon) {\n                  var icon;\n\n                  if (Array.isArray(weatherMap[i].icon)) {\n                    var now = new Date();\n                    var hours = now.getHours();\n                    var index = hours >= 21 ? 1 : 0;\n                    icon = weatherMap[i].icon[index];\n                  } else {\n                    icon = weatherMap[i].icon;\n                  }\n\n                  this.icon = true;\n                  this.value = iconPath + '/' + icon + '.' + iconExt;\n                }\n\n                return;\n              }\n            }\n          }\n        }, {\n          label: 'wind speed',\n          attr: 'wind_speed',\n          unit: 'm/s'\n        }, {\n          label: 'wind direction',\n          attr: 'wind_direction',\n          skipIfNull: true,\n          map: [{\n            key: 0,\n            value: 'N'\n          }, {\n            key: 45,\n            value: 'N-E'\n          }, {\n            key: 90,\n            value: 'E'\n          }, {\n            key: 135,\n            value: 'S-E'\n          }, {\n            key: 180,\n            value: 'S'\n          }, {\n            key: 225,\n            value: 'S-O'\n          }, {\n            key: 270,\n            value: 'O'\n          }, {\n            key: 315,\n            value: 'N-O'\n          }]\n        }];\n      }\n    }\n  }\n});\n\n//# sourceURL=webpack:///./src/components/WOpenWeatherMapDevice.js?");

/***/ }),

/***/ "./src/index.js":
/*!**********************!*\
  !*** ./src/index.js ***!
  \**********************/
/*! no exports provided */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _components_WOpenWeatherMapDevice__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./components/WOpenWeatherMapDevice */ \"./src/components/WOpenWeatherMapDevice.js\");\n/* harmony import */ var ething_quasar_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ething-quasar-core */ \"ething-quasar-core\");\n/* harmony import */ var ething_quasar_core__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(ething_quasar_core__WEBPACK_IMPORTED_MODULE_1__);\n\n\nconsole.log('loading plugin OpenWeatherMap...');\nething_quasar_core__WEBPACK_IMPORTED_MODULE_1___default.a.registerWidget(_components_WOpenWeatherMapDevice__WEBPACK_IMPORTED_MODULE_0__[\"default\"]);\nething_quasar_core__WEBPACK_IMPORTED_MODULE_1___default.a.extend('resources/OpenWeatherMapDevice', {\n  icon: 'mdi-weather-partlycloudy',\n  widgets: {\n    'default': 'WOpenWeatherMapDevice'\n  }\n});\n\n//# sourceURL=webpack:///./src/index.js?");

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