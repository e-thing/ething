(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[6],{"/7Pc":function(t,e,s){},N2R4:function(t,e,s){"use strict";var n=s("OMuZ"),a=s.n(n);a.a},OMuZ:function(t,e,s){},rmVo:function(t,e,s){"use strict";var n=s("s3X/"),a=s.n(n);a.a},rup0:function(t,e,s){"use strict";var n=s("/7Pc"),a=s.n(n);a.a},"s3X/":function(t,e,s){},tB8M:function(t,e,s){"use strict";s.r(e);var n=function(){var t=this,e=t.$createElement,s=t._self._c||e;return s("q-page",[s("q-tabs",{attrs:{"two-lines":"","no-pane-border":"",color:"secondary"}},[s("q-tab",{attrs:{slot:"title",default:"",label:"settings",name:"settings",icon:"settings"},slot:"title"}),s("q-tab",{attrs:{slot:"title",label:"log",name:"log",icon:"message"},slot:"title"}),s("q-tab",{attrs:{slot:"title",label:"about",name:"about",icon:"info"},slot:"title"}),s("q-tab-pane",{attrs:{name:"settings"}},[s("settings-view")],1),s("q-tab-pane",{attrs:{name:"log"}},[s("log-view")],1),s("q-tab-pane",{attrs:{name:"about"}},[s("dl",{staticClass:"horizontal"},[s("dt",[t._v("UI")]),s("dd",[t._v("version: "+t._s(t.$ui.VERSION))]),s("dt",[t._v("Server")]),s("dd",[t._v("version: "+t._s(t.$meta.info.VERSION))]),s("dt",[t._v("JS api")]),s("dd",[t._v("version: "+t._s(t.$ething.VERSION))]),s("dt",[t._v("Python")]),s("dd",[t._v("version: "+t._s(t.$meta.info.python.version)+" type: "+t._s(t.$meta.info.python.type))]),s("dt",[t._v("Platform")]),s("dd",[t._v(t._s(t.$meta.info.platform.name))]),s("dt",[t._v("NodeJS")]),s("dd",[t._v("version: "+t._s(t.$meta.info.nodejs.version))]),s("dt",[t._v("Plugins")]),s("dd",[t._v(t._s(t.plugins))])])])],1)],1)},a=[];n._withStripped=!0;s("rGqo"),s("yt8O"),s("RW0V");var i=function(){var t=this,e=t.$createElement,s=t._self._c||e;return!1===t.loading?s("div",[s("div",{staticClass:"q-mt-xl"},[s("div",{staticClass:"q-title q-title-opacity"},[t._v("General")]),s("form-schema",{staticClass:"q-my-md",attrs:{schema:t.$meta.config},on:{error:function(e){t.error=e}},model:{value:t.settings,callback:function(e){t.settings=e},expression:"settings"}})],1),t._l(t.plugins,function(e,n){return"object"===typeof e.schema?s("div",{key:n,staticClass:"q-mt-xl"},[s("div",{staticClass:"q-title q-title-opacity"},[t._v(t._s(n))]),s("form-schema",{staticClass:"q-my-md",attrs:{schema:e.schema},on:{error:function(t){e.error=t}},model:{value:t.settings[n],callback:function(e){t.$set(t.settings,n,e)},expression:"settings[name]"}})],1):t._e()}),t.saveError?s("q-alert",{staticClass:"q-mt-xl",attrs:{type:"negative"}},[t._v("\n    "+t._s(String(t.saveError))+"\n  ")]):t._e(),s("div",{staticClass:"q-mt-xl"},[s("q-btn",{attrs:{disable:t.globalError,loading:t.saving,color:"secondary",icon:"done",label:"save changes"},on:{click:t.onSave}})],1)],2):s("div",[t._v("loading ...")])},l=[];i._withStripped=!0;s("f3/d");var o={name:"SettingsView",data:function(){var t={};for(var e in this.$meta.plugins){var s=this.$meta.plugins[e];s.schema&&(t[e]={error:!1,schema:s.schema})}return{loading:!0,saving:!1,error:!1,saveError:!1,settings:{},plugins:t,logLevels:[{label:"debug",value:"debug"},{label:"info",value:"info"},{label:"warning",value:"warning"},{label:"error",value:"error"},{label:"fatal",value:"fatal"}]}},computed:{globalError:function(){var t=this.error;if(!t)for(var e in this.plugins){this.plugins[e].error&&(t=!0);break}return t}},methods:{load:function(){var t=this;this.loading=!0,this.$ething.settings.get().then(function(e){for(var s in console.log(e),t.plugins)"undefined"==typeof e[s]&&(e[s]={});t.settings=e,t.loading=!1})},onSave:function(){var t=this,e=this.settings;console.log(e),this.saving=!0,this.saveError=!1,this.$ething.settings.set(e).catch(function(e){t.saveError=e}).finally(function(){t.saving=!1})}},mounted:function(){this.load()}},r=o,c=(s("rup0"),s("KHd+")),d=Object(c["a"])(r,i,l,!1,null,"21f63b98",null),u=d.exports,g=function(){var t=this,e=t.$createElement,s=t._self._c||e;return!1===t.loading?s("div",[s("q-input",{staticClass:"inline",attrs:{placeholder:"filter"},model:{value:t.filter,callback:function(e){t.filter=e},expression:"filter"}}),s("q-select",{staticClass:"inline",attrs:{options:t.lengthOptions,suffix:"results"},model:{value:t.length,callback:function(e){t.length=e},expression:"length"}}),s("q-btn",{attrs:{color:"primary",flat:"",icon:"refresh",label:"refresh"},on:{click:t.load}}),s("div",{staticClass:"column gutter-y-xs q-mt-sm"},t._l(t.logs,function(e,n){return s("div",{staticClass:"log row gutter-x-xs",class:e.cls,attrs:{keys:n}},[s("div",{staticClass:"date col-md-auto col-sm-4 text-faded"},[t._v("\n        "+t._s(e.date)+"\n      ")]),s("div",{staticClass:"level col-md-1 col-sm-4 text-faded"},[t._v("\n        "+t._s(e.level)+"\n      ")]),s("div",{staticClass:"level col-md-2 col-sm-4 text-faded"},[t._v("\n        "+t._s(e.name)+"\n      ")]),s("div",{staticClass:"message col-md col-sm-12"},[t._v("\n        "+t._s(e.message)+"\n      ")])])}))],1):s("div",[t._v("loading ...")])},v=[];g._withStripped=!0;s("KKXr");var f={name:"LogView",data:function(){return{loading:!0,logs:[],filter:"",length:100,lengthOptions:[100,200,500,1e3].map(function(t){return{label:String(t),value:t}})}},methods:{load:function(){var t=this;this.loading=!0,this.$ething.request({url:"utils/read_log?line="+this.length+"&filter="+encodeURIComponent(this.filter),dataType:"json"}).then(function(e){t.logs=[],e.forEach(function(e){var s=e.split("::",4);if(4==s.length){var n=s[0].trim(),a=s[1].trim(),i=s[2].trim().toUpperCase(),l=s[3].trim();t.logs.push({date:n,name:a,level:i,cls:i.toLowerCase(),message:l})}else t.logs.length&&(t.logs[t.logs.length-1].message+="\n"+e)}),t.logs.reverse()}).finally(function(){t.loading=!1})}},mounted:function(){this.load()}},m=f,h=(s("N2R4"),Object(c["a"])(m,g,v,!1,null,"36cfc66b",null)),p=h.exports,_={name:"PageSettings",components:{SettingsView:u,LogView:p},data:function(){return{plugins:Object.keys(this.$meta.plugins).join(", ")}}},b=_,q=(s("rmVo"),Object(c["a"])(b,n,a,!1,null,null,null));e["default"]=q.exports}}]);