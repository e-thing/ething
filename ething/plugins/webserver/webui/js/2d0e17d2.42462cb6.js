(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["2d0e17d2"],{"7b3d":function(t,e,a){"use strict";a.r(e);var r=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("q-layout",{attrs:{view:"hHh Lpr lFf"}},[a("q-header",{attrs:{elevated:""}},[a("q-toolbar",{attrs:{color:"primary"}},[a("q-btn",{staticClass:"xs",attrs:{flat:"",round:"",dense:"",icon:"menu","aria-label":"Toggle menu on left side"},on:{click:function(e){t.leftDrawerOpen=!t.leftDrawerOpen}}}),t.back?a("q-btn",{attrs:{flat:"",round:"",dense:"",icon:"keyboard_backspace","aria-label":"back"},on:{click:function(e){return t.$router.go(-1)}}}):t._e(),a("q-toolbar-title",{attrs:{shrink:""}},[t._v("\n        EThing\n      ")]),a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",label:"Dashboard"},on:{click:function(e){return t.$router.push("/dashboard")}}}),a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",label:"Devices"},on:{click:function(e){return t.$router.push("/devices")}}}),a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",label:"Data"},on:{click:function(e){return t.$router.push("/data")}}}),a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",label:"Flows"},on:{click:function(e){return t.$router.push("/flows")}}}),a("q-toolbar-title",{staticClass:"gt-xs"}),t.refreshEnabled?a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",icon:"refresh","aria-label":"refresh"},on:{click:t.refresh}}):t._e(),a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",icon:"settings","aria-label":"Settings"},on:{click:function(e){return t.$router.push("/settings")}}}),t.$ethingUI.autoLogin?t._e():a("q-btn",{staticClass:"gt-xs",attrs:{flat:"",icon:"exit_to_app","aria-label":"Logout"},on:{click:t.logout}})],1)],1),a("q-drawer",{attrs:{bordered:"","content-class":"bg-grey-2"},model:{value:t.leftDrawerOpen,callback:function(e){t.leftDrawerOpen=e},expression:"leftDrawerOpen"}},[a("q-list",{attrs:{"inset-delimiter":""}},[a("q-item-label",{attrs:{header:""}},[t._v("Menu")]),a("q-item",{directives:[{name:"ripple",rawName:"v-ripple"}],attrs:{clickable:""},on:{click:function(e){return t.$router.push("/dashboard")}}},[a("q-item-section",{attrs:{avatar:""}},[a("q-icon",{attrs:{name:"dashboard"}})],1),a("q-item-section",[t._v("Dashboard")])],1),a("q-item",{directives:[{name:"ripple",rawName:"v-ripple"}],attrs:{clickable:""},on:{click:function(e){return t.$router.push("/devices")}}},[a("q-item-section",{attrs:{avatar:""}},[a("q-icon",{attrs:{name:"devices"}})],1),a("q-item-section",[t._v("Devices")])],1),a("q-item",{directives:[{name:"ripple",rawName:"v-ripple"}],attrs:{clickable:""},on:{click:function(e){return t.$router.push("/data")}}},[a("q-item-section",{attrs:{avatar:""}},[a("q-icon",{attrs:{name:"mdi-database"}})],1),a("q-item-section",[t._v("Data")])],1),a("q-item",{directives:[{name:"ripple",rawName:"v-ripple"}],attrs:{clickable:""},on:{click:function(e){return t.$router.push("/flows")}}},[a("q-item-section",{attrs:{avatar:""}},[a("q-icon",{attrs:{name:"mdi-ray-start-arrow"}})],1),a("q-item-section",[t._v("Flows")])],1),a("q-separator"),a("q-item",{directives:[{name:"ripple",rawName:"v-ripple"}],attrs:{clickable:""},on:{click:function(e){return t.$router.push("/settings")}}},[a("q-item-section",{attrs:{avatar:""}},[a("q-icon",{attrs:{name:"settings"}})],1),a("q-item-section",[t._v("Settings")])],1),t.$ethingUI.autoLogin?t._e():a("q-item",{directives:[{name:"ripple",rawName:"v-ripple"}],attrs:{clickable:""},on:{click:t.logout}},[a("q-item-section",{attrs:{avatar:""}},[a("q-icon",{attrs:{name:"exit_to_app"}})],1),a("q-item-section",[t._v("Logout")])],1)],1)],1),a("q-page-container",["ok"!==t.$root.state?a("q-inner-loading",{staticClass:"text-center",attrs:{showing:""}},["error"===t.$root.state?a("div",[a("div",{staticClass:"q-pa-lg text-negative"},[t._v("\n          "+t._s(String(t.$root.error))+"\n        ")]),a("q-btn",{attrs:{color:"negative",icon:"refresh",label:"Reload"},on:{click:t.reload}})],1):a("div",[a("div",{staticClass:"q-pa-lg text-primary"},[t._v("loading...")]),a("q-spinner-pie",{attrs:{color:"primary",size:"50px"}})],1)]):a("keep-alive",{attrs:{include:"PageDashboard,PageDevices,PageData"}},[a("router-view")],1),t.vKeyboardEnabled?a("v-keyboard"):t._e()],1)],1)},i=[],n={name:"LayoutDefault",data:function(){return{leftDrawerOpen:!1}},computed:{back:function(){return this.$route.meta.back&&(this.$q.platform.within.iframe||this.$q.platform.is.electron||this.$ethingUI.kioskMode)},refreshEnabled:function(){return this.$q.platform.has.touch&&(!this.$q.platform.is.desktop||this.$ethingUI.kioskMode)},vKeyboardEnabled:function(){return this.$ethingUI.virtualKeyboardEnabled}},methods:{logout:function(){var t=this;this.$q.dialog({title:"Logout ?",color:"primary",message:"Are you sure you want to logout ?",ok:"Logout",cancel:"Cancel"}).onOk(function(){t.$ethingUI.logout()})},reload:function(){this.$root.state="begin",this.$router.go(this.$router.currentRoute)},refresh:function(){this.$router.go()}}},s=n,o=a("2877"),l=Object(o["a"])(s,r,i,!1,null,null,null);e["default"]=l.exports}}]);