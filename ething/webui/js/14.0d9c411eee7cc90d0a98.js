webpackJsonp([14],{"/+vu":function(e,n,t){"use strict";Object.defineProperty(n,"__esModule",{value:!0});var r={name:"PageImage",components:{ImageViewer:t("pbTc").a},computed:{resource:function(){var e=this.$route.params.id,n=this.$store.getters["ething/get"](e);return e&&e.length&&(n||this.$router.replace("/404")),n},sources:function(){var e=this;return this.$ething.arbo.glob(this.resource.dirname()?this.resource.dirname()+"/*":"*").filter(function(n){return n instanceof e.$ething.File&&/^image/.test(n.mime())})}}},i=function(){var e=this.$createElement,n=this._self._c||e;return n("q-page",[n("image-viewer",{attrs:{source:this.sources,value:this.resource,thumbnails:"",controls:""}})],1)},s=[];i._withStripped=!0;var o=t("XyMi"),a=!1;var u=function(e){a||t("/z+b")},c=Object(o.a)(r,i,s,!1,u,null,null);c.options.__file="src\\pages\\Image.vue";n.default=c.exports},"/z+b":function(e,n,t){var r=t("lMVt");"string"==typeof r&&(r=[[e.i,r,""]]),r.locals&&(e.exports=r.locals);(0,t("rjj0").default)("e9649ae6",r,!1,{})},lMVt:function(e,n,t){(e.exports=t("FZ+f")(!1)).push([e.i,"\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",""])}});