webpackJsonp([9],{"0Ima":function(e,t,n){(e.exports=n("FZ+f")(!1)).push([e.i,"\n.vertical-panes > .pane {\n  overflow: hidden;\n}\n.vertical-panes > .pane ~ .pane {\n  border-left: 1px solid #ccc;\n}\n.horizontal-panes > .pane ~ .pane {\n  border-top: 1px solid #ccc;\n}\n.horizontal-panes > .pane {\n  overflow: hidden;\n}\n.custom-resizer > .multipane-resizer {\n  background-color: #f1f1f1;\n  margin: 0;\n  left: 0;\n  position: relative;\n}\n.custom-resizer > .multipane-resizer:before {\n  display: block;\n  content: \"\";\n  width: 3px;\n  height: 40px;\n  position: absolute;\n  top: 50%;\n  left: 50%;\n  margin-top: -20px;\n  margin-left: -1.5px;\n  border-left: 1px solid #ccc;\n  border-right: 1px solid #ccc;\n}\n.custom-resizer > .multipane-resizer:hover:before {\n  border-color: #999;\n}\n.console .output-line {\n  padding-left: 16px;\n  padding-right: 16px;\n}\n.console .output-line.stdout {\n  color: #777;\n}\n.console .output-line.stderr {\n  color: #db2828;\n}\n.console .output-line.info {\n  color: #1e88e5;\n}\n.console .output-line:not(:last-child) {\n  border-bottom: 1px solid #eee;\n}\n.CodeMirror {\n  height: 100%;\n}\n.title.dirty:after {\n  content: '*';\n  color: #db2828;\n}\n",""])},BjUQ:function(e,t,n){var i=n("0Ima");"string"==typeof i&&(i=[[e.i,i,""]]),i.locals&&(e.exports=i.locals);(0,n("rjj0").default)("e2ae0478",i,!1,{})},Z6qg:function(e,t,n){(function(e){"use strict";var t={},n=/[^\s\u00a0]/,i=e.Pos;function o(e){var t=e.search(n);return-1==t?0:t}function l(e,t){var n=e.getMode();return!1!==n.useInnerComments&&n.innerMode?e.getModeAt(t):n}e.commands.toggleComment=function(e){e.toggleComment()},e.defineExtension("toggleComment",function(e){e||(e=t);for(var n=1/0,o=this.listSelections(),l=null,a=o.length-1;a>=0;a--){var s=o[a].from(),r=o[a].to();s.line>=n||(r.line>=n&&(r=i(n,0)),n=s.line,null==l?this.uncomment(s,r,e)?l="un":(this.lineComment(s,r,e),l="line"):"un"==l?this.uncomment(s,r,e):this.lineComment(s,r,e))}}),e.defineExtension("lineComment",function(e,a,s){s||(s=t);var r=this,c=l(r,e),u=r.getLine(e.line);if(null!=u&&(m=e,d=u,!/\bstring\b/.test(r.getTokenTypeAt(i(m.line,0)))||/^[\'\"\`]/.test(d))){var m,d,f=s.lineComment||c.lineComment;if(f){var p=Math.min(0!=a.ch||a.line==e.line?a.line+1:a.line,r.lastLine()+1),g=null==s.padding?" ":s.padding,h=s.commentBlankLines||e.line==a.line;r.operation(function(){if(s.indent){for(var t=null,l=e.line;l<p;++l){var a=(c=r.getLine(l)).slice(0,o(c));(null==t||t.length>a.length)&&(t=a)}for(l=e.line;l<p;++l){var c=r.getLine(l),u=t.length;(h||n.test(c))&&(c.slice(0,u)!=t&&(u=o(c)),r.replaceRange(t+f+g,i(l,0),i(l,u)))}}else for(l=e.line;l<p;++l)(h||n.test(r.getLine(l)))&&r.replaceRange(f+g,i(l,0))})}else(s.blockCommentStart||c.blockCommentStart)&&(s.fullLines=!0,r.blockComment(e,a,s))}}),e.defineExtension("blockComment",function(e,o,a){a||(a=t);var s=this,r=l(s,e),c=a.blockCommentStart||r.blockCommentStart,u=a.blockCommentEnd||r.blockCommentEnd;if(c&&u){if(!/\bcomment\b/.test(s.getTokenTypeAt(i(e.line,0)))){var m=Math.min(o.line,s.lastLine());m!=e.line&&0==o.ch&&n.test(s.getLine(m))&&--m;var d=null==a.padding?" ":a.padding;e.line>m||s.operation(function(){if(0!=a.fullLines){var t=n.test(s.getLine(m));s.replaceRange(d+u,i(m)),s.replaceRange(c+d,i(e.line,0));var l=a.blockCommentLead||r.blockCommentLead;if(null!=l)for(var f=e.line+1;f<=m;++f)(f!=m||t)&&s.replaceRange(l+d,i(f,0))}else s.replaceRange(u,o),s.replaceRange(c,e)})}}else(a.lineComment||r.lineComment)&&0!=a.fullLines&&s.lineComment(e,o,a)}),e.defineExtension("uncomment",function(e,o,a){a||(a=t);var s,r=this,c=l(r,e),u=Math.min(0!=o.ch||o.line==e.line?o.line:o.line-1,r.lastLine()),m=Math.min(e.line,u),d=a.lineComment||c.lineComment,f=[],p=null==a.padding?" ":a.padding;e:if(d){for(var g=m;g<=u;++g){var h=r.getLine(g),v=h.indexOf(d);if(v>-1&&!/comment/.test(r.getTokenTypeAt(i(g,v+1)))&&(v=-1),-1==v&&n.test(h))break e;if(v>-1&&n.test(h.slice(0,v)))break e;f.push(h)}if(r.operation(function(){for(var e=m;e<=u;++e){var t=f[e-m],n=t.indexOf(d),o=n+d.length;n<0||(t.slice(o,o+p.length)==p&&(o+=p.length),s=!0,r.replaceRange("",i(e,n),i(e,o)))}}),s)return!0}var C=a.blockCommentStart||c.blockCommentStart,x=a.blockCommentEnd||c.blockCommentEnd;if(!C||!x)return!1;var b=a.blockCommentLead||c.blockCommentLead,y=r.getLine(m),k=y.indexOf(C);if(-1==k)return!1;var _=u==m?y:r.getLine(u),z=_.indexOf(x,u==m?k+C.length:0),L=i(m,k+1),S=i(u,z+1);if(-1==z||!/comment/.test(r.getTokenTypeAt(L))||!/comment/.test(r.getTokenTypeAt(S))||r.getRange(L,S,"\n").indexOf(x)>-1)return!1;var w=y.lastIndexOf(C,e.ch),R=-1==w?-1:y.slice(0,e.ch).indexOf(x,w+C.length);if(-1!=w&&-1!=R&&R+x.length!=e.ch)return!1;R=_.indexOf(x,o.ch);var T=_.slice(o.ch).lastIndexOf(C,R-o.ch);return w=-1==R||-1==T?-1:o.ch+T,(-1==R||-1==w||w==o.ch)&&(r.operation(function(){r.replaceRange("",i(u,z-(p&&_.slice(z-p.length,z)==p?p.length:0)),i(u,z+x.length));var e=k+C.length;if(p&&y.slice(e,e+p.length)==p&&(e+=p.length),r.replaceRange("",i(m,k),i(m,e)),b)for(var t=m+1;t<=u;++t){var o=r.getLine(t),l=o.indexOf(b);if(-1!=l&&!n.test(o.slice(0,l))){var a=l+b.length;p&&o.slice(a,a+p.length)==p&&(a+=p.length),r.replaceRange("",i(t,l),i(t,a))}}}),!0)})})(n("8U58"))},bQT5:function(e,t,n){(function(e){function t(t){if(t.getOption("disableInput"))return e.Pass;for(var i,o=t.listSelections(),l=[],a=0;a<o.length;a++){var s=o[a].head;if(!/\bcomment\b/.test(t.getTokenTypeAt(s)))return e.Pass;var r=t.getModeAt(s);if(i){if(i!=r)return e.Pass}else i=r;var c=null;if(i.blockCommentStart&&i.blockCommentContinue){var u,m,d=(u=t.getLine(s.line).slice(0,s.ch)).lastIndexOf(i.blockCommentEnd);if(-1!=d&&d==s.ch-i.blockCommentEnd.length);else if((m=u.lastIndexOf(i.blockCommentStart))>-1&&m>d){if(c=u.slice(0,m),/\S/.test(c)){c="";for(var f=0;f<m;++f)c+=" "}}else(m=u.indexOf(i.blockCommentContinue))>-1&&!/\S/.test(u.slice(0,m))&&(c=u.slice(0,m));null!=c&&(c+=i.blockCommentContinue)}if(null==c&&i.lineComment&&n(t))(m=(u=t.getLine(s.line)).indexOf(i.lineComment))>-1&&(c=u.slice(0,m),/\S/.test(c)?c=null:c+=i.lineComment+u.slice(m+i.lineComment.length).match(/^\s*/)[0]);if(null==c)return e.Pass;l[a]="\n"+c}t.operation(function(){for(var e=o.length-1;e>=0;e--)t.replaceRange(l[e],o[e].from(),o[e].to(),"+insert")})}function n(e){var t=e.getOption("continueComments");return!t||"object"!=typeof t||!1!==t.continueLineComment}e.defineOption("continueComments",null,function(n,i,o){if(o&&o!=e.Init&&n.removeKeyMap("continueComment"),i){var l="Enter";"string"==typeof i?l=i:"object"==typeof i&&i.key&&(l=i.key);var a={name:"continueComment"};a[l]=t,n.addKeyMap(a)}})})(n("8U58"))},uzIl:function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var i={name:"multipane",props:{layout:{type:String,default:"vertical"}},data:function(){return{isResizing:!1}},computed:{classnames:function(){return["multipane","layout-"+this.layout.slice(0,1),this.isResizing?"is-resizing":""]},cursor:function(){return this.isResizing?"vertical"==this.layout?"col-resize":"row-resize":""},userSelect:function(){return this.isResizing?"none":""}},methods:{onMouseDown:function(e){var t=e.target,n=e.pageX,i=e.pageY;if(t.className&&t.className.match("multipane-resizer")){var o=this,l=o.$el,a=o.layout,s=t.previousElementSibling,r=s.offsetWidth,c=s.offsetHeight,u=!!(s.style.width+"").match("%"),m=window.addEventListener,d=window.removeEventListener,f=function(e,t){if(void 0===t&&(t=0),"vertical"==a){var n=l.clientWidth,i=e+t;return s.style.width=u?i/n*100+"%":i+"px"}if("horizontal"==a){var o=l.clientHeight,r=e+t;return s.style.height=u?r/o*100+"%":r+"px"}};o.isResizing=!0;var p=f();o.$emit("paneResizeStart",s,t,p);var g=function(e){var l=e.pageX,u=e.pageY;p="vertical"==a?f(r,l-n):f(c,u-i),o.$emit("paneResize",s,t,p)},h=function(){p=f("vertical"==a?s.clientWidth:s.clientHeight),o.isResizing=!1,d("mousemove",g),d("mouseup",h),o.$emit("paneResizeStop",s,t,p)};m("mousemove",g),m("mouseup",h)}}}};!function(){if("undefined"!=typeof document){var e=document.head||document.getElementsByTagName("head")[0],t=document.createElement("style"),n=".multipane { display: flex; } .multipane.layout-h { flex-direction: column; } .multipane.layout-v { flex-direction: row; } .multipane > div { position: relative; z-index: 1; } .multipane-resizer { display: block; position: relative; z-index: 2; } .layout-h > .multipane-resizer { width: 100%; height: 10px; margin-top: -10px; top: 5px; cursor: row-resize; } .layout-v > .multipane-resizer { width: 10px; height: 100%; margin-left: -10px; left: 5px; cursor: col-resize; } ";t.type="text/css",t.styleSheet?t.styleSheet.cssText=n:t.appendChild(document.createTextNode(n)),e.appendChild(t)}}();var o=Object.assign(i,{render:function(){var e=this,t=e.$createElement;return(e._self._c||t)("div",{class:e.classnames,style:{cursor:e.cursor,userSelect:e.userSelect},on:{mousedown:e.onMouseDown}},[e._t("default")],2)},staticRenderFns:[]});o.prototype=i.prototype,function(){if("undefined"!=typeof document){var e=document.head||document.getElementsByTagName("head")[0],t=document.createElement("style");t.type="text/css",t.styleSheet?t.styleSheet.cssText="":t.appendChild(document.createTextNode("")),e.appendChild(t)}}();var l={render:function(){var e=this,t=e.$createElement;return(e._self._c||t)("div",{staticClass:"multipane-resizer"},[e._t("default")],2)},staticRenderFns:[]};"undefined"!=typeof window&&window.Vue&&(window.Vue.component("multipane",o),window.Vue.component("multipane-resizer",l));var a=n("E5Az"),s=(n("4/hK"),n("5IAE"),n("vq+x"),n("aX1R"),n("bQT5"),n("Z6qg"),{name:"PageText",components:{codemirror:a.codemirror,Multipane:o,MultipaneResizer:l},data:function(){var e=this;return{content:"",cmOption:{mode:"application/javascript",tabSize:4,styleActiveLine:!0,lineNumbers:!0,lineWrapping:!1,foldGutter:!0,styleSelectedText:!0,matchBrackets:!0,autoCloseBrackets:!0,showCursorWhenSelecting:!0,extraKeys:{Ctrl:"autocomplete","Ctrl-S":function(){e.save()}},hintOptions:{completeSingle:!1},viewportMargin:1/0},loading:!0,saveLoading:!1,exeLoading:!1,dirty:!1,console:{enabled:!1,output:[],info:{}},orientation:this.$q.platform.is.mobile?"horizontal":"vertical",settingsModal:!1,args:""}},computed:{resource:function(){var e=this.$route.params.id,t=this.$store.getters["ething/get"](e);return e&&e.length&&(t||this.$router.replace("/404")),t}},methods:{codemirror:function(){return this.$refs.cm.codemirror},markClean:function(){this.dirty=!1,this.codemirror().markClean()},reloadContent:function(){var e=this;this.loading=!0,this.resource.read().then(function(t){e.content=t,e.$nextTick(function(){e.markClean(),e.codemirror().clearHistory()})}).finally(function(){e.loading=!1})},save:function(e){var t=this;this.saveLoading=!0,this.resource.write(this.content).then(function(){t.dirty=!1,t.markClean(),"function"==typeof e&&e()}).finally(function(){t.saveLoading=!1})},onChange:function(e,t){this.dirty=!e.isClean()},execute:function(){var e=this;this.exeLoading=!0,this.resource.execute(this.args).then(function(t){console.log(t),e.printResult(t)}).finally(function(){e.exeLoading=!1,setTimeout(function(){e.$refs.outputScrollArea.setScrollPosition(1e9)},1)})},onExecuteClick:function(){this.dirty?this.save(this.execute):this.execute()},printResult:function(e){this.console.enabled=!0,this.console.output=e.output,this.console.info={status:e.ok,returnCode:e.return_code,executionTime:e.executionTime}}},mounted:function(){this.reloadContent()}}),r=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("q-page",[n("multipane",{staticClass:"absolute fit",class:"vertical"==e.orientation?"vertical-panes":"horizontal-panes",attrs:{layout:e.orientation}},[n("div",{staticClass:"pane",style:"vertical"==e.orientation?{width:"50%",maxWidth:"75%"}:{height:"50%",maxHeight:"75%"}},[n("div",{staticClass:"column absolute fit"},[n("div",{staticClass:"col-auto"},[n("q-btn-group",{attrs:{flat:""}},[n("q-btn",{attrs:{loading:e.saveLoading,label:"save",icon:"mdi-content-save-outline"},on:{click:e.save}}),e._v(" "),n("q-btn",{attrs:{loading:e.exeLoading,label:"run",icon:"play_arrow"},on:{click:e.onExecuteClick}}),e._v(" "),n("q-btn",{attrs:{label:"settings",icon:"settings"},on:{click:function(t){e.settingsModal=!0}}})],1),e._v(" "),n("span",{staticClass:"title text-faded",class:{dirty:e.dirty}},[e._v(e._s(e.resource.name()))])],1),e._v(" "),n("q-scroll-area",{staticClass:"col",staticStyle:{height:"100%"}},[n("codemirror",{ref:"cm",attrs:{options:e.cmOption},on:{changes:e.onChange},model:{value:e.content,callback:function(t){e.content=t},expression:"content"}})],1)],1)]),e._v(" "),n("multipane-resizer"),e._v(" "),n("div",{staticClass:"pane console",style:{flexGrow:1}},[e.exeLoading?n("div",{staticClass:"absolute-center text-faded"},[e._v("\n        running ...\n      ")]):e.console.enabled?n("q-scroll-area",{ref:"outputScrollArea",staticClass:"absolute fit"},[n("div",{staticClass:"output"},[e._l(e.console.output,function(t,i){return n("div",{key:i,staticClass:"output-line",class:t.type},[n("pre",{staticClass:"q-ma-none"},[n("code",[e._v(e._s(t.chunk))])])])}),e._v(" "),n("div",{staticClass:"output-line info"},[e._v("status: "+e._s(e.console.info.status?"success":"fail"))]),e._v(" "),n("div",{staticClass:"output-line info"},[e._v("return code: "+e._s(e.console.info.returnCode))]),e._v(" "),n("div",{staticClass:"output-line info"},[e._v("duration: "+e._s(e.console.info.executionTime)+" secondes")])],2)]):e._e()],1)],1),e._v(" "),n("q-modal",{attrs:{"content-css":{padding:"50px",minWidth:"50vw"}},model:{value:e.settingsModal,callback:function(t){e.settingsModal=t},expression:"settingsModal"}},[n("div",{staticClass:"q-title q-my-md"},[e._v("Settings")]),e._v(" "),n("q-field",{staticClass:"q-my-md",attrs:{label:"Arguments",orientation:"vertical"}},[n("q-input",{model:{value:e.args,callback:function(t){e.args=t},expression:"args"}})],1),e._v(" "),n("div",{staticClass:"q-mt-xl"},[n("q-btn",{attrs:{flat:"",color:"faded",label:"Close"},on:{click:function(t){e.settingsModal=!1}}})],1)],1)],1)},c=[];r._withStripped=!0;var u=n("XyMi"),m=!1;var d=function(e){m||n("BjUQ")},f=Object(u.a)(s,r,c,!1,d,null,null);f.options.__file="src\\pages\\Script.vue";t.default=f.exports}});