webpackJsonp([9],{"0Ima":function(e,t,n){(e.exports=n("FZ+f")(!1)).push([e.i,"\n.vertical-panes > .pane {\n  overflow: auto;\n}\n.vertical-panes > .pane ~ .pane {\n  border-left: 1px solid #ccc;\n}\n.horizontal-panes > .pane ~ .pane {\n  border-top: 1px solid #ccc;\n}\n.horizontal-panes > .pane {\n  overflow: auto;\n}\n.custom-resizer > .multipane-resizer {\n  background-color: #f1f1f1;\n  margin: 0;\n  left: 0;\n  position: relative;\n}\n.custom-resizer > .multipane-resizer:before {\n  display: block;\n  content: \"\";\n  width: 3px;\n  height: 40px;\n  position: absolute;\n  top: 50%;\n  left: 50%;\n  margin-top: -20px;\n  margin-left: -1.5px;\n  border-left: 1px solid #ccc;\n  border-right: 1px solid #ccc;\n}\n.custom-resizer > .multipane-resizer:hover:before {\n  border-color: #999;\n}\n.console .output-line {\n  padding-left: 16px;\n  padding-right: 16px;\n}\n.console .output-line.stdout {\n  color: #777;\n}\n.console .output-line.stderr {\n  color: #db2828;\n}\n.console .output-line:not(:last-child) {\n  border-bottom: 1px solid #eee;\n}\n.CodeMirror {\n  height: 100%;\n}\n.title.dirty:after {\n  content: '*';\n  color: #db2828;\n}\n",""])},BjUQ:function(e,t,n){var i=n("0Ima");"string"==typeof i&&(i=[[e.i,i,""]]),i.locals&&(e.exports=i.locals);(0,n("rjj0").default)("e2ae0478",i,!1,{})},Z6qg:function(e,t,n){(function(e){"use strict";var t={},n=/[^\s\u00a0]/,i=e.Pos;function o(e){var t=e.search(n);return-1==t?0:t}function l(e,t){var n=e.getMode();return!1!==n.useInnerComments&&n.innerMode?e.getModeAt(t):n}e.commands.toggleComment=function(e){e.toggleComment()},e.defineExtension("toggleComment",function(e){e||(e=t);for(var n=1/0,o=this.listSelections(),l=null,r=o.length-1;r>=0;r--){var a=o[r].from(),s=o[r].to();a.line>=n||(s.line>=n&&(s=i(n,0)),n=a.line,null==l?this.uncomment(a,s,e)?l="un":(this.lineComment(a,s,e),l="line"):"un"==l?this.uncomment(a,s,e):this.lineComment(a,s,e))}}),e.defineExtension("lineComment",function(e,r,a){a||(a=t);var s=this,c=l(s,e),u=s.getLine(e.line);if(null!=u&&(m=e,d=u,!/\bstring\b/.test(s.getTokenTypeAt(i(m.line,0)))||/^[\'\"\`]/.test(d))){var m,d,p=a.lineComment||c.lineComment;if(p){var f=Math.min(0!=r.ch||r.line==e.line?r.line+1:r.line,s.lastLine()+1),h=null==a.padding?" ":a.padding,g=a.commentBlankLines||e.line==r.line;s.operation(function(){if(a.indent){for(var t=null,l=e.line;l<f;++l){var r=(c=s.getLine(l)).slice(0,o(c));(null==t||t.length>r.length)&&(t=r)}for(l=e.line;l<f;++l){var c=s.getLine(l),u=t.length;(g||n.test(c))&&(c.slice(0,u)!=t&&(u=o(c)),s.replaceRange(t+p+h,i(l,0),i(l,u)))}}else for(l=e.line;l<f;++l)(g||n.test(s.getLine(l)))&&s.replaceRange(p+h,i(l,0))})}else(a.blockCommentStart||c.blockCommentStart)&&(a.fullLines=!0,s.blockComment(e,r,a))}}),e.defineExtension("blockComment",function(e,o,r){r||(r=t);var a=this,s=l(a,e),c=r.blockCommentStart||s.blockCommentStart,u=r.blockCommentEnd||s.blockCommentEnd;if(c&&u){if(!/\bcomment\b/.test(a.getTokenTypeAt(i(e.line,0)))){var m=Math.min(o.line,a.lastLine());m!=e.line&&0==o.ch&&n.test(a.getLine(m))&&--m;var d=null==r.padding?" ":r.padding;e.line>m||a.operation(function(){if(0!=r.fullLines){var t=n.test(a.getLine(m));a.replaceRange(d+u,i(m)),a.replaceRange(c+d,i(e.line,0));var l=r.blockCommentLead||s.blockCommentLead;if(null!=l)for(var p=e.line+1;p<=m;++p)(p!=m||t)&&a.replaceRange(l+d,i(p,0))}else a.replaceRange(u,o),a.replaceRange(c,e)})}}else(r.lineComment||s.lineComment)&&0!=r.fullLines&&a.lineComment(e,o,r)}),e.defineExtension("uncomment",function(e,o,r){r||(r=t);var a,s=this,c=l(s,e),u=Math.min(0!=o.ch||o.line==e.line?o.line:o.line-1,s.lastLine()),m=Math.min(e.line,u),d=r.lineComment||c.lineComment,p=[],f=null==r.padding?" ":r.padding;e:if(d){for(var h=m;h<=u;++h){var g=s.getLine(h),v=g.indexOf(d);if(v>-1&&!/comment/.test(s.getTokenTypeAt(i(h,v+1)))&&(v=-1),-1==v&&n.test(g))break e;if(v>-1&&n.test(g.slice(0,v)))break e;p.push(g)}if(s.operation(function(){for(var e=m;e<=u;++e){var t=p[e-m],n=t.indexOf(d),o=n+d.length;n<0||(t.slice(o,o+f.length)==f&&(o+=f.length),a=!0,s.replaceRange("",i(e,n),i(e,o)))}}),a)return!0}var C=r.blockCommentStart||c.blockCommentStart,x=r.blockCommentEnd||c.blockCommentEnd;if(!C||!x)return!1;var y=r.blockCommentLead||c.blockCommentLead,b=s.getLine(m),k=b.indexOf(C);if(-1==k)return!1;var z=u==m?b:s.getLine(u),L=z.indexOf(x,u==m?k+C.length:0),w=i(m,k+1),S=i(u,L+1);if(-1==L||!/comment/.test(s.getTokenTypeAt(w))||!/comment/.test(s.getTokenTypeAt(S))||s.getRange(w,S,"\n").indexOf(x)>-1)return!1;var R=b.lastIndexOf(C,e.ch),E=-1==R?-1:b.slice(0,e.ch).indexOf(x,R+C.length);if(-1!=R&&-1!=E&&E+x.length!=e.ch)return!1;E=z.indexOf(x,o.ch);var _=z.slice(o.ch).lastIndexOf(C,E-o.ch);return R=-1==E||-1==_?-1:o.ch+_,(-1==E||-1==R||R==o.ch)&&(s.operation(function(){s.replaceRange("",i(u,L-(f&&z.slice(L-f.length,L)==f?f.length:0)),i(u,L+x.length));var e=k+C.length;if(f&&b.slice(e,e+f.length)==f&&(e+=f.length),s.replaceRange("",i(m,k),i(m,e)),y)for(var t=m+1;t<=u;++t){var o=s.getLine(t),l=o.indexOf(y);if(-1!=l&&!n.test(o.slice(0,l))){var r=l+y.length;f&&o.slice(r,r+f.length)==f&&(r+=f.length),s.replaceRange("",i(t,l),i(t,r))}}}),!0)})})(n("8U58"))},bQT5:function(e,t,n){(function(e){function t(t){if(t.getOption("disableInput"))return e.Pass;for(var i,o=t.listSelections(),l=[],r=0;r<o.length;r++){var a=o[r].head;if(!/\bcomment\b/.test(t.getTokenTypeAt(a)))return e.Pass;var s=t.getModeAt(a);if(i){if(i!=s)return e.Pass}else i=s;var c=null;if(i.blockCommentStart&&i.blockCommentContinue){var u,m,d=(u=t.getLine(a.line).slice(0,a.ch)).lastIndexOf(i.blockCommentEnd);if(-1!=d&&d==a.ch-i.blockCommentEnd.length);else if((m=u.lastIndexOf(i.blockCommentStart))>-1&&m>d){if(c=u.slice(0,m),/\S/.test(c)){c="";for(var p=0;p<m;++p)c+=" "}}else(m=u.indexOf(i.blockCommentContinue))>-1&&!/\S/.test(u.slice(0,m))&&(c=u.slice(0,m));null!=c&&(c+=i.blockCommentContinue)}if(null==c&&i.lineComment&&n(t))(m=(u=t.getLine(a.line)).indexOf(i.lineComment))>-1&&(c=u.slice(0,m),/\S/.test(c)?c=null:c+=i.lineComment+u.slice(m+i.lineComment.length).match(/^\s*/)[0]);if(null==c)return e.Pass;l[r]="\n"+c}t.operation(function(){for(var e=o.length-1;e>=0;e--)t.replaceRange(l[e],o[e].from(),o[e].to(),"+insert")})}function n(e){var t=e.getOption("continueComments");return!t||"object"!=typeof t||!1!==t.continueLineComment}e.defineOption("continueComments",null,function(n,i,o){if(o&&o!=e.Init&&n.removeKeyMap("continueComment"),i){var l="Enter";"string"==typeof i?l=i:"object"==typeof i&&i.key&&(l=i.key);var r={name:"continueComment"};r[l]=t,n.addKeyMap(r)}})})(n("8U58"))},uzIl:function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var i={name:"multipane",props:{layout:{type:String,default:"vertical"}},data:function(){return{isResizing:!1}},computed:{classnames:function(){return["multipane","layout-"+this.layout.slice(0,1),this.isResizing?"is-resizing":""]},cursor:function(){return this.isResizing?"vertical"==this.layout?"col-resize":"row-resize":""},userSelect:function(){return this.isResizing?"none":""}},methods:{onMouseDown:function(e){var t=e.target,n=e.pageX,i=e.pageY;if(t.className&&t.className.match("multipane-resizer")){var o=this,l=o.$el,r=o.layout,a=t.previousElementSibling,s=a.offsetWidth,c=a.offsetHeight,u=!!(a.style.width+"").match("%"),m=window.addEventListener,d=window.removeEventListener,p=function(e,t){if(void 0===t&&(t=0),"vertical"==r){var n=l.clientWidth,i=e+t;return a.style.width=u?i/n*100+"%":i+"px"}if("horizontal"==r){var o=l.clientHeight,s=e+t;return a.style.height=u?s/o*100+"%":s+"px"}};o.isResizing=!0;var f=p();o.$emit("paneResizeStart",a,t,f);var h=function(e){var l=e.pageX,u=e.pageY;f="vertical"==r?p(s,l-n):p(c,u-i),o.$emit("paneResize",a,t,f)},g=function(){f=p("vertical"==r?a.clientWidth:a.clientHeight),o.isResizing=!1,d("mousemove",h),d("mouseup",g),o.$emit("paneResizeStop",a,t,f)};m("mousemove",h),m("mouseup",g)}}}};!function(){if("undefined"!=typeof document){var e=document.head||document.getElementsByTagName("head")[0],t=document.createElement("style"),n=".multipane { display: flex; } .multipane.layout-h { flex-direction: column; } .multipane.layout-v { flex-direction: row; } .multipane > div { position: relative; z-index: 1; } .multipane-resizer { display: block; position: relative; z-index: 2; } .layout-h > .multipane-resizer { width: 100%; height: 10px; margin-top: -10px; top: 5px; cursor: row-resize; } .layout-v > .multipane-resizer { width: 10px; height: 100%; margin-left: -10px; left: 5px; cursor: col-resize; } ";t.type="text/css",t.styleSheet?t.styleSheet.cssText=n:t.appendChild(document.createTextNode(n)),e.appendChild(t)}}();var o=Object.assign(i,{render:function(){var e=this,t=e.$createElement;return(e._self._c||t)("div",{class:e.classnames,style:{cursor:e.cursor,userSelect:e.userSelect},on:{mousedown:e.onMouseDown}},[e._t("default")],2)},staticRenderFns:[]});o.prototype=i.prototype,function(){if("undefined"!=typeof document){var e=document.head||document.getElementsByTagName("head")[0],t=document.createElement("style");t.type="text/css",t.styleSheet?t.styleSheet.cssText="":t.appendChild(document.createTextNode("")),e.appendChild(t)}}();var l={render:function(){var e=this,t=e.$createElement;return(e._self._c||t)("div",{staticClass:"multipane-resizer"},[e._t("default")],2)},staticRenderFns:[]};"undefined"!=typeof window&&window.Vue&&(window.Vue.component("multipane",o),window.Vue.component("multipane-resizer",l));var r=n("E5Az"),a=(n("4/hK"),n("5IAE"),n("vq+x"),n("aX1R"),n("bQT5"),n("Z6qg"),{name:"PageText",components:{codemirror:r.codemirror,Multipane:o,MultipaneResizer:l},data:function(){var e=this;return{content:"",cmOption:{mode:"application/javascript",tabSize:4,styleActiveLine:!0,lineNumbers:!0,lineWrapping:!1,foldGutter:!0,styleSelectedText:!0,matchBrackets:!0,autoCloseBrackets:!0,showCursorWhenSelecting:!0,extraKeys:{Ctrl:"autocomplete","Ctrl-S":function(){e.save()}},hintOptions:{completeSingle:!1},viewportMargin:1/0},loading:!0,saveLoading:!1,exeLoading:!1,dirty:!1,console:{output:[]},orientation:this.$q.platform.is.mobile?"horizontal":"vertical"}},computed:{resource:function(){var e=this.$route.params.id,t=this.$store.getters["ething/get"](e);return e&&e.length&&(t||this.$router.replace("/404")),t}},methods:{codemirror:function(){return this.$refs.cm.codemirror},markClean:function(){this.dirty=!1,this.codemirror().markClean()},reloadContent:function(){var e=this;this.loading=!0,this.resource.read().then(function(t){e.content=t,e.$nextTick(function(){e.markClean(),e.codemirror().clearHistory()})}).finally(function(){e.loading=!1})},save:function(e){var t=this;this.saveLoading=!0,this.resource.write(this.content).then(function(){t.dirty=!1,t.markClean(),"function"==typeof e&&e()}).finally(function(){t.saveLoading=!1})},onChange:function(e,t){this.dirty=!e.isClean()},execute:function(){var e=this;this.exeLoading=!0,this.resource.execute().then(function(t){console.log(t),e.printResult(t)}).finally(function(){e.exeLoading=!1})},onExecuteClick:function(){this.dirty?this.save(this.execute):this.execute()},printResult:function(e){this.console.output=e.output}},mounted:function(){this.reloadContent()}}),s=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("q-page",[n("multipane",{staticClass:"absolute fit",class:"vertical"==e.orientation?"vertical-panes":"horizontal-panes",attrs:{layout:e.orientation}},[n("div",{staticClass:"pane",style:"vertical"==e.orientation?{width:"50%",maxWidth:"75%"}:{height:"50%",maxHeight:"75%"}},[n("q-btn-group",{attrs:{flat:""}},[n("q-btn",{attrs:{loading:e.saveLoading,label:"save",icon:"mdi-content-save-outline"},on:{click:e.save}}),e._v(" "),n("q-btn",{attrs:{loading:e.exeLoading,label:"run",icon:"play_arrow"},on:{click:e.onExecuteClick}})],1),e._v(" "),n("span",{staticClass:"title text-faded",class:{dirty:e.dirty}},[e._v(e._s(e.resource.name()))]),e._v(" "),n("codemirror",{ref:"cm",attrs:{options:e.cmOption},on:{changes:e.onChange},model:{value:e.content,callback:function(t){e.content=t},expression:"content"}})],1),e._v(" "),n("multipane-resizer"),e._v(" "),n("div",{staticClass:"pane console",style:{flexGrow:1}},[e.exeLoading?n("div",{staticClass:"absolute-center text-faded"},[e._v("\n        running ...\n      ")]):n("div",{staticClass:"absolute fit"},[n("div",{staticClass:"output"},e._l(e.console.output,function(t,i){return n("div",{key:i,staticClass:"output-line",class:t.type},[n("pre",{staticClass:"q-ma-none"},[n("code",[e._v(e._s(t.chunk))])])])}))])])],1)],1)},c=[];s._withStripped=!0;var u=n("XyMi"),m=!1;var d=function(e){m||n("BjUQ")},p=Object(u.a)(a,s,c,!1,d,null,null);p.options.__file="src\\pages\\Script.vue";t.default=p.exports}});