webpackJsonp([15],{lfHO:function(t,n,e){"use strict";Object.defineProperty(n,"__esModule",{value:!0});var a={name:"LayoutDefault",data:function(){return{leftDrawerOpen:!1}},computed:{back:function(){return this.$route.meta.back&&(this.$q.platform.within.iframe||this.$q.platform.is.electron||this.$ui.kioskMode)}},methods:{logout:function(){this.$ui.logout()},reload:function(){this.$root.state="begin",this.$router.go(this.$router.currentRoute)},refresher:function(t){console.log("refresh"),this.$router.go(),t()}}},i=function(){var t=this,n=t.$createElement,e=t._self._c||n;return e("q-layout",{attrs:{view:"hHh Lpr lFf"}},[e("q-layout-header",[e("q-toolbar",{attrs:{color:"primary"}},[e("q-btn",{staticClass:"xs",attrs:{flat:"",round:"",dense:"",icon:"menu","aria-label":"Toggle menu on left side"},on:{click:function(n){t.leftDrawerOpen=!t.leftDrawerOpen}}}),t._v(" "),t.back?e("q-btn",{attrs:{flat:"",round:"",dense:"",icon:"keyboard_backspace","aria-label":"back"},on:{click:function(n){t.$router.go(-1)}}}):t._e(),t._v(" "),e("q-toolbar-title",{attrs:{shrink:""}},[t._v("\n        EThing\n      ")]),t._v(" "),e("q-btn",{staticClass:"gt-xs",attrs:{flat:"",label:"Dashboard"},on:{click:function(n){t.$router.push("/dashboard")}}}),t._v(" "),e("q-btn",{staticClass:"gt-xs",attrs:{flat:"",label:"Devices"},on:{click:function(n){t.$router.push("/devices")}}}),t._v(" "),e("q-btn",{staticClass:"gt-xs",attrs:{flat:"",label:"Data"},on:{click:function(n){t.$router.push("/data")}}}),t._v(" "),e("q-btn",{staticClass:"gt-xs",attrs:{flat:"",label:"Rules"},on:{click:function(n){t.$router.push("/rules")}}}),t._v(" "),e("q-toolbar-title",{staticClass:"gt-xs"}),t._v(" "),e("q-btn",{staticClass:"gt-xs",attrs:{flat:"",dense:"",icon:"settings","aria-label":"settings"},on:{click:function(n){t.$router.push("/settings")}}}),t._v(" "),t.$ui.autoLogin?t._e():e("q-btn",{staticClass:"gt-xs",attrs:{flat:"",dense:"",icon:"exit to app","aria-label":"logout"},on:{click:t.logout}})],1)],1),t._v(" "),e("q-layout-drawer",{attrs:{"content-class":"mat"===t.$q.theme?"bg-grey-2":null},model:{value:t.leftDrawerOpen,callback:function(n){t.leftDrawerOpen=n},expression:"leftDrawerOpen"}},[e("q-list",{attrs:{"no-border":"",link:"","inset-delimiter":""}},[e("q-list-header",[t._v("Menu")]),t._v(" "),e("q-item",{nativeOn:{click:function(n){t.$router.push("/dashboard")}}},[e("q-item-side",{attrs:{icon:"dashboard"}}),t._v(" "),e("q-item-main",{attrs:{label:"Dashboard"}})],1),t._v(" "),e("q-item",{nativeOn:{click:function(n){t.$router.push("/devices")}}},[e("q-item-side",{attrs:{icon:"devices"}}),t._v(" "),e("q-item-main",{attrs:{label:"Devices"}})],1),t._v(" "),e("q-item",{nativeOn:{click:function(n){t.$router.push("/data")}}},[e("q-item-side",{attrs:{icon:"mdi-database"}}),t._v(" "),e("q-item-main",{attrs:{label:"Data"}})],1),t._v(" "),e("q-item",{nativeOn:{click:function(n){t.$router.push("/rules")}}},[e("q-item-side",{attrs:{icon:"event"}}),t._v(" "),e("q-item-main",{attrs:{label:"Rules"}})],1),t._v(" "),e("q-item-separator"),t._v(" "),e("q-item",{nativeOn:{click:function(n){t.$router.push("/settings")}}},[e("q-item-side",{attrs:{icon:"settings"}}),t._v(" "),e("q-item-main",{attrs:{label:"Settings"}})],1),t._v(" "),t.$ui.autoLogin?t._e():e("q-item",{nativeOn:{click:function(n){return t.logout(n)}}},[e("q-item-side",{attrs:{icon:"exit to app"}}),t._v(" "),e("q-item-main",{attrs:{label:"Logout"}})],1)],1)],1),t._v(" "),e("q-page-container",["ok"!==t.$root.state?e("q-inner-loading",{staticClass:"text-center",attrs:{visible:""}},["error"===t.$root.state?e("div",[e("div",{staticClass:"q-pa-lg text-negative"},[t._v("\n          "+t._s(String(t.$root.error))+"\n        ")]),t._v(" "),e("q-btn",{attrs:{color:"negative",icon:"refresh",label:"Reload"},on:{click:t.reload}})],1):e("div",[e("div",{staticClass:"q-pa-lg text-primary"},[t._v("loading...")]),t._v(" "),e("q-spinner-pie",{attrs:{color:"primary",size:"50px"}})],1)]):e("keep-alive",{attrs:{include:"PageDashboard,PageDevices,PageData"}},[e("q-pull-to-refresh",{attrs:{handler:t.refresher}},[e("router-view")],1)],1)],1)],1)},r=[];i._withStripped=!0;var s=e("XyMi"),o=!1;var l=function(t){o||e("xwNl")},c=Object(s.a)(a,i,r,!1,l,null,null);c.options.__file="src\\layouts\\default.vue";n.default=c.exports},smEj:function(t,n,e){(t.exports=e("FZ+f")(!1)).push([t.i,"\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",""])},xwNl:function(t,n,e){var a=e("smEj");"string"==typeof a&&(a=[[t.i,a,""]]),a.locals&&(t.exports=a.locals);(0,e("rjj0").default)("2fd6de1e",a,!1,{})}});