webpackJsonp([7],{"0Ima":function(e,n,t){(e.exports=t("FZ+f")(!1)).push([e.i,"\n.vertical-panes > .pane {\n  overflow: hidden;\n}\n.vertical-panes > .pane ~ .pane {\n  border-left: 1px solid #ccc;\n}\n.horizontal-panes > .pane ~ .pane {\n  border-top: 1px solid #ccc;\n}\n.horizontal-panes > .pane {\n  overflow: hidden;\n}\n.custom-resizer > .multipane-resizer {\n  background-color: #f1f1f1;\n  margin: 0;\n  position: relative;\n}\n.custom-resizer > .multipane-resizer:before {\n  display: block;\n  content: \"\";\n  position: absolute;\n  top: 50%;\n  left: 50%;\n}\n.custom-resizer > .multipane-resizer:hover:before {\n  border-color: #999;\n}\n.horizontal-panes.custom-resizer > .multipane-resizer {\n  top: 0;\n}\n.horizontal-panes.custom-resizer > .multipane-resizer:before {\n  width: 40px;\n  height: 3px;\n  margin-top: -1.5px;\n  margin-left: -20px;\n  border-top: 1px solid #ccc;\n  border-bottom: 1px solid #ccc;\n}\n.vertical-panes.custom-resizer > .multipane-resizer {\n  left: 0;\n}\n.vertical-panes.custom-resizer > .multipane-resizer:before {\n  width: 3px;\n  height: 40px;\n  margin-top: -20px;\n  margin-left: -1.5px;\n  border-left: 1px solid #ccc;\n  border-right: 1px solid #ccc;\n}\n.console .output-line {\n  padding-left: 16px;\n  padding-right: 16px;\n}\n.console .output-line.stdout {\n  color: #777;\n}\n.console .output-line.stderr {\n  color: #db2828;\n}\n.console .output-line.info {\n  color: #1e88e5;\n}\n.console .output-line:not(:last-child) {\n  border-bottom: 1px solid #eee;\n}\n.CodeMirror {\n  height: 100%;\n}\n.title.dirty:after {\n  content: '*';\n  color: #db2828;\n}\n",""])},BjUQ:function(e,n,t){var i=t("0Ima");"string"==typeof i&&(i=[[e.i,i,""]]),i.locals&&(e.exports=i.locals);(0,t("rjj0").default)("e2ae0478",i,!1,{})},PjUl:function(e,n,t){(e.exports=t("FZ+f")(!1)).push([e.i,"\n.multipane {\n  display: -ms-flexbox;\n  display: flex;\n}\n.multipane.layout-h {\n  -ms-flex-direction: column;\n      flex-direction: column;\n}\n.multipane.layout-v {\n  -ms-flex-direction: row;\n      flex-direction: row;\n}\n.multipane > div {\n  position: relative;\n  z-index: 1;\n}\n.multipane-resizer {\n  display: block;\n  position: relative;\n  z-index: 2;\n}\n.layout-h > .multipane-resizer {\n  width: 100%;\n  height: 10px;\n  margin-top: -10px;\n  top: 5px;\n  cursor: row-resize;\n}\n.layout-v > .multipane-resizer {\n  width: 10px;\n  height: 100%;\n  margin-left: -10px;\n  left: 5px;\n  cursor: col-resize;\n}\n",""])},W0s8:function(e,n,t){var i=t("PjUl");"string"==typeof i&&(i=[[e.i,i,""]]),i.locals&&(e.exports=i.locals);(0,t("rjj0").default)("41f6cea8",i,!1,{})},Z6qg:function(e,n,t){(function(e){"use strict";var n={},t=/[^\s\u00a0]/,i=e.Pos;function o(e){var n=e.search(t);return-1==n?0:n}function l(e,n){var t=e.getMode();return!1!==t.useInnerComments&&t.innerMode?e.getModeAt(n):t}e.commands.toggleComment=function(e){e.toggleComment()},e.defineExtension("toggleComment",function(e){e||(e=n);for(var t=1/0,o=this.listSelections(),l=null,s=o.length-1;s>=0;s--){var a=o[s].from(),r=o[s].to();a.line>=t||(r.line>=t&&(r=i(t,0)),t=a.line,null==l?this.uncomment(a,r,e)?l="un":(this.lineComment(a,r,e),l="line"):"un"==l?this.uncomment(a,r,e):this.lineComment(a,r,e))}}),e.defineExtension("lineComment",function(e,s,a){a||(a=n);var r=this,c=l(r,e),u=r.getLine(e.line);if(null!=u&&(m=e,f=u,!/\bstring\b/.test(r.getTokenTypeAt(i(m.line,0)))||/^[\'\"\`]/.test(f))){var m,f,p=a.lineComment||c.lineComment;if(p){var d=Math.min(0!=s.ch||s.line==e.line?s.line+1:s.line,r.lastLine()+1),h=null==a.padding?" ":a.padding,g=a.commentBlankLines||e.line==s.line;r.operation(function(){if(a.indent){for(var n=null,l=e.line;l<d;++l){var s=(c=r.getLine(l)).slice(0,o(c));(null==n||n.length>s.length)&&(n=s)}for(l=e.line;l<d;++l){var c=r.getLine(l),u=n.length;(g||t.test(c))&&(c.slice(0,u)!=n&&(u=o(c)),r.replaceRange(n+p+h,i(l,0),i(l,u)))}}else for(l=e.line;l<d;++l)(g||t.test(r.getLine(l)))&&r.replaceRange(p+h,i(l,0))})}else(a.blockCommentStart||c.blockCommentStart)&&(a.fullLines=!0,r.blockComment(e,s,a))}}),e.defineExtension("blockComment",function(e,o,s){s||(s=n);var a=this,r=l(a,e),c=s.blockCommentStart||r.blockCommentStart,u=s.blockCommentEnd||r.blockCommentEnd;if(c&&u){if(!/\bcomment\b/.test(a.getTokenTypeAt(i(e.line,0)))){var m=Math.min(o.line,a.lastLine());m!=e.line&&0==o.ch&&t.test(a.getLine(m))&&--m;var f=null==s.padding?" ":s.padding;e.line>m||a.operation(function(){if(0!=s.fullLines){var n=t.test(a.getLine(m));a.replaceRange(f+u,i(m)),a.replaceRange(c+f,i(e.line,0));var l=s.blockCommentLead||r.blockCommentLead;if(null!=l)for(var p=e.line+1;p<=m;++p)(p!=m||n)&&a.replaceRange(l+f,i(p,0))}else a.replaceRange(u,o),a.replaceRange(c,e)})}}else(s.lineComment||r.lineComment)&&0!=s.fullLines&&a.lineComment(e,o,s)}),e.defineExtension("uncomment",function(e,o,s){s||(s=n);var a,r=this,c=l(r,e),u=Math.min(0!=o.ch||o.line==e.line?o.line:o.line-1,r.lastLine()),m=Math.min(e.line,u),f=s.lineComment||c.lineComment,p=[],d=null==s.padding?" ":s.padding;e:if(f){for(var h=m;h<=u;++h){var g=r.getLine(h),v=g.indexOf(f);if(v>-1&&!/comment/.test(r.getTokenTypeAt(i(h,v+1)))&&(v=-1),-1==v&&t.test(g))break e;if(v>-1&&t.test(g.slice(0,v)))break e;p.push(g)}if(r.operation(function(){for(var e=m;e<=u;++e){var n=p[e-m],t=n.indexOf(f),o=t+f.length;t<0||(n.slice(o,o+d.length)==d&&(o+=d.length),a=!0,r.replaceRange("",i(e,t),i(e,o)))}}),a)return!0}var x=s.blockCommentStart||c.blockCommentStart,b=s.blockCommentEnd||c.blockCommentEnd;if(!x||!b)return!1;var C=s.blockCommentLead||c.blockCommentLead,y=r.getLine(m),k=y.indexOf(x);if(-1==k)return!1;var z=u==m?y:r.getLine(u),_=z.indexOf(b,u==m?k+x.length:0),w=i(m,k+1),L=i(u,_+1);if(-1==_||!/comment/.test(r.getTokenTypeAt(w))||!/comment/.test(r.getTokenTypeAt(L))||r.getRange(w,L,"\n").indexOf(b)>-1)return!1;var S=y.lastIndexOf(x,e.ch),R=-1==S?-1:y.slice(0,e.ch).indexOf(b,S+x.length);if(-1!=S&&-1!=R&&R+b.length!=e.ch)return!1;R=z.indexOf(b,o.ch);var M=z.slice(o.ch).lastIndexOf(x,R-o.ch);return S=-1==R||-1==M?-1:o.ch+M,(-1==R||-1==S||S==o.ch)&&(r.operation(function(){r.replaceRange("",i(u,_-(d&&z.slice(_-d.length,_)==d?d.length:0)),i(u,_+b.length));var e=k+x.length;if(d&&y.slice(e,e+d.length)==d&&(e+=d.length),r.replaceRange("",i(m,k),i(m,e)),C)for(var n=m+1;n<=u;++n){var o=r.getLine(n),l=o.indexOf(C);if(-1!=l&&!t.test(o.slice(0,l))){var s=l+C.length;d&&o.slice(s,s+d.length)==d&&(s+=d.length),r.replaceRange("",i(n,l),i(n,s))}}}),!0)})})(t("8U58"))},bQT5:function(e,n,t){(function(e){function n(n){if(n.getOption("disableInput"))return e.Pass;for(var i,o=n.listSelections(),l=[],s=0;s<o.length;s++){var a=o[s].head;if(!/\bcomment\b/.test(n.getTokenTypeAt(a)))return e.Pass;var r=n.getModeAt(a);if(i){if(i!=r)return e.Pass}else i=r;var c=null;if(i.blockCommentStart&&i.blockCommentContinue){var u,m,f=(u=n.getLine(a.line).slice(0,a.ch)).lastIndexOf(i.blockCommentEnd);if(-1!=f&&f==a.ch-i.blockCommentEnd.length);else if((m=u.lastIndexOf(i.blockCommentStart))>-1&&m>f){if(c=u.slice(0,m),/\S/.test(c)){c="";for(var p=0;p<m;++p)c+=" "}}else(m=u.indexOf(i.blockCommentContinue))>-1&&!/\S/.test(u.slice(0,m))&&(c=u.slice(0,m));null!=c&&(c+=i.blockCommentContinue)}if(null==c&&i.lineComment&&t(n))(m=(u=n.getLine(a.line)).indexOf(i.lineComment))>-1&&(c=u.slice(0,m),/\S/.test(c)?c=null:c+=i.lineComment+u.slice(m+i.lineComment.length).match(/^\s*/)[0]);if(null==c)return e.Pass;l[s]="\n"+c}n.operation(function(){for(var e=o.length-1;e>=0;e--)n.replaceRange(l[e],o[e].from(),o[e].to(),"+insert")})}function t(e){var n=e.getOption("continueComments");return!n||"object"!=typeof n||!1!==n.continueLineComment}e.defineOption("continueComments",null,function(t,i,o){if(o&&o!=e.Init&&t.removeKeyMap("continueComment"),i){var l="Enter";"string"==typeof i?l=i:"object"==typeof i&&i.key&&(l=i.key);var s={name:"continueComment"};s[l]=n,t.addKeyMap(s)}})})(t("8U58"))},uzIl:function(e,n,t){"use strict";Object.defineProperty(n,"__esModule",{value:!0});var i={name:"multipane",props:{layout:{type:String,default:"vertical"}},data:function(){return{isResizing:!1}},computed:{classnames:function(){return["multipane","layout-"+this.layout.slice(0,1),this.isResizing?"is-resizing":""]},cursor:function(){return this.isResizing?"vertical"==this.layout?"col-resize":"row-resize":""},userSelect:function(){return this.isResizing?"none":""}},methods:{onMouseDown:function(e){var n=e.target;if(n.className&&n.className.match("multipane-resizer")){var t=function(e,n){var t="page"+n;return"number"==typeof e[t]?e[t]:e.touches&&e.touches.length>0?e.touches[0][t]:void 0};e.preventDefault();var i=t(e,"X"),o=t(e,"Y"),l=this,s=l.$el,a=l.layout,r=Boolean(n.className.match("affect-follower")),c=n.previousElementSibling;r&&(c=n.nextElementSibling);var u=c,m=u.offsetWidth,f=u.offsetHeight,p=!!(c.style.width+"").match("%"),d=window,h=d.addEventListener,g=d.removeEventListener,v=function(e){var n=arguments.length>1&&void 0!==arguments[1]?arguments[1]:0;if(r&&(n=-n),"vertical"==a){var t=s.clientWidth,i=e+n;return c.style.width=p?i/t*100+"%":i+"px"}if("horizontal"==a){var o=s.clientHeight,l=e+n;return c.style.height=p?l/o*100+"%":l+"px"}};l.isResizing=!0;var x=v();l.$emit("paneResizeStart",c,n,x);var b=function(e){var s=t(e,"X"),r=t(e,"Y");x="vertical"==a?v(m,s-i):v(f,r-o),l.$emit("paneResize",c,n,x)},C=function e(){x=v("vertical"==a?c.clientWidth:c.clientHeight),l.isResizing=!1,g("mousemove",b),g("mouseup",e),g("touchmove",b),g("touchend",e),l.$emit("paneResizeStop",c,n,x)};h("mousemove",b),h("mouseup",C),h("touchmove",b),h("touchend",C)}}}},o=function(){var e=this.$createElement;return(this._self._c||e)("div",{class:this.classnames,style:{cursor:this.cursor,userSelect:this.userSelect},on:{mousedown:this.onMouseDown,touchstart:this.onMouseDown}},[this._t("default")],2)},l=[];o._withStripped=!0;var s=t("XyMi"),a=!1;var r=function(e){a||t("W0s8")},c=Object(s.a)(i,o,l,!1,r,null,null);c.options.__file="src\\components\\vue-multipane\\multipane.vue";var u=c.exports,m={name:"multipane-resizer",props:{affectFollower:{type:Boolean,default:!1}},computed:{classnames:function(){return["multipane-resizer",this.affectFollower?"affect-follower":""]}}},f=function(){var e=this.$createElement;return(this._self._c||e)("div",{class:this.classnames},[this._t("default")],2)},p=[];f._withStripped=!0;var d=Object(s.a)(m,f,p,!1,null,null,null);d.options.__file="src\\components\\vue-multipane\\multipane-resizer.vue";var h=d.exports;"undefined"!=typeof window&&window.Vue&&(window.Vue.component("multipane",u),window.Vue.component("multipane-resizer",h));var g=t("E5Az"),v=(t("4/hK"),t("5IAE"),t("vq+x"),t("aX1R"),t("bQT5"),t("Z6qg"),{name:"PageText",components:{codemirror:g.codemirror,Multipane:u,MultipaneResizer:h},data:function(){var e=this;return{content:"",cmOption:{mode:"application/javascript",tabSize:4,styleActiveLine:!0,lineNumbers:!0,lineWrapping:!1,foldGutter:!0,styleSelectedText:!0,matchBrackets:!0,autoCloseBrackets:!0,showCursorWhenSelecting:!0,extraKeys:{Ctrl:"autocomplete","Ctrl-S":function(){e.save()}},hintOptions:{completeSingle:!1},viewportMargin:1/0},loading:!0,saveLoading:!1,exeLoading:!1,dirty:!1,console:{enabled:!1,output:[],info:{}},orientation:this.$q.platform.is.mobile?"horizontal":"vertical",settingsModal:!1,args:""}},computed:{resource:function(){var e=this.$route.params.id,n=this.$store.getters["ething/get"](e);return e&&e.length&&(n||this.$router.replace("/404")),n}},methods:{codemirror:function(){return this.$refs.cm.codemirror},markClean:function(){this.dirty=!1,this.codemirror().markClean()},reloadContent:function(){var e=this;this.loading=!0,this.resource.read().then(function(n){e.content=n,e.$nextTick(function(){e.markClean(),e.codemirror().clearHistory()})}).finally(function(){e.loading=!1})},save:function(e){var n=this;this.saveLoading=!0,this.resource.write(this.content).then(function(){n.dirty=!1,n.markClean(),"function"==typeof e&&e()}).finally(function(){n.saveLoading=!1})},onChange:function(e,n){this.dirty=!e.isClean()},execute:function(){var e=this;this.exeLoading=!0,this.resource.execute(this.args).then(function(n){console.log(n),e.printResult(n)}).finally(function(){e.exeLoading=!1,setTimeout(function(){e.$refs.outputScrollArea.setScrollPosition(1e9)},1)})},onExecuteClick:function(){this.dirty?this.save(this.execute):this.execute()},printResult:function(e){this.console.enabled=!0,this.console.output=e.output,this.console.info={status:e.ok,returnCode:e.return_code,executionTime:e.executionTime}}},mounted:function(){this.reloadContent()}}),x=function(){var e=this,n=e.$createElement,t=e._self._c||n;return t("q-page",[t("multipane",{staticClass:"absolute fit custom-resizer",class:"vertical"==e.orientation?"vertical-panes":"horizontal-panes",attrs:{layout:e.orientation}},[t("div",{staticClass:"pane",style:"vertical"==e.orientation?{width:"50%",minWidth:"25%",maxWidth:"75%"}:{height:"50%",minHeight:"25%",maxHeight:"75%"}},[t("div",{staticClass:"column absolute fit"},[t("div",{staticClass:"col-auto"},[t("q-btn-group",{attrs:{flat:""}},[t("q-btn",{attrs:{loading:e.saveLoading,label:"save",icon:"mdi-content-save-outline"},on:{click:e.save}}),e._v(" "),t("q-btn",{attrs:{loading:e.exeLoading,label:"run",icon:"play_arrow"},on:{click:e.onExecuteClick}}),e._v(" "),t("q-btn",{attrs:{label:"settings",icon:"settings"},on:{click:function(n){e.settingsModal=!0}}})],1),e._v(" "),t("span",{staticClass:"title text-faded",class:{dirty:e.dirty}},[e._v(e._s(e.resource.name()))])],1),e._v(" "),t("q-scroll-area",{staticClass:"col",staticStyle:{height:"100%"}},[t("codemirror",{ref:"cm",attrs:{options:e.cmOption},on:{changes:e.onChange},model:{value:e.content,callback:function(n){e.content=n},expression:"content"}})],1)],1)]),e._v(" "),t("multipane-resizer"),e._v(" "),t("div",{staticClass:"pane console",style:{flexGrow:1}},[e.exeLoading?t("div",{staticClass:"absolute-center text-faded"},[e._v("\n        running ...\n      ")]):e.console.enabled?t("q-scroll-area",{ref:"outputScrollArea",staticClass:"absolute fit"},[t("div",{staticClass:"output"},[e._l(e.console.output,function(n,i){return t("div",{key:i,staticClass:"output-line",class:n.type},[t("pre",{staticClass:"q-ma-none"},[t("code",[e._v(e._s(n.chunk))])])])}),e._v(" "),t("div",{staticClass:"output-line info"},[e._v("status: "+e._s(e.console.info.status?"success":"fail"))]),e._v(" "),t("div",{staticClass:"output-line info"},[e._v("return code: "+e._s(e.console.info.returnCode))]),e._v(" "),t("div",{staticClass:"output-line info"},[e._v("duration: "+e._s(e.console.info.executionTime)+" secondes")])],2)]):t("div",{staticClass:"absolute-center text-light"},[e._v("\n        Console\n      ")])],1)],1),e._v(" "),t("q-modal",{attrs:{"content-css":{padding:"50px",minWidth:"50vw"}},model:{value:e.settingsModal,callback:function(n){e.settingsModal=n},expression:"settingsModal"}},[t("div",{staticClass:"q-title q-my-md"},[e._v("Settings")]),e._v(" "),t("q-field",{staticClass:"q-my-md",attrs:{label:"Arguments",orientation:"vertical"}},[t("q-input",{model:{value:e.args,callback:function(n){e.args=n},expression:"args"}})],1),e._v(" "),t("div",{staticClass:"q-mt-xl"},[t("q-btn",{attrs:{flat:"",color:"faded",label:"Close"},on:{click:function(n){e.settingsModal=!1}}})],1)],1)],1)},b=[];x._withStripped=!0;var C=!1;var y=function(e){C||t("BjUQ")},k=Object(s.a)(v,x,b,!1,y,null,null);k.options.__file="src\\pages\\Script.vue";n.default=k.exports}});