(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[15],{"+B4/":function(r,e,o){},"2kGi":function(r,e,o){"use strict";var t=o("+B4/"),n=o.n(t);n.a},"AT+L":function(r,e,o){"use strict";o.r(e);var t=function(){var r=this,e=r.$createElement,o=r._self._c||e;return o("div",{staticClass:"fixed-center content"},[o("div",{staticClass:"q-display-3 text-primary text-center"},[r._v("EThing")]),o("div",{staticClass:"q-pb-md"},[r.$ui.dynamicServerUrl?o("q-field",{attrs:{error:r.$v.server.$error,"error-label":"required"}},[o("q-input",{ref:"server",staticClass:"q-py-md",attrs:{autofocus:"","float-label":"Server Url"},on:{keyup:function(e){if(!("button"in e)&&r._k(e.keyCode,"enter",13,e.key,"Enter"))return null;r.$refs.login.focus()},blur:r.$v.server.$touch},model:{value:r.server,callback:function(e){r.server=e},expression:"server"}})],1):r._e(),o("q-field",{attrs:{error:r.$v.form.login.$error,"error-label":"Login is required"}},[o("q-input",{ref:"login",staticClass:"q-py-md",attrs:{autofocus:"","float-label":"Login"},on:{keyup:function(e){if(!("button"in e)&&r._k(e.keyCode,"enter",13,e.key,"Enter"))return null;r.$refs.password.focus()},blur:r.$v.form.login.$touch},model:{value:r.form.login,callback:function(e){r.$set(r.form,"login",e)},expression:"form.login"}})],1),o("q-field",{attrs:{error:r.$v.form.password.$error,"error-label":"Password is required"}},[o("q-input",{ref:"password",staticClass:"q-py-md",attrs:{type:"password","float-label":"Password",error:r.$v.form.password.$error},on:{keyup:function(e){return"button"in e||!r._k(e.keyCode,"enter",13,e.key,"Enter")?r.onConnect(e):null},blur:r.$v.form.password.$touch},model:{value:r.form.password,callback:function(e){r.$set(r.form,"password",e)},expression:"form.password"}})],1)],1),o("q-btn",{staticClass:"full-width",attrs:{loading:r.loading,disable:r.$v.$error,color:"primary"},on:{click:r.onConnect}},[r._v("Connect")])],1)},n=[];t._withStripped=!0;o("pIFo");var s=o("ta7f"),i="http://localhost:8000",a={name:"PageLogin",data:function(){return{loading:!1,server:this.$ui.getServerUrl()||i,form:{login:"",password:""}}},validations:function(){var r={form:{login:{required:s["required"]},password:{required:s["required"]}}};return this.$ui.dynamicServerUrl&&(r.server={required:s["required"]}),r},methods:{onConnect:function(){var r=this;if(this.$v.$touch(),!this.$v.$error){this.loading=!0;var e=this.server.trim().replace(/\/+$/,"");this.$ui.login(e,this.form.login,this.form.password).catch(function(o){if(o.response){var t=o.response.status;401==t||403==t?r.$q.notify("Invalid credentials."):r.$q.notify("Could not authenticate.")}else o.request?r.$q.notify("Unable to access to the EThing server at "+e):r.$q.notify("Error: "+o.message)}).finally(function(){r.loading=!1})}}}},l=a,u=(o("2kGi"),o("KHd+")),c=Object(u["a"])(l,t,n,!1,null,null,null);c.options.__file="Login.vue";e["default"]=c.exports}}]);