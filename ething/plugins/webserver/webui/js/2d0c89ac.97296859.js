(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["2d0c89ac"],{"561f":function(t,e,r){"use strict";r.r(e);var n=function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("q-page",{staticClass:"page page-width-md"},[r("div",{staticClass:"page-block q-pa-xl"},[r("div",{staticClass:"q-my-md q-mb-xl q-display-1 q-display-1-opacity"},[r("q-icon",{attrs:{name:t.$ethingUI.get(t.type).icon}}),t._v("\n      "+t._s(t.$ethingUI.get(t.type).title||t.defaultLabel)+"\n    ")],1),r("resource-editor",{ref:"form",attrs:{resource:t.type},on:{error:function(e){t.formError=e}}}),t.error?r("q-alert",{staticClass:"q-mb-xl",attrs:{type:"negative"}},[t._v("\n      "+t._s(String(t.error))+"\n    ")]):t._e(),r("div",[r("q-btn",{attrs:{loading:t.loading,disable:t.formError,color:"primary",icon:"done",label:"valid"},on:{click:t.handler}}),r("q-btn",{staticClass:"q-ml-sm",attrs:{color:"negative",icon:"clear",label:"cancel",flat:""},on:{click:t.onCancel}})],1)],1)])},o=[];n._withStripped=!0;r("a481"),r("28a5");var a=r("d6ac"),i={name:"PageResource",components:{ResourceEditor:a["a"]},data:function(){return{loading:!1,error:!1,formError:!1}},computed:{type:function(){return this.$route.params.type},defaultLabel:function(){return this.type.split("/").pop()}},methods:{onDone:function(){this.$router.go(-1)},onCancel:function(){this.$router.go(-1)},handler:function(){var t=this;this.loading=!0,this.$refs.form.submit().then(this.onDone).catch(function(e){t.error=e||"error"}).finally(function(){t.loading=!1})}},mounted:function(){this.$ethingUI.isDefined(this.type)||this.$router.replace("/404")}},s=i,l=r("2877"),c=Object(l["a"])(s,n,o,!1,null,null,null);c.options.__file="Create.vue";e["default"]=c.exports}}]);