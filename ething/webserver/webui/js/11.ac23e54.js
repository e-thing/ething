(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[11],{"GA/o":function(t,e,s){"use strict";s.r(e);var a=function(){var t=this,e=t.$createElement,s=t._self._c||e;return s("q-page",{attrs:{padding:""}},[s("div",{staticClass:"q-my-md q-display-1 q-display-1-opacity"},[s("q-icon",{staticClass:"vertical-middle",attrs:{name:t.$ethingUI.get(t.resource).icon}}),s("span",{staticClass:"vertical-middle"},[t._v("\n      "+t._s(t.resource.basename())+"\n    ")]),t.resource.lastSeenDate()?s("q-chip",{staticClass:"q-ml-sm",attrs:{small:"",square:"",detail:"",icon:"access time"}},[t._v("\n      "+t._s(t.$ethingUI.utils.dateToString(t.resource.lastSeenDate()))+"\n    ")]):t._e(),s("resource-battery-chip",{staticClass:"vertical-middle q-ml-sm",attrs:{resource:t.resource,square:""}}),t.resource.location()?s("q-chip",{staticClass:"q-ml-sm",attrs:{small:"",square:"",detail:"",icon:"location_on"}},[t._v("\n      "+t._s(t.resource.location())+"\n    ")]):t._e(),s("q-btn",{staticClass:"float-right",attrs:{flat:"",label:"settings",icon:"settings"},on:{click:function(e){t.$router.push("/resource/"+t.resource.id())}}})],1),t.createdBys.length?s("q-breadcrumbs",{staticClass:"q-py-md"},[t._l(t.createdBys,function(e,a){return s("q-breadcrumbs-el",{key:a,attrs:{label:e.basename(),to:t.$ethingUI.route(e)}})}),s("q-breadcrumbs-el",{attrs:{label:""}})],2):t._e(),t.attributes.length>0?s("q-card",{staticClass:"q-my-md attributes",class:{detailled:t.showDetailledAttributes}},[s("q-card-title",{staticClass:"bg-primary text-white"},[s("q-icon",{staticClass:"vertical-middle",attrs:{name:"mdi-format-list-bulleted"}}),s("span",{staticClass:"vertical-middle"},[t._v("\n        Attributes\n      ")]),s("q-btn",{staticClass:"float-right",staticStyle:{"line-height":"initial"},attrs:{flat:"",rounded:"",size:"small",label:t.showDetailledAttributes?"less":"more",icon:t.showDetailledAttributes?"expand_less":"expand_more"},on:{click:function(e){t.showDetailledAttributes=!t.showDetailledAttributes}}})],1),s("q-card-separator"),s("q-card-main",[s("div",{staticClass:"row"},[t._l(t.attributes,function(e){return[s("div",{staticClass:"col-xs-12 col-sm-2 key text-secondary",class:{detailled:e.detailled}},[t._v(t._s(e.name))]),s("div",{staticClass:"col-xs-12 col-sm-10 value",class:{detailled:e.detailled}},[t._v(t._s(e.value))])]})],2)])],1):t._e(),t.data?s("q-card",{staticClass:"q-my-md"},[s("q-card-title",{staticClass:"bg-primary text-white"},[s("q-icon",{staticClass:"vertical-middle",attrs:{name:"mdi-format-list-bulleted"}}),s("span",{staticClass:"vertical-middle"},[t._v("\n        Data\n      ")])],1),s("q-card-separator"),s("q-card-main",[s("div",{staticClass:"row"},[t._l(t.data,function(e,a){return[s("div",{staticClass:"col-xs-12 col-sm-2 key text-secondary"},[t._v(t._s(a))]),s("div",{staticClass:"col-xs-12 col-sm-10 value"},[t._v(t._s(e))])]})],2)])],1):t._e(),t.children.length?s("q-card",{staticClass:"q-my-md"},[s("q-card-title",{staticClass:"bg-primary text-white"},[s("q-icon",{staticClass:"vertical-middle",attrs:{name:"mdi-database"}}),s("span",{staticClass:"vertical-middle"},[t._v("\n        Resources\n      ")])],1),s("q-card-separator"),s("q-card-main",[s("q-list",{attrs:{"no-border":""}},t._l(t.children,function(t){return s("resource-q-item",{key:t.id(),attrs:{resource:t}})}))],1)],1):t._e(),Object.keys(t.$ethingUI.get(t.resource).methods).length?s("q-card",{staticClass:"q-my-md"},[s("q-card-title",{staticClass:"bg-primary text-white"},[s("q-icon",{staticClass:"vertical-middle",attrs:{name:"mdi-database"}}),s("span",{staticClass:"vertical-middle"},[t._v("\n        API\n      ")])],1),s("q-card-separator"),s("q-card-main",[s("device-api",{attrs:{device:t.resource}})],1)],1):t._e()],1)},i=[];a._withStripped=!0;s("f3/d"),s("rGqo"),s("yt8O"),s("RW0V"),s("pIFo");var r=s("WZpT"),c=s("ZDT0"),l=s("V3Uy"),n=s("s4Jd"),d={name:"PageDevice",components:{DeviceApi:r["a"],ResourceQItem:c["a"],ResourceBatteryChip:l["a"],ResourceWidget:n["a"]},data:function(){return{showDetailledAttributes:!1}},computed:{resource:function(){var t=this.$route.params.id,e=this.$store.getters["ething/get"](t);return t&&t.length&&(e&&e.isTypeof("resources/Device")||this.$router.replace("/404")),e},children:function(){var t=this;return this.$store.getters["ething/filter"](function(e){return e.createdBy()===t.resource.id()})},tables:function(){return this.children.filter(function(t){return t.isTypeof("resources/Table")})},files:function(){return this.children.filter(function(t){return t.isTypeof("resources/File")})},devices:function(){return this.children.filter(function(t){return t.isTypeof("resources/Device")})},data:function(){var t=this.resource.data();return t&&Object.keys(t).length>0?t:void 0},attributes:function(){var t=this.$ethingUI.get(this.resource).properties,e=[],s=["name","data","description"],a=["id","modifiedDate","createdBy","type","extends","public","createdDate","methods","battery","location","interfaces","connected","lastSeenDate"];for(var i in t)if(-1===s.indexOf(i)){var r=t[i],c=r.getFormatted(this.resource);e.push({name:i,value:c,detailled:-1!==a.indexOf(i)})}return e},createdBys:function(){var t=[],e=this.resource.createdBy();while(e){var s=this.$ething.arbo.get(e);if(!s)break;t.push(s),e=s.createdBy()}return t.reverse()}}},o=d,u=(s("Ra9x"),s("KHd+")),m=Object(u["a"])(o,a,i,!1,null,null,null);m.options.__file="Device.vue";e["default"]=m.exports},L8Rl:function(t,e,s){},Ra9x:function(t,e,s){"use strict";var a=s("L8Rl"),i=s.n(a);i.a}}]);