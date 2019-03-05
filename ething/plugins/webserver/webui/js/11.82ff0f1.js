(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[11],{"GA/o":function(t,e,s){"use strict";s.r(e);var i=function(){var t=this,e=t.$createElement,s=t._self._c||e;return s("q-page",{staticClass:"bg-grey-2"},[s("div",{staticClass:"bg-white q-py-lg q-px-lg",staticStyle:{"border-bottom":"5px solid #eee"}},[s("div",{staticClass:"q-my-md q-display-1 q-display-1-opacity"},[s("q-icon",{staticClass:"vertical-middle",attrs:{name:t.$ethingUI.get(t.resource).icon}}),s("span",{staticClass:"vertical-middle"},[t._v("\n        "+t._s(t.resource.basename())+"\n      ")]),s("q-btn",{staticClass:"float-right",attrs:{flat:"",dense:t.$q.screen.lt.sm,label:"settings",icon:"settings"},on:{click:function(e){t.$router.push("/resource/"+t.resource.id())}}})],1),s("div",[t.resource.lastSeenDate()?s("q-chip",{staticClass:"q-mr-sm",attrs:{small:"",square:"",detail:"",icon:"access time"}},[t._v("\n        "+t._s(t.$ethingUI.utils.dateToString(t.resource.lastSeenDate()))+"\n      ")]):t._e(),s("resource-battery-chip",{staticClass:"vertical-middle q-mr-sm",attrs:{resource:t.resource,square:""}}),t.resource.location()?s("q-chip",{staticClass:"q-mr-sm",attrs:{small:"",square:"",detail:"",icon:"location_on"}},[t._v("\n        "+t._s(t.resource.location())+"\n      ")]):t._e()],1),t.createdBys.length?s("div",{staticClass:"q-py-md"},[t._l(t.createdBys,function(e,i){return[i>0?s("span",[t._v(" - ")]):t._e(),s("span",{staticClass:"createdby-item",on:{click:function(s){t.$ethingUI.open(e)}}},[t._v(t._s(e.basename()))])]})],2):t._e()]),s("div",{staticClass:"q-px-lg q-pb-md"},[t._l(t.$ethingUI.get(t.resource)._mro,function(e){return t.$ethingUI.get(e).mainComponent?s("div",{key:e,staticClass:"bloc"},[s("div",{staticClass:"bloc-title"},[s("q-icon",{attrs:{name:t.$ethingUI.get(e).icon}}),s("span",[t._v(t._s(t.$ethingUI.get(e).title))])],1),s("device-component",{staticClass:"bloc-content",attrs:{device:t.resource,component:t.$ethingUI.get(e).mainComponent,componentAttr:t.$ethingUI.get(e).mainComponentAttributes}})],1):t._e()}),t.attributes.length>0?s("div",{staticClass:"bloc attributes",class:{detailled:t.showDetailledAttributes}},[s("div",{staticClass:"bloc-title"},[s("q-icon",{attrs:{name:"mdi-format-list-bulleted"}}),s("span",[t._v("Attributes")]),s("q-btn",{staticClass:"float-right",staticStyle:{"line-height":"initial"},attrs:{flat:"",rounded:"",size:"small",label:t.showDetailledAttributes?"less":"more",icon:t.showDetailledAttributes?"expand_less":"expand_more"},on:{click:function(e){t.showDetailledAttributes=!t.showDetailledAttributes}}})],1),s("div",{staticClass:"bloc-content"},[s("div",{staticClass:"row"},[t._l(t.attributes,function(e){return[s("div",{staticClass:"col-xs-12 col-sm-2 key text-secondary ellipsis",class:{detailled:e.detailled}},[t._v(t._s(e.name))]),s("div",{staticClass:"col-xs-12 col-sm-10 value ellipsis",class:{detailled:e.detailled}},[t._v(t._s(e.value))])]})],2)])]):t._e(),t.data?s("div",{staticClass:"bloc"},[s("div",{staticClass:"bloc-title"},[s("q-icon",{attrs:{name:"mdi-format-list-bulleted"}}),s("span",[t._v("Data")])],1),s("div",{staticClass:"bloc-content"},[s("div",{staticClass:"row"},[t._l(t.data,function(e,i){return[s("div",{staticClass:"col-xs-12 col-sm-2 key text-secondary"},[t._v(t._s(i))]),s("div",{staticClass:"col-xs-12 col-sm-10 value"},[t._v(t._s(e))])]})],2)])]):t._e(),t.children.length?s("div",{staticClass:"bloc"},[s("div",{staticClass:"bloc-title"},[s("q-icon",{attrs:{name:"mdi-database"}}),s("span",[t._v("Resources")])],1),s("div",{staticClass:"bloc-content bloc-content-no-padding"},[s("q-list",{attrs:{"no-border":""}},t._l(t.children,function(t){return s("resource-q-item",{key:t.id(),attrs:{resource:t}})}))],1)]):t._e(),Object.keys(t.$ethingUI.get(t.resource).methods).length?s("div",{staticClass:"bloc"},[s("div",{staticClass:"bloc-title"},[s("q-icon",{attrs:{name:"mdi-database"}}),s("span",[t._v("API")])],1),s("div",{staticClass:"bloc-content bloc-content-no-padding"},[s("device-api",{attrs:{device:t.resource}})],1)]):t._e()],2)])},n=[];i._withStripped=!0;s("f3/d"),s("rGqo"),s("yt8O"),s("RW0V"),s("dRSK"),s("pIFo");var a=s("WZpT"),r=s("ZDT0"),c=s("V3Uy"),o=function(){var t=this,e=t.$createElement,s=t._self._c||e;return s("div",[t.isWidget?t._l(t.widgets,function(t,e){return[s("widget",{class:{"q-mt-md":e},attrs:{widgetClass:t.widgetClass,widgetOptions:t.widgetOptions}})]}):[s("div",{ref:"component"})]],2)},l=[];o._withStripped=!0;s("91GP");var d={name:"DeviceComponent",props:["device","component","componentAttr"],data:function(){return{isWidget:!1,instance:null,widgets:[],widgetClass:null,widgetOptions:null}},computed:{computedDevice:function(){return"string"==typeof this.device?this.$ething.arbo.get(this.device):this.device}},mounted:function(){var t=this;if(this.computedDevice){var e,s,i=this.$ethingUI.get(this.computedDevice);if(this.component?(e=this.component,s=this.componentAttr):(e=i.mainComponent,s=i.mainComponentAttributes),"string"==typeof e&&(e=[e],s=[s]),Array.isArray(e))e.forEach(function(e,n){var a=i.widgets[e];if(a){var r={resource:t.computedDevice.id()};s&&s[n]&&Object.assign(r,s[n]),t.widgets.push({widgetClass:a,widgetOptions:r})}else console.error('widget "'+e+'" not found for the resource '+t.computedDevice.id())}),this.isWidget=!!this.widgets.length;else if(e){this.$ethingUI.utils.isPlainObject(e)&&(e=Vue.extend(e));var n=new e({propsData:Object.assign({resource:this.computedDevice},s||{}),parent:this});n.$mount(this.$refs.component),this.instance=n}}},beforeDestroy:function(){this.instance&&this.instance.$destroy()}},u=d,p=s("KHd+"),v=Object(p["a"])(u,o,l,!1,null,null,null);v.options.__file="DeviceComponent.vue";var h=v.exports,m={name:"PageDevice",components:{DeviceApi:a["a"],ResourceQItem:r["a"],ResourceBatteryChip:c["a"],DeviceComponent:h},data:function(){return{showDetailledAttributes:!1}},computed:{resource:function(){var t=this.$route.params.id,e=this.$ething.arbo.get(t);return t&&t.length&&(e&&e.isTypeof("resources/Device")||this.$router.replace("/404")),e},children:function(){var t=this;return this.$ething.arbo.find(function(e){return e.createdBy()===t.resource.id()})},tables:function(){return this.children.filter(function(t){return t.isTypeof("resources/Table")})},files:function(){return this.children.filter(function(t){return t.isTypeof("resources/File")})},devices:function(){return this.children.filter(function(t){return t.isTypeof("resources/Device")})},data:function(){var t=this.resource.data();return t&&Object.keys(t).length>0?t:void 0},attributes:function(){var t=this.$ethingUI.get(this.resource).properties,e=[],s=["name","data","description"],i=["id","modifiedDate","createdBy","type","extends","public","createdDate","methods","battery","location","interfaces","connected","lastSeenDate"];for(var n in t)if(-1===s.indexOf(n)){var a=t[n],r=a.getFormatted(this.resource);e.push({name:n,value:r,detailled:-1!==i.indexOf(n)})}return e},createdBys:function(){var t=[],e=this.resource.createdBy();while(e){var s=this.$ething.arbo.get(e);if(!s)break;t.push(s),e=s.createdBy()}return t.reverse()}}},g=m,f=(s("Ra9x"),Object(p["a"])(g,i,n,!1,null,null,null));f.options.__file="Device.vue";e["default"]=f.exports},L8Rl:function(t,e,s){},Ra9x:function(t,e,s){"use strict";var i=s("L8Rl"),n=s.n(i);n.a}}]);