(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[6],{"25Eh":function(e,t,n){(function(e){e(n("VrN/"))})(function(e){"use strict";function t(e){return new RegExp("^(("+e.join(")|(")+"))\\b")}var n=t(["and","or","not","is"]),i=["as","assert","break","class","continue","def","del","elif","else","except","finally","for","from","global","if","import","lambda","pass","raise","return","try","while","with","yield","in"],r=["abs","all","any","bin","bool","bytearray","callable","chr","classmethod","compile","complex","delattr","dict","dir","divmod","enumerate","eval","filter","float","format","frozenset","getattr","globals","hasattr","hash","help","hex","id","input","int","isinstance","issubclass","iter","len","list","locals","map","max","memoryview","min","next","object","oct","open","ord","pow","property","range","repr","reversed","round","set","setattr","slice","sorted","staticmethod","str","sum","super","tuple","type","vars","zip","__import__","NotImplemented","Ellipsis","__debug__"];function a(e){return e.scopes[e.scopes.length-1]}e.registerHelper("hintWords","python",i.concat(r)),e.defineMode("python",function(o,l){for(var s="error",c=l.delimiters||l.singleDelimiters||/^[\(\)\[\]\{\}@,:`=;\.\\]/,u=[l.singleOperators,l.doubleOperators,l.doubleDelimiters,l.tripleDelimiters,l.operators||/^([-+*/%\/&|^]=?|[<>=]+|\/\/=?|\*\*=?|!=|[~!@])/],f=0;f<u.length;f++)u[f]||u.splice(f--,1);var m=l.hangingIndent||o.indentUnit,d=i,p=r;void 0!=l.extra_keywords&&(d=d.concat(l.extra_keywords)),void 0!=l.extra_builtins&&(p=p.concat(l.extra_builtins));var h=!(l.version&&Number(l.version)<3);if(h){var g=l.identifiers||/^[_A-Za-z\u00A1-\uFFFF][_A-Za-z0-9\u00A1-\uFFFF]*/;d=d.concat(["nonlocal","False","True","None","async","await"]),p=p.concat(["ascii","bytes","exec","print"]);var v=new RegExp("^(([rbuf]|(br)|(fr))?('{3}|\"{3}|['\"]))","i")}else{g=l.identifiers||/^[_A-Za-z][_A-Za-z0-9]*/;d=d.concat(["exec","print"]),p=p.concat(["apply","basestring","buffer","cmp","coerce","execfile","file","intern","long","raw_input","reduce","reload","unichr","unicode","xrange","False","True","None"]);v=new RegExp("^(([rubf]|(ur)|(br))?('{3}|\"{3}|['\"]))","i")}var b=t(d),y=t(p);function k(e,t){var n=e.sol()&&"\\"!=t.lastToken;if(n&&(t.indent=e.indentation()),n&&"py"==a(t).type){var i=a(t).offset;if(e.eatSpace()){var r=e.indentation();return r>i?w(t):r<i&&S(e,t)&&"#"!=e.peek()&&(t.errorToken=!0),null}var o=C(e,t);return i>0&&S(e,t)&&(o+=" "+s),o}return C(e,t)}function C(e,t){if(e.eatSpace())return null;if(e.match(/^#.*/))return"comment";if(e.match(/^[0-9\.]/,!1)){var i=!1;if(e.match(/^[\d_]*\.\d+(e[\+\-]?\d+)?/i)&&(i=!0),e.match(/^[\d_]+\.\d*/)&&(i=!0),e.match(/^\.\d+/)&&(i=!0),i)return e.eat(/J/i),"number";var r=!1;if(e.match(/^0x[0-9a-f_]+/i)&&(r=!0),e.match(/^0b[01_]+/i)&&(r=!0),e.match(/^0o[0-7_]+/i)&&(r=!0),e.match(/^[1-9][\d_]*(e[\+\-]?[\d_]+)?/)&&(e.eat(/J/i),r=!0),e.match(/^0(?![\dx])/i)&&(r=!0),r)return e.eat(/L/i),"number"}if(e.match(v)){var a=-1!==e.current().toLowerCase().indexOf("f");return a?(t.tokenize=x(e.current(),t.tokenize),t.tokenize(e,t)):(t.tokenize=L(e.current()),t.tokenize(e,t))}for(var o=0;o<u.length;o++)if(e.match(u[o]))return"operator";return e.match(c)?"punctuation":"."==t.lastToken&&e.match(g)?"property":e.match(b)||e.match(n)?"keyword":e.match(y)?"builtin":e.match(/^(self|cls)\b/)?"variable-2":e.match(g)?"def"==t.lastToken||"class"==t.lastToken?"def":"variable":(e.next(),s)}function x(e,t){while("rubf".indexOf(e.charAt(0).toLowerCase())>=0)e=e.substr(1);var n=1==e.length,i="string";function r(t,n){return t.match(e)?(n.tokenize=a,i):t.match("{")?"punctuation":t.match("}")?(n.tokenize=a,"punctuation"):C(t,n)}function a(a,o){while(!a.eol())if(a.eatWhile(/[^'"\{\}\\]/),a.eat("\\")){if(a.next(),n&&a.eol())return i}else{if(a.match(e))return o.tokenize=t,i;if(a.match("{{"))return i;if(a.match("{",!1))return o.tokenize=r,a.current()?i:(a.next(),"punctuation");if(a.match("}}"))return i;if(a.match("}"))return s;a.eat(/['"]/)}if(n){if(l.singleLineStringErrors)return s;o.tokenize=t}return i}return a.isString=!0,a}function L(e){while("rubf".indexOf(e.charAt(0).toLowerCase())>=0)e=e.substr(1);var t=1==e.length,n="string";function i(i,r){while(!i.eol())if(i.eatWhile(/[^'"\\]/),i.eat("\\")){if(i.next(),t&&i.eol())return n}else{if(i.match(e))return r.tokenize=k,n;i.eat(/['"]/)}if(t){if(l.singleLineStringErrors)return s;r.tokenize=k}return n}return i.isString=!0,i}function w(e){while("py"!=a(e).type)e.scopes.pop();e.scopes.push({offset:a(e).offset+o.indentUnit,type:"py",align:null})}function O(e,t,n){var i=e.match(/^([\s\[\{\(]|#.*)*$/,!1)?null:e.column()+1;t.scopes.push({offset:t.indent+m,type:n,align:i})}function S(e,t){var n=e.indentation();while(t.scopes.length>1&&a(t).offset>n){if("py"!=a(t).type)return!0;t.scopes.pop()}return a(t).offset!=n}function T(e,t){e.sol()&&(t.beginningOfLine=!0);var n=t.tokenize(e,t),i=e.current();if(t.beginningOfLine&&"@"==i)return e.match(g,!1)?"meta":h?"operator":s;if(/\S/.test(i)&&(t.beginningOfLine=!1),"variable"!=n&&"builtin"!=n||"meta"!=t.lastToken||(n="meta"),"pass"!=i&&"return"!=i||(t.dedent+=1),"lambda"==i&&(t.lambda=!0),":"!=i||t.lambda||"py"!=a(t).type||w(t),1==i.length&&!/string|comment/.test(n)){var r="[({".indexOf(i);if(-1!=r&&O(e,t,"])}".slice(r,r+1)),r="])}".indexOf(i),-1!=r){if(a(t).type!=i)return s;t.indent=t.scopes.pop().offset-m}}return t.dedent>0&&e.eol()&&"py"==a(t).type&&(t.scopes.length>1&&t.scopes.pop(),t.dedent-=1),n}var _={startState:function(e){return{tokenize:k,scopes:[{offset:e||0,type:"py",align:null}],indent:e||0,lastToken:null,lambda:!1,dedent:0}},token:function(e,t){var n=t.errorToken;n&&(t.errorToken=!1);var i=T(e,t);return i&&"comment"!=i&&(t.lastToken="keyword"==i||"punctuation"==i?e.current():i),"punctuation"==i&&(i=null),e.eol()&&t.lambda&&(t.lambda=!1),n?i+" "+s:i},indent:function(t,n){if(t.tokenize!=k)return t.tokenize.isString?e.Pass:0;var i=a(t),r=i.type==n.charAt(0);return null!=i.align?i.align-(r?1:0):i.offset-(r?m:0)},electricInput:/^\s*[\}\]\)]$/,closeBrackets:{triples:"'\""},lineComment:"#",fold:"indent"};return _}),e.defineMIME("text/x-python","python");var o=function(e){return e.split(" ")};e.defineMIME("text/x-cython",{name:"python",extra_keywords:o("by cdef cimport cpdef ctypedef enum except extern gil include nogil property public readonly struct union DEF IF ELIF ELSE")})})},"3TLe":function(e,t,n){},"Mcf+":function(e,t,n){"use strict";var i=n("3TLe"),r=n.n(i);r.a},NO8f:function(e,t,n){n("7DDg")("Uint8",1,function(e){return function(t,n,i){return e(this,t,n,i)}})},a8ks:function(e,t,n){(function(e){e(n("VrN/"))})(function(e){function t(t){if(t.getOption("disableInput"))return e.Pass;for(var i,r=t.listSelections(),a=[],o=0;o<r.length;o++){var l=r[o].head;if(!/\bcomment\b/.test(t.getTokenTypeAt(l)))return e.Pass;var s=t.getModeAt(l);if(i){if(i!=s)return e.Pass}else i=s;var c=null;if(i.blockCommentStart&&i.blockCommentContinue){var u=t.getLine(l.line).slice(0,l.ch),f=u.lastIndexOf(i.blockCommentEnd);if(-1!=f&&f==l.ch-i.blockCommentEnd.length);else if((d=u.lastIndexOf(i.blockCommentStart))>-1&&d>f){if(c=u.slice(0,d),/\S/.test(c)){c="";for(var m=0;m<d;++m)c+=" "}}else(d=u.indexOf(i.blockCommentContinue))>-1&&!/\S/.test(u.slice(0,d))&&(c=u.slice(0,d));null!=c&&(c+=i.blockCommentContinue)}if(null==c&&i.lineComment&&n(t)){u=t.getLine(l.line);var d=u.indexOf(i.lineComment);d>-1&&(c=u.slice(0,d),/\S/.test(c)?c=null:c+=i.lineComment+u.slice(d+i.lineComment.length).match(/^\s*/)[0])}if(null==c)return e.Pass;a[o]="\n"+c}t.operation(function(){for(var e=r.length-1;e>=0;e--)t.replaceRange(a[e],r[e].from(),r[e].to(),"+insert")})}function n(e){var t=e.getOption("continueComments");return!t||"object"!=typeof t||!1!==t.continueLineComment}e.defineOption("continueComments",null,function(n,i,r){if(r&&r!=e.Init&&n.removeKeyMap("continueComment"),i){var a="Enter";"string"==typeof i?a=i:"object"==typeof i&&i.key&&(a=i.key);var o={name:"continueComment"};o[a]=t,n.addKeyMap(o)}})})},cokd:function(e,t,n){(function(e){e(n("VrN/"))})(function(e){"use strict";var t={},n=/[^\s\u00a0]/,i=e.Pos;function r(e){var t=e.search(n);return-1==t?0:t}function a(e,t,n){return/\bstring\b/.test(e.getTokenTypeAt(i(t.line,0)))&&!/^[\'\"\`]/.test(n)}function o(e,t){var n=e.getMode();return!1!==n.useInnerComments&&n.innerMode?e.getModeAt(t):n}e.commands.toggleComment=function(e){e.toggleComment()},e.defineExtension("toggleComment",function(e){e||(e=t);for(var n=this,r=1/0,a=this.listSelections(),o=null,l=a.length-1;l>=0;l--){var s=a[l].from(),c=a[l].to();s.line>=r||(c.line>=r&&(c=i(r,0)),r=s.line,null==o?n.uncomment(s,c,e)?o="un":(n.lineComment(s,c,e),o="line"):"un"==o?n.uncomment(s,c,e):n.lineComment(s,c,e))}}),e.defineExtension("lineComment",function(e,l,s){s||(s=t);var c=this,u=o(c,e),f=c.getLine(e.line);if(null!=f&&!a(c,e,f)){var m=s.lineComment||u.lineComment;if(m){var d=Math.min(0!=l.ch||l.line==e.line?l.line+1:l.line,c.lastLine()+1),p=null==s.padding?" ":s.padding,h=s.commentBlankLines||e.line==l.line;c.operation(function(){if(s.indent){for(var t=null,a=e.line;a<d;++a){var o=c.getLine(a),l=o.slice(0,r(o));(null==t||t.length>l.length)&&(t=l)}for(a=e.line;a<d;++a){o=c.getLine(a);var u=t.length;(h||n.test(o))&&(o.slice(0,u)!=t&&(u=r(o)),c.replaceRange(t+m+p,i(a,0),i(a,u)))}}else for(a=e.line;a<d;++a)(h||n.test(c.getLine(a)))&&c.replaceRange(m+p,i(a,0))})}else(s.blockCommentStart||u.blockCommentStart)&&(s.fullLines=!0,c.blockComment(e,l,s))}}),e.defineExtension("blockComment",function(e,r,a){a||(a=t);var l=this,s=o(l,e),c=a.blockCommentStart||s.blockCommentStart,u=a.blockCommentEnd||s.blockCommentEnd;if(c&&u){if(!/\bcomment\b/.test(l.getTokenTypeAt(i(e.line,0)))){var f=Math.min(r.line,l.lastLine());f!=e.line&&0==r.ch&&n.test(l.getLine(f))&&--f;var m=null==a.padding?" ":a.padding;e.line>f||l.operation(function(){if(0!=a.fullLines){var t=n.test(l.getLine(f));l.replaceRange(m+u,i(f)),l.replaceRange(c+m,i(e.line,0));var o=a.blockCommentLead||s.blockCommentLead;if(null!=o)for(var d=e.line+1;d<=f;++d)(d!=f||t)&&l.replaceRange(o+m,i(d,0))}else l.replaceRange(u,r),l.replaceRange(c,e)})}}else(a.lineComment||s.lineComment)&&0!=a.fullLines&&l.lineComment(e,r,a)}),e.defineExtension("uncomment",function(e,r,a){a||(a=t);var l,s=this,c=o(s,e),u=Math.min(0!=r.ch||r.line==e.line?r.line:r.line-1,s.lastLine()),f=Math.min(e.line,u),m=a.lineComment||c.lineComment,d=[],p=null==a.padding?" ":a.padding;e:if(m){for(var h=f;h<=u;++h){var g=s.getLine(h),v=g.indexOf(m);if(v>-1&&!/comment/.test(s.getTokenTypeAt(i(h,v+1)))&&(v=-1),-1==v&&n.test(g))break e;if(v>-1&&n.test(g.slice(0,v)))break e;d.push(g)}if(s.operation(function(){for(var e=f;e<=u;++e){var t=d[e-f],n=t.indexOf(m),r=n+m.length;n<0||(t.slice(r,r+p.length)==p&&(r+=p.length),l=!0,s.replaceRange("",i(e,n),i(e,r)))}}),l)return!0}var b=a.blockCommentStart||c.blockCommentStart,y=a.blockCommentEnd||c.blockCommentEnd;if(!b||!y)return!1;var k=a.blockCommentLead||c.blockCommentLead,C=s.getLine(f),x=C.indexOf(b);if(-1==x)return!1;var L=u==f?C:s.getLine(u),w=L.indexOf(y,u==f?x+b.length:0),O=i(f,x+1),S=i(u,w+1);if(-1==w||!/comment/.test(s.getTokenTypeAt(O))||!/comment/.test(s.getTokenTypeAt(S))||s.getRange(O,S,"\n").indexOf(y)>-1)return!1;var T=C.lastIndexOf(b,e.ch),_=-1==T?-1:C.slice(0,e.ch).indexOf(y,T+b.length);if(-1!=T&&-1!=_&&_+y.length!=e.ch)return!1;_=L.indexOf(y,r.ch);var M=L.slice(r.ch).lastIndexOf(b,_-r.ch);return T=-1==_||-1==M?-1:r.ch+M,(-1==_||-1==T||T==r.ch)&&(s.operation(function(){s.replaceRange("",i(u,w-(p&&L.slice(w-p.length,w)==p?p.length:0)),i(u,w+y.length));var e=x+b.length;if(p&&C.slice(e,e+p.length)==p&&(e+=p.length),s.replaceRange("",i(f,x),i(f,e)),k)for(var t=f+1;t<=u;++t){var r=s.getLine(t),a=r.indexOf(k);if(-1!=a&&!n.test(r.slice(0,a))){var o=a+k.length;p&&r.slice(o,o+p.length)==p&&(o+=p.length),s.replaceRange("",i(t,a),i(t,o))}}}),!0)})})},xItC:function(e,t,n){"use strict";n.r(t);var i=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("q-page",[n("q-btn-group",{attrs:{flat:""}},[n("q-btn",{attrs:{loading:e.saveLoading,label:"save",icon:"mdi-content-save-outline"},on:{click:e.save}}),n("q-btn-dropdown",{attrs:{label:e.langage}},[n("q-list",{attrs:{link:""}},e._l(e.langages,function(t,i,r){return n("q-item",{directives:[{name:"close-overlay",rawName:"v-close-overlay"}],key:i,nativeOn:{click:function(t){e.setLangage(i)}}},[n("q-item-main",[n("q-item-tile",{attrs:{label:""}},[e._v(e._s(i))])],1)],1)}))],1)],1),n("span",{staticClass:"title text-faded",class:{dirty:e.dirty}},[e._v(e._s(e.resource.name()))]),n("codemirror",{ref:"cm",attrs:{options:e.cmOption},on:{changes:e.onChange},model:{value:e.content,callback:function(t){e.content=t},expression:"content"}})],1)},r=[];i._withStripped=!0;n("NO8f"),n("pIFo");var a=n("Ezub"),o=n("j5TT"),l=(n("p77/"),n("+dQi"),n("ztCB"),n("25Eh"),n("jDMi"),n("ELLl"),n("a8ks"),n("cokd"),{name:"PageText",components:{codemirror:o["codemirror"]},data:function(){var e=this;return{content:"",contentDate:null,warnedContentDate:null,contentModifiedNotification:null,cmOption:{mode:"text/plain",tabSize:4,styleActiveLine:!0,lineNumbers:!0,lineWrapping:!1,foldGutter:!0,styleSelectedText:!0,matchBrackets:!0,autoCloseBrackets:!0,showCursorWhenSelecting:!0,extraKeys:{Ctrl:"autocomplete","Ctrl-S":function(){e.save()}},hintOptions:{completeSingle:!1},viewportMargin:1/0},loading:!0,saveLoading:!1,langages:{text:"text/plain",javascript:["text/javascript","application/javascript"],yaml:["text/x-yaml","application/x-yaml"],json:"application/json",python:"text/x-python"},langage:"text",dirty:!1}},computed:{resource:function(){var e=this.$route.params.id,t=this.$store.getters["ething/get"](e);return e&&e.length&&(t||this.$router.replace("/404")),t}},watch:{resource:{handler:function(e){var t=e.contentModifiedDate();this.contentDate&&t>this.contentDate&&t.getTime()!=this.warnedContentDate&&(this.warnedContentDate=t.getTime(),console.log("the content has been updated !"),this.dirty?(this.contentModifiedNotification&&(this.contentModifiedNotification(),this.contentModifiedNotification=null),this.contentModifiedNotification=a["a"].create({message:"The content of this file has changed in the server and differ from your current version !",timeout:5e4,type:"negative"})):this.reloadContent())},immediate:!0},contentDate:function(e){null===e&&this.contentModifiedNotification&&(this.contentModifiedNotification(),this.contentModifiedNotification=null)}},methods:{codemirror:function(){return this.$refs["cm"].codemirror},markClean:function(){this.dirty=!1,this.codemirror().markClean()},reloadContent:function(){var e=this;this.loading=!0,this.contentDate=null,this.resource.read(!0).then(function(t){e.setLangage(e.resource.mime()),e.content=String.fromCharCode.apply(null,new Uint8Array(t)),e.contentDate=e.resource.contentModifiedDate(),e.$nextTick(function(){e.markClean(),e.codemirror().clearHistory()})}).finally(function(){e.loading=!1})},setLangage:function(e){if(console.log("setLangage = "+e),/^[^\/]+\/[^\/]+$/.test(e))for(var t in this.langages)if(Array.isArray(this.langages[t])?-1!==this.langages[t].indexOf(e):this.langages[t]===e)return this.cmOption.mode=Array.isArray(this.langages[t])?this.langages[t][0]:e,void(this.langage=t);this.langages[e]||(e="text"),this.cmOption.mode=this.langages[e],this.langage=e},save:function(){var e=this;this.saveLoading=!0,this.contentDate=null,this.resource.write(this.content).then(function(){e.contentDate=e.resource.contentModifiedDate(),e.dirty=!1,e.markClean()}).finally(function(){e.saveLoading=!1})},onChange:function(e,t){this.dirty=!e.isClean()}},mounted:function(){this.reloadContent()}}),s=l,c=(n("Mcf+"),n("KHd+")),u=Object(c["a"])(s,i,r,!1,null,null,null);u.options.__file="Text.vue";t["default"]=u.exports},ztCB:function(e,t,n){(function(e){e(n("VrN/"))})(function(e){"use strict";e.defineMode("yaml",function(){var e=["true","false","on","off","yes","no"],t=new RegExp("\\b(("+e.join(")|(")+"))$","i");return{token:function(e,n){var i=e.peek(),r=n.escaped;if(n.escaped=!1,"#"==i&&(0==e.pos||/\s/.test(e.string.charAt(e.pos-1))))return e.skipToEnd(),"comment";if(e.match(/^('([^']|\\.)*'?|"([^"]|\\.)*"?)/))return"string";if(n.literal&&e.indentation()>n.keyCol)return e.skipToEnd(),"string";if(n.literal&&(n.literal=!1),e.sol()){if(n.keyCol=0,n.pair=!1,n.pairStart=!1,e.match(/---/))return"def";if(e.match(/\.\.\./))return"def";if(e.match(/\s*-\s+/))return"meta"}if(e.match(/^(\{|\}|\[|\])/))return"{"==i?n.inlinePairs++:"}"==i?n.inlinePairs--:"["==i?n.inlineList++:n.inlineList--,"meta";if(n.inlineList>0&&!r&&","==i)return e.next(),"meta";if(n.inlinePairs>0&&!r&&","==i)return n.keyCol=0,n.pair=!1,n.pairStart=!1,e.next(),"meta";if(n.pairStart){if(e.match(/^\s*(\||\>)\s*/))return n.literal=!0,"meta";if(e.match(/^\s*(\&|\*)[a-z0-9\._-]+\b/i))return"variable-2";if(0==n.inlinePairs&&e.match(/^\s*-?[0-9\.\,]+\s?$/))return"number";if(n.inlinePairs>0&&e.match(/^\s*-?[0-9\.\,]+\s?(?=(,|}))/))return"number";if(e.match(t))return"keyword"}return!n.pair&&e.match(/^\s*(?:[,\[\]{}&*!|>'"%@`][^\s'":]|[^,\[\]{}#&*!|>'"%@`])[^#]*?(?=\s*:($|\s))/)?(n.pair=!0,n.keyCol=e.indentation(),"atom"):n.pair&&e.match(/^:\s*/)?(n.pairStart=!0,"meta"):(n.pairStart=!1,n.escaped="\\"==i,e.next(),null)},startState:function(){return{pair:!1,pairStart:!1,keyCol:0,inlinePairs:0,inlineList:0,literal:!1,escaped:!1}},lineComment:"#",fold:"indent"}}),e.defineMIME("text/x-yaml","yaml"),e.defineMIME("text/yaml","yaml")})}}]);