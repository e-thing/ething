webpackJsonp([10],{A1YC:function(n,t,e){(n.exports=e("FZ+f")(!1)).push([n.i,"\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",""])},FBn6:function(n,t,e){var o=e("A1YC");"string"==typeof o&&(o=[[n.i,o,""]]),o.locals&&(n.exports=o.locals);(0,e("rjj0").default)("60c6804b",o,!1,{})},d04G:function(n,t,e){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var o=function(){var n=this,t=n.$createElement,e=n._self._c||t;return e("q-page",{attrs:{padding:""}},[e("div",{staticClass:"row"},[e("div",{staticClass:"col-6"},[e("form-schema",{attrs:{schema:n.schema},on:{error:function(t){n.error=t}},model:{value:n.model,callback:function(t){n.model=t},expression:"model"}})],1),n._v(" "),e("div",{staticClass:"col-6"},[e("pre",[n._v(n._s(n.model))]),n._v(" "),n.error?e("div",[n._v("error")]):e("div",[n._v("ok")])])])])},r=[];o._withStripped=!0;var s=e("XyMi"),i=!1;var a=function(n){i||e("FBn6")},p=Object(s.a)({name:"PageTest",data:function(){return{error:!1,schema:{type:"object",properties:{host:{description:"une description",type:"string",pattern:"^toto"},anything:{},array:{type:"array",items:{}},isOk:{type:"boolean"},count:{type:"number",default:42,minimum:40},color:{type:"string",format:"color"},date:{type:"string",format:"date-time"},optional:{description:"une description",anyOf:[{type:"null"},{type:"string"}]},json:{type:"json"},object:{type:"object",required:["host"],properties:{host:{type:"string"},isOk:{type:"boolean"},count:{type:"number"},object:{type:"object",required:["host"],properties:{host:{type:"string"},isOk:{type:"boolean"}}}}}}},model:{host:"toto",isOk:!1,json:"{}",array:[4,5],optional:"tyty"}}}},o,r,!1,a,null,null);p.options.__file="src\\pages\\Test.vue";t.default=p.exports}});