(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[9],{GwkG:function(r,t,e){},"RIt+":function(r,t,e){"use strict";var n=e("GwkG"),o=e.n(n);o.a},"uLZ+":function(r,t,e){"use strict";e.r(t);var n=function(){var r=this,t=r.$createElement,e=r._self._c||t;return e("q-page",{attrs:{padding:""}},[e("div",{staticClass:"q-my-md q-display-1 text-primary"},[e("q-icon",{staticClass:"q-mr-sm",attrs:{name:r.$ethingUI.get(r.resource).icon}}),e("small",{staticClass:"text-faded"},[r._v("settings:")]),r._v(" "+r._s(r.resource.basename())+"\n  ")],1),e("resource-editor",{ref:"form",attrs:{resource:r.resource},on:{error:function(t){r.formError=t}}}),e("div",[e("q-btn",{attrs:{loading:r.loading,disable:r.formError,color:"primary",icon:"done",label:"valid"},on:{click:r.handler}}),e("q-btn",{staticClass:"q-ml-sm",attrs:{color:"negative",icon:"clear",label:"cancel",flat:""},on:{click:r.onCancel}})],1)],1)},o=[];n._withStripped=!0;e("pIFo");var a=e("wfIq"),i={name:"PageResource",components:{ResourceEditor:a["a"]},data:function(){return{loading:!1,error:!1,formError:!1}},computed:{resource:function(){var r=this.$route.params.id,t=this.$ething.arbo.get(r);return r&&r.length&&(t||this.$router.replace("/404")),t}},methods:{onDone:function(){this.$router.go(-1)},onCancel:function(){this.$router.go(-1)},handler:function(){var r=this;this.loading=!0,this.$refs.form.submit().then(this.onDone).catch(function(t){r.error=t||"error"}).finally(function(){r.loading=!1})}}},s=i,c=(e("RIt+"),e("KHd+")),l=Object(c["a"])(s,n,o,!1,null,null,null);l.options.__file="Resource.vue";t["default"]=l.exports}}]);