(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[3],{"AT+L":function(r,e,t){"use strict";t.r(e);var o=function(){var r=this,e=r.$createElement,t=r._self._c||e;return t("div",{staticClass:"fixed-center content"},[t("div",{staticClass:"q-display-3 text-primary text-center"},[r._v("EThing")]),t("div",{staticClass:"q-pb-md"},[r.$ui.dynamicServerUrl?t("q-field",{attrs:{error:r.$v.server.$error,"error-label":"required"}},[t("q-input",{ref:"server",staticClass:"q-py-md",attrs:{autofocus:"","float-label":"Server Url"},on:{keyup:function(e){if(!("button"in e)&&r._k(e.keyCode,"enter",13,e.key,"Enter"))return null;r.$refs.login.focus()},blur:r.$v.server.$touch},model:{value:r.server,callback:function(e){r.server=e},expression:"server"}})],1):r._e(),t("q-field",{attrs:{error:r.$v.form.login.$error,"error-label":"Login is required"}},[t("q-input",{ref:"login",staticClass:"q-py-md",attrs:{autofocus:"","float-label":"Login"},on:{keyup:function(e){if(!("button"in e)&&r._k(e.keyCode,"enter",13,e.key,"Enter"))return null;r.$refs.password.focus()},blur:r.$v.form.login.$touch},model:{value:r.form.login,callback:function(e){r.$set(r.form,"login",e)},expression:"form.login"}})],1),t("q-field",{attrs:{error:r.$v.form.password.$error,"error-label":"Password is required"}},[t("q-input",{ref:"password",staticClass:"q-py-md",attrs:{type:"password","float-label":"Password",error:r.$v.form.password.$error},on:{keyup:function(e){return"button"in e||!r._k(e.keyCode,"enter",13,e.key,"Enter")?r.onConnect(e):null},blur:r.$v.form.password.$touch},model:{value:r.form.password,callback:function(e){r.$set(r.form,"password",e)},expression:"form.password"}})],1)],1),t("q-btn",{staticClass:"full-width",attrs:{loading:r.loading,disable:r.$v.$error,color:"primary"},on:{click:r.onConnect}},[r._v("Connect")])],1)},n=[];o._withStripped=!0;t("pIFo");var s=t("ta7f"),i="http://localhost:8000",a={name:"PageLogin",data:function(){return{loading:!1,server:this.$ui.getServerUrl()||i,form:{login:"",password:""}}},validations:function(){var r={form:{login:{required:s["required"]},password:{required:s["required"]}}};return this.$ui.dynamicServerUrl&&(r.server={required:s["required"]}),r},methods:{onConnect:function(){var r=this;if(this.$v.$touch(),!this.$v.$error){this.loading=!0;var e=this.server.trim().replace(/\/+$/,"");this.$ui.login(e,this.form.login,this.form.password).catch(function(t){if(t.response){var o=t.response.status;401==o||403==o?r.$q.notify("Invalid credentials."):r.$q.notify("Could not authenticate.")}else t.request?r.$q.notify("Unable to access to the EThing server at "+e):r.$q.notify("Error: "+t.message)}).finally(function(){r.loading=!1})}}}},l=a,u=(t("G3IP"),t("KHd+")),c=Object(u["a"])(l,o,n,!1,null,null,null);e["default"]=c.exports},G3IP:function(r,e,t){"use strict";var o=t("bJV5"),n=t.n(o);n.a},bJV5:function(r,e,t){}}]);