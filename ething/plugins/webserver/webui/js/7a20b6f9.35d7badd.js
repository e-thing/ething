(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["7a20b6f9"],{"0ae9":function(t,e,a){},"7b3d":function(t,e,a){"use strict";a.r(e);var i=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("q-layout",{attrs:{view:"hHh Lpr lFf"}},[a("q-layout-header",[a("q-toolbar",{attrs:{color:"primary"}},[a("q-btn",{staticClass:"xs",attrs:{flat:"",round:"",dense:"",icon:"menu","aria-label":"Toggle menu on left side"},on:{click:function(e){t.leftDrawerOpen=!t.leftDrawerOpen}}}),t.back?a("q-btn",{attrs:{flat:"",round:"",dense:"",icon:"keyboard_backspace","aria-label":"back"},on:{click:function(e){t.$router.go(-1)}}}):t._e(),a("q-toolbar-title",{attrs:{shrink:""}},[t._v("\n        EThing\n      ")]),a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",label:"Dashboard"},on:{click:function(e){t.$router.push("/dashboard")}}}),a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",label:"Devices"},on:{click:function(e){t.$router.push("/devices")}}}),a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",label:"Data"},on:{click:function(e){t.$router.push("/data")}}}),a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",label:"Flows"},on:{click:function(e){t.$router.push("/flows")}}}),a("q-toolbar-title",{staticClass:"gt-xs"}),t.refreshEnabled?a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",icon:"refresh","aria-label":"refresh"},on:{click:t.refresh}}):t._e(),a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",icon:"settings","aria-label":"Settings"},on:{click:function(e){t.$router.push("/settings")}}}),t.$ethingUI.autoLogin?t._e():a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",icon:"exit to app","aria-label":"Logout"},on:{click:t.logout}})],1)],1),a("q-layout-drawer",{attrs:{"content-class":"mat"===t.$q.theme?"bg-grey-2":null},model:{value:t.leftDrawerOpen,callback:function(e){t.leftDrawerOpen=e},expression:"leftDrawerOpen"}},[a("q-list",{attrs:{"no-border":"",link:"","inset-delimiter":""}},[a("q-list-header",[t._v("Menu")]),a("q-item",{nativeOn:{click:function(e){t.$router.push("/dashboard")}}},[a("q-item-side",{attrs:{icon:"dashboard"}}),a("q-item-main",{attrs:{label:"Dashboard"}})],1),a("q-item",{nativeOn:{click:function(e){t.$router.push("/devices")}}},[a("q-item-side",{attrs:{icon:"devices"}}),a("q-item-main",{attrs:{label:"Devices"}})],1),a("q-item",{nativeOn:{click:function(e){t.$router.push("/data")}}},[a("q-item-side",{attrs:{icon:"mdi-database"}}),a("q-item-main",{attrs:{label:"Data"}})],1),a("q-item",{nativeOn:{click:function(e){t.$router.push("/flows")}}},[a("q-item-side",{attrs:{icon:"mdi-ray-start-arrow"}}),a("q-item-main",{attrs:{label:"Flows"}})],1),a("q-item-separator"),a("q-item",{nativeOn:{click:function(e){t.$router.push("/settings")}}},[a("q-item-side",{attrs:{icon:"settings"}}),a("q-item-main",{attrs:{label:"Settings"}})],1),t.$ethingUI.autoLogin?t._e():a("q-item",{nativeOn:{click:function(e){return t.logout(e)}}},[a("q-item-side",{attrs:{icon:"exit to app"}}),a("q-item-main",{attrs:{label:"Logout"}})],1)],1)],1),a("q-page-container",["ok"!==t.$root.state?a("q-inner-loading",{staticClass:"text-center",attrs:{visible:""}},["error"===t.$root.state?a("div",[a("div",{staticClass:"q-pa-lg text-negative"},[t._v("\n          "+t._s(String(t.$root.error))+"\n        ")]),a("q-btn",{attrs:{color:"negative",icon:"refresh",label:"Reload"},on:{click:t.reload}})],1):a("div",[a("div",{staticClass:"q-pa-lg text-primary"},[t._v("loading...")]),a("q-spinner-pie",{attrs:{color:"primary",size:"50px"}})],1)]):a("keep-alive",{attrs:{include:"PageDashboard,PageDevices,PageData"}},[a("router-view")],1),t.vKeyboardEnabled?a("v-keyboard"):t._e()],1)],1)},n=[];i._withStripped=!0;var r={name:"LayoutDefault",data:function(){return{leftDrawerOpen:!1}},computed:{back:function(){return this.$route.meta.back&&(this.$q.platform.within.iframe||this.$q.platform.is.electron||this.$ethingUI.kioskMode)},refreshEnabled:function(){return this.$q.platform.has.touch&&(!this.$q.platform.is.desktop||this.$ethingUI.kioskMode)},vKeyboardEnabled:function(){return this.$ethingUI.virtualKeyboardEnabled}},methods:{logout:function(){var t=this;this.$q.dialog({title:"Logout ?",color:"primary",message:"Are you sure you want to logout ?",ok:"Logout",cancel:"Cancel"}).then(function(){t.$ethingUI.logout()}).catch(function(){})},reload:function(){this.$root.state="begin",this.$router.go(this.$router.currentRoute)},refresh:function(){this.$router.go()}}},s=r,o=(a("f70f"),a("2877")),l=Object(o["a"])(s,i,n,!1,null,null,null);l.options.__file="default.vue";e["default"]=l.exports},f70f:function(t,e,a){"use strict";var i=a("0ae9"),n=a.n(i);n.a}}]);