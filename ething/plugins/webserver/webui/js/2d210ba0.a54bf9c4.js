(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["2d210ba0"],{b8b6:function(r,e,t){"use strict";t.r(e);var o=function(){var r=this,e=r.$createElement,t=r._self._c||e;return t("q-page",{staticClass:"page page-width-md"},[t("div",{staticClass:"page-block q-pa-xl"},[t("div",{staticClass:"q-my-md q-mb-xl q-display-1 text-primary"},[t("q-icon",{staticClass:"q-mr-sm",attrs:{name:r.$ethingUI.get(r.resource).icon}}),t("small",{staticClass:"text-faded"},[r._v("settings:")]),r._v(" "+r._s(r.resource.basename())+"\n    ")],1),t("resource-editor",{ref:"form",attrs:{resource:r.resource},on:{error:function(e){r.formError=e}}}),r.error?t("q-alert",{staticClass:"q-mb-xl",attrs:{type:"negative"}},[r._v("\n      "+r._s(String(r.error))+"\n    ")]):r._e(),t("div",[t("q-btn",{attrs:{loading:r.loading,disable:r.formError,color:"primary",icon:"done",label:"valid"},on:{click:r.handler}}),t("q-btn",{staticClass:"q-ml-sm",attrs:{color:"negative",icon:"clear",label:"cancel",flat:""},on:{click:r.onCancel}})],1)],1)])},a=[];o._withStripped=!0;t("a481");var n=t("d6ac"),s={name:"PageResource",components:{ResourceEditor:n["a"]},data:function(){return{loading:!1,error:!1,formError:!1}},computed:{resource:function(){var r=this.$route.params.id,e=this.$ething.arbo.get(r);return r&&r.length&&(e||this.$router.replace("/404")),e}},methods:{onDone:function(){this.$router.go(-1)},onCancel:function(){this.$router.go(-1)},handler:function(){var r=this;this.loading=!0,this.$refs.form.submit().then(this.onDone).catch(function(e){r.error=e||"error"}).finally(function(){r.loading=!1})}}},i=s,c=t("2877"),l=Object(c["a"])(i,o,a,!1,null,null,null);l.options.__file="Resource.vue";e["default"]=l.exports}}]);