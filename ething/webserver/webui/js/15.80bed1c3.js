(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[15],{GeLR:function(M,e,t){"use strict";t.r(e);var i=function(){var M=this,e=M.$createElement,i=M._self._c||e;return i("q-page",{attrs:{padding:""}},[i("div",{staticClass:"row justify-between"},[i("div",[i("q-btn",{attrs:{label:"All",flat:"",rounded:"",color:"faded"},on:{click:function(e){M.category=""}}}),i("q-btn",{attrs:{label:"Sensor",flat:"",rounded:"",color:"faded"},on:{click:function(e){M.category="sensor"}}}),i("q-btn",{attrs:{label:"Switch/Light",flat:"",rounded:"",color:"faded"},on:{click:function(e){M.category="switch"}}}),i("q-btn",{attrs:{label:"Camera",flat:"",rounded:"",color:"faded"},on:{click:function(e){M.category="camera"}}})],1),i("div",{staticClass:"row"},[i("q-btn-dropdown",{attrs:{color:"primary",label:"Create",icon:"add",flat:""}},[i("q-list",{attrs:{link:""}},[M._l(M.categories,function(e){return[i("q-list-header",{attrs:{inset:""}},[M._v(M._s(e.name))]),M._l(e.types,function(e){return i("q-item",{directives:[{name:"close-overlay",rawName:"v-close-overlay"}],key:e.type,nativeOn:{click:function(t){M.create(e.name)}}},[i("q-item-side",{attrs:{icon:M.$meta.get(e.type).icon,color:M.$meta.get(e.type).color}}),i("q-item-main",[i("q-item-tile",{attrs:{label:""}},[M._v(M._s(e.label))])],1)],1)})]})],2)],1)],1)]),M.listOrdered.length?i("div",[i("q-list",{attrs:{link:"","no-border":""}},M._l(M.deviceFiltered,function(M,e){return i("resource-q-item",{key:e,attrs:{resource:M.device,level:M.level,"no-parent":""}})}))],1):i("div",{staticClass:"absolute-center text-center"},[i("p",[i("img",{staticStyle:{width:"30vw","max-width":"150px"},attrs:{src:t("xOSM")}})]),i("p",{staticClass:"text-faded"},[M._v("No devices installed")])])])},j=[];i._withStripped=!0;t("Oyvg"),t("91GP"),t("f3/d"),t("yt8O"),t("RW0V"),t("rGqo");var u=t("QmqO"),g=t.n(u),I=t("ZlnI"),A={name:"PageDevices",components:{ResourceQItem:I["a"]},data:function(){var M={},e=this.$meta.definitions.resources;Object.keys(e).forEach(function(t){var i=e[t];if(-1!==i.inheritances.indexOf("resources/Device")&&!i.virtual&&!i.disableCreation){var j=i.path||[],u=i.label||t,g=j.length>0?j[0]:"other";M[g]||(M[g]={types:[]}),M[g].types.push({label:u,name:t,type:"resources/"+t})}});var t=M["other"],i=[];for(var j in delete M["other"],M)i.push(Object.assign({name:j},M[j]));return i.push(Object.assign({name:"other"},t)),{categories:i,filter:"",category:""}},computed:{devices:function(){var M=this;return this.$store.getters["ething/filter"](function(e){return e instanceof M.$ething.Device})},listOrdered:function(){var M=[],e=this;function t(M){return e.$store.getters["ething/filter"](function(e){return e.createdBy()===M.id()&&e instanceof g.a.Device})}function i(M){return!!M.createdBy()}var j=0;function u(M){return{device:M,level:j,indent:20*j}}function I(M){var e=[u(M)];return j++,t(M).map(function(M){e=e.concat(I(M))}),j--,e}return this.devices.filter(function(M){return!i(M)}).forEach(function(e){M=M.concat(I(e))}),M},deviceFiltered:function(){if(this.category||this.filter){var M=this.devices;if(this.category)switch(this.category){case"sensor":M=M.filter(function(M){return M.isTypeof("interfaces/Sensor")});break;case"switch":M=M.filter(function(M){return M.isTypeof("interfaces/Switch")});break;case"camera":M=M.filter(function(M){return M.isTypeof("interfaces/Camera")});break}return this.filter&&(M=this.applyFilter(M)),M.map(function(M){return{device:M,level:0}})}return this.listOrdered}},methods:{create:function(M){this.$router.push("/create/"+M)},applyFilter:function(M){if(this.filter){var e=new RegExp(this.filter);M=M.filter(function(M){return e.test(M.name())||e.test(M.id())})}return M}}},N=A,r=t("KHd+"),D=Object(r["a"])(N,i,j,!1,null,null,null);e["default"]=D.exports},ZlnI:function(M,e,t){"use strict";var i=function(){var M=this,e=M.$createElement,t=M._self._c||e;return t("q-item",{staticClass:"item",attrs:{link:!M.readonly},nativeOn:{click:function(e){M.open(M.resource)}}},[M._l(M.level,function(e){return t("div",{class:M.gen(e)})}),t("q-item-side",{attrs:{icon:M.$meta.get(M.resource).icon,inverted:"",color:M.$meta.get(M.resource).color}}),t("q-item-main",[t("q-item-tile",{attrs:{label:""}},[t("span",{staticClass:"vertical-middle text-black"},[M._v(M._s(M.resource.basename()))]),M.showParent?t("small",{staticClass:"parent text-faded vertical-bottom on-right",class:M.readonly?"":"cursor-pointer",on:{click:function(e){e.stopPropagation(),M.open(M.createdBy)}}},[M._v(M._s(M.createdBy.basename()))]):M._e(),M.showConnected&&!M.resource.connected()?t("q-icon",{staticClass:"vertical-middle on-right",attrs:{name:"mdi-lan-disconnect",color:"warning"}}):M._e(),M.resource.public()?t("q-icon",{staticClass:"vertical-middle on-right",attrs:{name:"share",color:"warning"}}):M._e()],1),t("q-item-tile",{attrs:{sublabel:""}},[M._v(M._s(M.$ui.dateToString(M.date)))]),M.showType?t("q-item-tile",{attrs:{sublabel:""}},[M._v(M._s(M.resource.type().replace("resources/","")))]):M._e(),M.showBattery?t("q-item-tile",{staticClass:"lt-sm",attrs:{sublabel:""}},[M._v("battery: "+M._s(M.resource.battery())+"%")]):M._e(),M.showLocation?t("q-item-tile",{staticClass:"lt-sm",attrs:{sublabel:""}},[M._v("location: "+M._s(M.resource.location()))]):M._e(),M.showSize?t("q-item-tile",{attrs:{sublabel:""}},[M._v(M._s(M.$ui.sizeToString(M.resource.size())))]):M._e(),M.showLength?t("q-item-tile",{attrs:{sublabel:""}},[M._v(M._s(M.resource.length())+" rows")]):M._e()],1),M.showLocation?t("q-item-side",{staticClass:"gt-xs",attrs:{right:""}},[t("q-chip",{attrs:{small:"",detail:"",icon:"location_on"}},[M._v("\n      "+M._s(M.resource.location())+"\n    ")])],1):M._e(),M.showBattery?t("q-item-side",{staticClass:"gt-xs",attrs:{right:""}},[t("resource-battery-chip",{attrs:{resource:M.resource}})],1):M._e(),M.readonly?M._e():[M.showChart?t("q-item-side",{staticClass:"gt-xs",attrs:{right:""}},[t("q-btn",{attrs:{icon:"mdi-chart-line",round:"",flat:"",dense:"",color:"secondary"},on:{click:function(e){return e.stopPropagation(),M.chart(e)}}})],1):M._e(),M.showDownload?t("q-item-side",{staticClass:"gt-xs",attrs:{right:""}},[t("q-btn",{attrs:{icon:"cloud_download",round:"",flat:"",dense:"",color:"secondary"},on:{click:function(e){return e.stopPropagation(),M.download(e)}}})],1):M._e(),t("q-item-side",{staticClass:"gt-xs",attrs:{right:""}},[t("q-btn",{attrs:{icon:"delete",round:"",flat:"",dense:"",color:"negative"},on:{click:function(e){return e.stopPropagation(),M.remove(e)}}})],1),t("q-item-side",{staticClass:"gt-xs",attrs:{right:""}},[t("q-btn",{attrs:{icon:"settings",round:"",flat:"",dense:""},on:{click:function(e){return e.stopPropagation(),M.settings(e)}}})],1),t("q-item-side",{staticClass:"lt-sm",attrs:{right:""}},[t("q-btn",{attrs:{icon:"more_vert",round:"",flat:"",dense:""},on:{click:function(e){return e.stopPropagation(),M.more(e)}}})],1)]],2)},j=[];i._withStripped=!0;t("f3/d"),t("xfY5");var u=t("aRp8"),g=t("JEAp"),I=t.n(g),A={name:"ResourceQItem",components:{ResourceBatteryChip:u["a"]},props:{resource:{},level:{type:Number,default:0},noParent:Boolean,readonly:Boolean},data:function(){return{}},computed:{date:function(){var M=this.resource.modifiedDate();if(this.resource instanceof this.$ething.Device){var e=this.resource.lastSeenDate();if(e&&e>M)return e}return M},createdBy:function(){return this.resource.createdBy()?this.$ething.arbo.get(this.resource.createdBy()):null},showParent:function(){return!this.noParent&&!!this.createdBy},showType:function(){return this.resource instanceof this.$ething.Device},showConnected:function(){return this.resource instanceof this.$ething.Device},showBattery:function(){return this.resource instanceof this.$ething.Device&&this.resource.hasBattery()},showLocation:function(){return this.resource instanceof this.$ething.Device&&this.resource.location()},showSize:function(){return this.resource instanceof this.$ething.File},showLength:function(){return this.resource instanceof this.$ething.Table},showChart:function(){return this.resource instanceof this.$ething.Table&&this.resource.length()},showDownload:function(){return this.resource instanceof this.$ething.File||this.resource instanceof this.$ething.Table}},methods:{gen:function(M){return["pad","pad-"+M]},batteryIcon:function(M){return M>95?"mdi-battery":M>85?"mdi-battery-90":M>75?"mdi-battery-80":M>65?"mdi-battery-70":M>55?"mdi-battery-60":M>45?"mdi-battery-50":M>35?"mdi-battery-40":M>25?"mdi-battery-30":M>15?"mdi-battery-20":M>=0?"mdi-battery-alert":"battery unknown"},batteryColor:function(M){return M<=15?"negative":M<=40?"warning":void 0},settings:function(){this.$router.push("/resource/"+this.resource.id())},more:function(){var M=this,e=[];this.showChart&&e.push({label:"Plot chart",color:"secondary",icon:"mdi-chart-line",handler:function(){return M.chart()}}),e.push({label:"Delete",color:"negative",icon:"delete",handler:function(){return M.remove()}}),e.push({label:"Settings",icon:"settings",handler:function(){M.settings()}}),this.$q.actionSheet({title:this.resource.basename(),actions:e}).catch(function(){})},remove:function(){var M=this,e=this.resource.name(),t=this.$ething.arbo.list().filter(function(e){return e.createdBy()===M.resource.id()}),i=[];return t.length&&i.push({label:"Remove also the children resources",value:"removeChildren",color:"secondary"}),this.$q.dialog({title:"Remove",message:"Do you really want to remove definitely the "+this.resource.type()+' "'+this.resource.name()+'" ?',options:{type:"checkbox",model:[],items:i},ok:"Remove",cancel:"Cancel"}).then(function(t){M.resource.remove(-1!==t.indexOf("removeChildren")).then(function(){M.$q.notify(e+" removed !")})})},chart:function(){this.$router.push("/chart/"+this.resource.id())},download:function(){var M=this;this.resource instanceof this.$ething.File?this.$ething.request({url:this.resource.getContentUrl(),dataType:"blob"}).then(function(e){I.a.saveAs(e,M.resource.basename())}):this.resource instanceof this.$ething.Table&&this.$q.dialog({title:'Download "'+this.resource.name()+'"',message:"Format: ",options:{type:"radio",model:"csv",items:[{label:"CSV",value:"csv"},{label:"JSON",value:"json_pretty"}]},cancel:!0,preventClose:!0,color:"secondary"}).then(function(e){M.$ething.request({url:M.resource.getContentUrl()+"?fmt="+e,dataType:"blob"}).then(function(t){I.a.saveAs(t,M.resource.basename()+"."+("json_pretty"==e?"json":e))})})},open:function(M){this.readonly||this.$ui.open(M)}}},N=A,r=(t("iYqZ"),t("KHd+")),D=Object(r["a"])(N,i,j,!1,null,"7ad34ebe",null);e["a"]=D.exports},aRp8:function(M,e,t){"use strict";var i=function(){var M=this,e=M.$createElement,t=M._self._c||e;return"number"===typeof M.battery?t("q-chip",{attrs:{small:"",detail:"",icon:M.batteryIcon(M.battery),color:M.batteryColor(M.battery)}},[M._v("\n  "+M._s(M.battery)+"%\n")]):M._e()},j=[];i._withStripped=!0;var u={name:"ResourceBatteryChip",props:{resource:{}},data:function(){return{}},computed:{battery:function(){return this.resource.battery()}},methods:{batteryIcon:function(M){return M>95?"mdi-battery":M>85?"mdi-battery-90":M>75?"mdi-battery-80":M>65?"mdi-battery-70":M>55?"mdi-battery-60":M>45?"mdi-battery-50":M>35?"mdi-battery-40":M>25?"mdi-battery-30":M>15?"mdi-battery-20":M>=0?"mdi-battery-alert":"battery unknown"},batteryColor:function(M){return M<=15?"negative":M<=40?"warning":void 0}}},g=u,I=t("KHd+"),A=Object(I["a"])(g,i,j,!1,null,null,null);e["a"]=A.exports},adv4:function(M,e,t){},iYqZ:function(M,e,t){"use strict";var i=t("adv4"),j=t.n(i);j.a},xOSM:function(M,e){M.exports="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNjYuNyAxNjguOSIgd2lkdGg9IjE2Ni43IiBoZWlnaHQ9IjE2OC45IiBpc29sYXRpb249Imlzb2xhdGUiPjxkZWZzPjxjbGlwUGF0aD48cmVjdCB3aWR0aD0iMTY2LjciIGhlaWdodD0iMTY4LjkiLz48L2NsaXBQYXRoPjwvZGVmcz48ZyBjbGlwLXBhdGg9InVybCgjX2NsaXBQYXRoX1BQUGlFY09SaFJTWXdvcEVFTm5hUkZ6emVZU1htd3R0KSI+PHBhdGggZD0iTTY1LjYgMTM1LjJDNjUuNiAxMzcuMSA2NC4xIDEzOC42IDYyLjIgMTM4LjYgNjAuNCAxMzguNiA1OC45IDEzNy4xIDU4LjkgMTM1LjIgNTguOSAxMzAuNyA2MS45IDEyNi43IDY2LjggMTI0IDcxLjEgMTIxLjYgNzcgMTIwLjEgODMuMyAxMjAuMSA4OS43IDEyMC4xIDk1LjYgMTIxLjYgOTkuOSAxMjQgMTA0LjcgMTI2LjcgMTA3LjggMTMwLjcgMTA3LjggMTM1LjIgMTA3LjggMTM3LjEgMTA2LjMgMTM4LjYgMTA0LjQgMTM4LjYgMTAyLjYgMTM4LjYgMTAxLjEgMTM3LjEgMTAxLjEgMTM1LjIgMTAxLjEgMTMzLjMgOTkuNCAxMzEuMyA5Ni42IDEyOS44IDkzLjMgMTI3LjkgODguNiAxMjYuOCA4My4zIDEyNi44IDc4LjEgMTI2LjggNzMuNCAxMjcuOSA3MCAxMjkuOCA2Ny4zIDEzMS4zIDY1LjYgMTMzLjMgNjUuNiAxMzUuMlpNMTQ5LjIgMTUzLjNDMTQ5LjIgMTU3LjYgMTQ3LjUgMTYxLjUgMTQ0LjYgMTY0LjQgMTQxLjggMTY3LjIgMTM3LjkgMTY4LjkgMTMzLjYgMTY4LjkgMTI5LjMgMTY4LjkgMTI1LjQgMTY3LjIgMTIyLjYgMTY0LjQgMTIwLjkgMTYyLjggMTE5LjcgMTYwLjkgMTE4LjkgMTU4LjcgMTE0LjEgMTYxIDEwOSAxNjIuOCAxMDMuNyAxNjQuMSA5Ny4yIDE2NS44IDkwLjQgMTY2LjYgODMuMyAxNjYuNiA2MC4zIDE2Ni42IDM5LjUgMTU3LjMgMjQuNCAxNDIuMiA5LjMgMTI3LjEgMCAxMDYuMyAwIDgzLjMgMCA2MC4zIDkuMyAzOS41IDI0LjQgMjQuNCAzOS41IDkuMyA2MC4zIDAgODMuMyAwIDEwNi40IDAgMTI3LjIgOS4zIDE0Mi4zIDI0LjQgMTU3LjMgMzkuNSAxNjYuNyA2MC4zIDE2Ni43IDgzLjMgMTY2LjcgOTQuNSAxNjQuNSAxMDUuMSAxNjAuNSAxMTQuOSAxNTYuNiAxMjQuMiAxNTEuMSAxMzIuNyAxNDQuNCAxNDAgMTQ3IDE0NS4xIDE0OS4yIDE1MC4yIDE0OS4yIDE1My4zWk0xMzAuNyAxMjYuM0MxMzEuMSAxMjUuNSAxMzEuOCAxMjUgMTMyLjUgMTI0LjhMMTMyLjYgMTI0LjcgMTMyLjYgMTI0LjcgMTMyLjcgMTI0LjcgMTMyLjcgMTI0LjcgMTMyLjggMTI0LjcgMTMyLjkgMTI0LjYgMTMyLjkgMTI0LjYgMTMyLjkgMTI0LjYgMTMzIDEyNC42IDEzMyAxMjQuNkMxMzMgMTI0LjYgMTMzLjEgMTI0LjYgMTMzLjEgMTI0LjZMMTMzLjEgMTI0LjYgMTMzLjIgMTI0LjYgMTMzLjIgMTI0LjZDMTMzLjkgMTI0LjUgMTM0LjYgMTI0LjYgMTM1LjIgMTI1IDEzNS44IDEyNS4zIDEzNi4zIDEyNS44IDEzNi42IDEyNi40TDEzNi42IDEyNi40IDEzNi42IDEyNi40IDEzNi42IDEyNi40IDEzNi42IDEyNi40IDEzNi42IDEyNi40IDEzNi42IDEyNi41IDEzNi42IDEyNi41IDEzNi42IDEyNi41IDEzNi42IDEyNi41IDEzNi42IDEyNi41IDEzNi43IDEyNi41QzEzNyAxMjcuMiAxMzcuNyAxMjguMyAxMzguNCAxMjkuNkwxMzguNCAxMjkuNiAxMzguNSAxMjkuNyAxMzguNSAxMjkuNyAxMzguNiAxMjkuOCAxMzguNiAxMjkuOSAxMzguNiAxMjkuOSAxMzguNyAxMzAgMTM4LjcgMTMwLjEgMTM4LjcgMTMwLjEgMTM4LjcgMTMwLjEgMTM4LjggMTMwLjIgMTM4LjggMTMwLjIgMTM4LjggMTMwLjMgMTM4LjkgMTMwLjMgMTM4LjkgMTMwLjQgMTM4LjkgMTMwLjQgMTM4LjkgMTMwLjQgMTM5IDEzMC41IDEzOSAxMzAuNSAxMzkgMTMwLjYgMTM5LjEgMTMwLjcgMTM5LjEgMTMwLjcgMTM5LjEgMTMwLjcgMTM5LjIgMTMwLjggMTM5LjIgMTMwLjggMTM5LjIgMTMwLjlDMTM5LjggMTMxLjggMTQwLjQgMTMyLjkgMTQxIDEzMy45IDE0Ni41IDEyNy42IDE1MS4xIDEyMC4zIDE1NC4zIDExMi40IDE1OCAxMDMuNCAxNjAgOTMuNiAxNjAgODMuMyAxNjAgNjIuMSAxNTEuNCA0MyAxMzcuNiAyOS4xIDEyMy43IDE1LjIgMTA0LjUgNi43IDgzLjMgNi43IDYyLjIgNi43IDQzIDE1LjIgMjkuMSAyOS4xIDE1LjIgNDMgNi43IDYyLjEgNi43IDgzLjMgNi43IDEwNC41IDE1LjIgMTIzLjYgMjkuMSAxMzcuNSA0MyAxNTEuNCA2Mi4yIDE2MCA4My4zIDE2MCA4OS44IDE2MCA5Ni4xIDE1OS4yIDEwMi4xIDE1Ny43IDEwNy44IDE1Ni4yIDExMy4xIDE1NC4yIDExOC4xIDE1MS43TDExOC4xIDE1MS42IDExOC4yIDE1MS42IDExOC4yIDE1MS4zIDExOC4yIDE1MS4zIDExOC4zIDE1MSAxMTguMyAxNTEgMTE4LjQgMTUwLjcgMTE4LjQgMTUwLjYgMTE4LjUgMTUwLjQgMTE4LjUgMTUwLjMgMTE4LjUgMTUwIDExOC42IDE0OS45IDExOC42IDE0OS43IDExOC43IDE0OS42IDExOC44IDE0OS4zQzExOC45IDE0OC45IDExOSAxNDguNSAxMTkuMSAxNDguMkwxMTkuMiAxNDguMSAxMTkuMyAxNDcuOCAxMTkuMyAxNDcuNyAxMTkuNCAxNDcuNCAxMTkuNCAxNDcuNEMxMTkuNSAxNDcuMSAxMTkuNiAxNDYuOSAxMTkuNyAxNDYuN0wxMTkuNyAxNDYuNiAxMTkuOCAxNDYuMyAxMTkuOSAxNDYuMiAxMjAgMTQ1LjkgMTIwLjEgMTQ1LjlDMTIwLjIgMTQ1LjYgMTIwLjMgMTQ1LjMgMTIwLjQgMTQ1LjFMMTIwLjQgMTQ1LjEgMTIwLjYgMTQ0LjcgMTIwLjYgMTQ0LjYgMTIwLjcgMTQ0LjMgMTIwLjggMTQ0LjIgMTIwLjkgMTQzLjkgMTIwLjkgMTQzLjggMTIxIDE0My44IDEyMS4xIDE0My41IDEyMS4xIDE0My40IDEyMS4yIDE0My4yIDEyMS4zIDE0MyAxMjEuNCAxNDNDMTIxLjYgMTQyLjYgMTIxLjcgMTQyLjIgMTIyIDE0MS44TDEyMiAxNDEuNyAxMjIuMiAxNDEuNCAxMjIuMiAxNDEuMyAxMjIuNCAxNDAuOSAxMjIuNCAxNDAuOSAxMjIuNiAxNDAuNSAxMjIuNiAxNDAuNSAxMjIuOCAxNDAuMSAxMjMgMTM5LjggMTIzIDEzOS43IDEyMyAxMzkuNyAxMjMuNCAxMzguOSAxMjMuNSAxMzguOSAxMjMuNiAxMzguNiAxMjMuNyAxMzguNCAxMjMuOCAxMzguMyAxMjMuOSAxMzggMTI0IDEzNy45IDEyNC4yIDEzNy42IDEyNC4yIDEzNy41IDEyNC40IDEzNy4yIDEyNC40IDEzNy4yIDEyNC42IDEzNi44IDEyNC42IDEzNi44IDEyNC44IDEzNi40IDEyNC44IDEzNi40IDEyNSAxMzYuMSAxMjUuMSAxMzYgMTI1LjIgMTM1LjcgMTI1LjMgMTM1LjYgMTI1LjQgMTM1LjMgMTI1LjUgMTM1LjIgMTI1LjYgMTM1IDEyNS43IDEzNC44IDEyNS44IDEzNC42IDEyNS45IDEzNC40IDEyNi4yIDEzNCAxMjYuMiAxMzMuOSAxMjYuNCAxMzMuNiAxMjYuNCAxMzMuNiAxMjYuNiAxMzMuMyAxMjYuNiAxMzMuMiAxMjYuOCAxMzIuOSAxMjYuOCAxMzIuOSAxMjcgMTMyLjUgMTI3IDEzMi41IDEyNy4zIDEzMi4yIDEyNy40IDEzMS45IDEyNy40IDEzMS44IDEyNy42IDEzMS42IDEyNy43IDEzMS41IDEyNy44IDEzMS4zIDEyNy45IDEzMS4xIDEyOCAxMzEgMTI4LjEgMTMwLjggMTI4LjEgMTMwLjYgMTI4LjMgMTMwLjQgMTI4LjMgMTMwLjQgMTI4LjUgMTMwLjEgMTI4LjUgMTMwLjEgMTI4LjcgMTI5LjggMTI4LjcgMTI5LjggMTI4LjggMTI5LjUgMTI4LjggMTI5LjUgMTI4LjkgMTI5LjQgMTI4LjkgMTI5LjMgMTI5IDEyOS4zIDEyOSAxMjkuMiAxMjkgMTI5LjEgMTI5IDEyOS4xIDEyOS4xIDEyOSAxMjkuMSAxMjkgMTI5LjIgMTI4LjkgMTI5LjIgMTI4LjkgMTI5LjIgMTI4LjggMTI5LjIgMTI4LjggMTI5LjMgMTI4LjggMTI5LjMgMTI4LjggMTI5LjMgMTI4LjcgMTI5LjMgMTI4LjcgMTI5LjMgMTI4LjcgMTI5LjMgMTI4LjcgMTI5LjQgMTI4LjYgMTI5LjQgMTI4LjYgMTI5LjQgMTI4LjUgMTI5LjQgMTI4LjUgMTI5LjQgMTI4LjQgMTI5LjUgMTI4LjQgMTI5LjUgMTI4LjQgMTI5LjUgMTI4LjQgMTI5LjUgMTI4LjQgMTI5LjUgMTI4LjMgMTI5LjUgMTI4LjMgMTI5LjYgMTI4LjIgMTI5LjYgMTI4LjIgMTI5LjYgMTI4LjIgMTI5LjYgMTI4LjIgMTI5LjYgMTI4LjEgMTI5LjYgMTI4LjEgMTI5LjcgMTI4LjEgMTI5LjcgMTI4LjEgMTI5LjcgMTI4IDEyOS43IDEyOCAxMjkuOCAxMjcuOSAxMjkuOCAxMjcuOSAxMjkuOCAxMjcuOSAxMjkuOCAxMjcuOSAxMjkuOCAxMjcuOCAxMjkuOCAxMjcuOCAxMjkuOCAxMjcuOCAxMjkuOCAxMjcuOCAxMjkuOSAxMjcuNyAxMjkuOSAxMjcuNyAxMjkuOSAxMjcuNyAxMjkuOSAxMjcuNyAxMjkuOSAxMjcuNiAxMjkuOSAxMjcuNiAxMzAgMTI3LjYgMTMwIDEyNy42IDEzMCAxMjcuNSAxMzAgMTI3LjUgMTMwIDEyNy40IDEzMCAxMjcuNCAxMzAuMSAxMjcuNCAxMzAuMSAxMjcuNCAxMzAuMSAxMjcuNCAxMzAuMSAxMjcuNCAxMzAuMSAxMjcuMyAxMzAuMSAxMjcuMyAxMzAuMSAxMjcuMyAxMzAuMSAxMjcuMyAxMzAuMiAxMjcuMiAxMzAuMiAxMjcuMiAxMzAuMiAxMjcuMiAxMzAuMiAxMjcuMiAxMzAuMiAxMjcuMSAxMzAuMiAxMjcuMSAxMzAuMiAxMjcuMSAxMzAuMiAxMjcuMSAxMzAuMyAxMjcgMTMwLjMgMTI3IDEzMC4zIDEyNyAxMzAuMyAxMjcgMTMwLjMgMTI3IDEzMC4zIDEyNyAxMzAuNCAxMjYuOSAxMzAuNCAxMjYuOSAxMzAuNCAxMjYuOSAxMzAuNCAxMjYuOSAxMzAuNCAxMjYuOCAxMzAuNCAxMjYuOCAxMzAuNCAxMjYuOCAxMzAuNCAxMjYuOCAxMzAuNCAxMjYuOCAxMzAuNCAxMjYuOCAxMzAuNSAxMjYuNyAxMzAuNSAxMjYuNyAxMzAuNSAxMjYuNyAxMzAuNSAxMjYuNyAxMzAuNSAxMjYuNyAxMzAuNSAxMjYuNyAxMzAuNSAxMjYuNiAxMzAuNSAxMjYuNiAxMzAuNSAxMjYuNiAxMzAuNSAxMjYuNiAxMzAuNiAxMjYuNSAxMzAuNiAxMjYuNSAxMzAuNiAxMjYuNSAxMzAuNiAxMjYuNSAxMzAuNiAxMjYuNSAxMzAuNiAxMjYuNSAxMzAuNiAxMjYuNCAxMzAuNiAxMjYuNCAxMzAuNyAxMjYuNCAxMzAuNyAxMjYuNCAxMzAuNyAxMjYuNCAxMzAuNyAxMjYuNCAxMzAuNyAxMjYuMyAxMzAuNyAxMjYuMyAxMzAuNyAxMjYuMyAxMzAuNyAxMjYuM1pNMTQwIDE1OS42QzE0MS41IDE1OC4xIDE0Mi42IDE1NS44IDE0Mi42IDE1My4zIDE0Mi42IDE1MSAxNDAuMSAxNDYgMTM3LjQgMTQxLjFMMTM3LjQgMTQxLjEgMTM3LjQgMTQxLjEgMTM3LjQgMTQxLjFDMTM3IDE0MC40IDEzNi43IDEzOS44IDEzNi4zIDEzOS4xTDEzNi4yIDEzOSAxMzYuMiAxMzguOSAxMzYuMSAxMzguOSAxMzYuMSAxMzguOCAxMzYgMTM4LjUgMTM1LjkgMTM4LjVDMTM1LjIgMTM3LjIgMTM0LjUgMTM2LjEgMTMzLjkgMTM1TDEzMy44IDEzNC45IDEzMy44IDEzNC44IDEzMy44IDEzNC44IDEzMy43IDEzNC43IDEzMy42IDEzNC42IDEzMy42IDEzNC41IDEzMy40IDEzNC44IDEzMy4zIDEzNS4xIDEzMy4zIDEzNS4xIDEzMy4xIDEzNS40IDEzMy4xIDEzNS40IDEzMi45IDEzNS43IDEzMi43IDEzNiAxMzIuNyAxMzYgMTMyLjUgMTM2LjMgMTMyLjUgMTM2LjMgMTMyLjQgMTM2LjYgMTMyLjIgMTM2LjkgMTMyLjIgMTM2LjkgMTMyIDEzNy4yIDEzMS44IDEzNy41IDEzMS44IDEzNy41IDEzMS42IDEzNy45IDEzMS42IDEzNy45IDEzMS40IDEzOC4yIDEzMS40IDEzOC4yIDEzMS4yIDEzOC41IDEzMSAxMzguOSAxMzEgMTM4LjkgMTMwLjggMTM5LjIgMTMwLjggMTM5LjIgMTMwLjcgMTM5LjUgMTMwLjcgMTM5LjUgMTMwLjUgMTM5LjkgMTMwLjUgMTM5LjkgMTMwLjMgMTQwLjIgMTMwLjEgMTQwLjUgMTMwLjEgMTQwLjUgMTI5LjkgMTQwLjkgMTI5LjkgMTQwLjkgMTI5LjcgMTQxLjIgMTI5LjcgMTQxLjIgMTI5LjYgMTQxLjUgMTI5LjQgMTQxLjkgMTI5LjIgMTQyLjIgMTI5LjIgMTQyLjIgMTI5IDE0Mi42IDEyOSAxNDIuNiAxMjguOCAxNDIuOSAxMjguNiAxNDMuMiAxMjguNiAxNDMuMiAxMjguNSAxNDMuNiAxMjguMyAxNDMuOSAxMjguMyAxNDMuOSAxMjguMSAxNDQuMyAxMjguMSAxNDQuMyAxMjcuOSAxNDQuNiAxMjcuOSAxNDQuNiAxMjcuOCAxNDQuOSAxMjcuNiAxNDUuMiAxMjcuNCAxNDUuNiAxMjcuMyAxNDUuOSAxMjcuMyAxNDUuOSAxMjcuMSAxNDYuMiAxMjcgMTQ2LjUgMTI3IDE0Ni41IDEyNi44IDE0Ni44IDEyNi44IDE0Ni44IDEyNi43IDE0Ny4yIDEyNi43IDE0Ny4yIDEyNi41IDE0Ny41IDEyNi41IDE0Ny41IDEyNi40IDE0Ny44IDEyNi40IDE0Ny44IDEyNi4zIDE0OC4xIDEyNi4xIDE0OC40IDEyNiAxNDguNiAxMjYgMTQ4LjYgMTI1LjkgMTQ5IDEyNS45IDE0OSAxMjUuNyAxNDkuMyAxMjUuNyAxNDkuNSAxMjUuNyAxNDkuNSAxMjUuNiAxNDkuOCAxMjUuNiAxNDkuOCAxMjUuNCAxNTAgMTI1LjQgMTUwIDEyNS4zIDE1MC4zIDEyNS4zIDE1MC4zIDEyNS4zIDE1MC42IDEyNS4zIDE1MC42IDEyNS4yIDE1MC44IDEyNS4yIDE1MC44IDEyNS4xIDE1MS4xIDEyNS4xIDE1MS4xIDEyNSAxNTEuMyAxMjUgMTUxLjMgMTI1IDE1MS42IDEyNSAxNTEuNiAxMjQuOSAxNTEuOCAxMjQuOSAxNTEuOCAxMjQuOCAxNTIgMTI0LjggMTUyIDEyNC44IDE1Mi4yIDEyNC44IDE1Mi4yIDEyNC44IDE1Mi40IDEyNC44IDE1Mi40QzEyNC43IDE1Mi41IDEyNC43IDE1Mi41IDEyNC43IDE1Mi42TDEyNC43IDE1Mi42IDEyNC43IDE1Mi44IDEyNC43IDE1Mi44QzEyNC43IDE1Mi45IDEyNC43IDE1Mi45IDEyNC43IDE1M0wxMjQuNyAxNTMgMTI0LjYgMTUzLjIgMTI0LjYgMTUzLjIgMTI0LjYgMTUzLjMgMTI0LjYgMTUzLjRDMTI0LjcgMTU1LjkgMTI1LjcgMTU4LjEgMTI3LjMgMTU5LjcgMTI4LjkgMTYxLjMgMTMxLjEgMTYyLjMgMTMzLjYgMTYyLjMgMTM2LjEgMTYyLjMgMTM4LjMgMTYxLjMgMTQwIDE1OS42Wk0xMzUuMyA3Mi43QzEzNi4yIDc0LjMgMTM1LjYgNzYuMyAxMzMuOSA3Ny4yIDEzMi4zIDc4IDEzMC4zIDc3LjQgMTI5LjQgNzUuOCAxMjguNyA3NC4zIDEyNy42IDcyLjkgMTI2LjMgNzEuOSAxMjUgNzAuOCAxMjMuNCA3MC4xIDEyMS44IDY5LjZMMTIxLjggNjkuNkMxMjAuOCA2OS40IDExOS44IDY5LjIgMTE4LjkgNjkuMiAxMTcuOCA2OS4yIDExNi44IDY5LjMgMTE1LjggNjkuNSAxMTQgNjkuOSAxMTIuMyA2OC44IDExMS44IDY3IDExMS41IDY1LjIgMTEyLjYgNjMuNSAxMTQuNCA2MyAxMTUuOCA2Mi43IDExNy40IDYyLjYgMTE4LjkgNjIuNiAxMjAuNSA2Mi42IDEyMiA2Mi44IDEyMy40IDYzLjJMMTIzLjYgNjMuMkMxMjYuMSA2My45IDEyOC40IDY1LjEgMTMwLjQgNjYuNyAxMzIuNSA2OC4zIDEzNC4xIDcwLjQgMTM1LjMgNzIuN1pNMzcuMiA3NS44QzM2LjQgNzcuNCAzNC40IDc4IDMyLjcgNzcuMiAzMS4xIDc2LjMgMzAuNSA3NC4zIDMxLjMgNzIuNyAzMi41IDcwLjQgMzQuMiA2OC4zIDM2LjIgNjYuNyAzOC4yIDY1LjEgNDAuNiA2My45IDQzLjEgNjMuMkw0My4yIDYzLjJDNDQuNyA2Mi44IDQ2LjIgNjIuNiA0Ny43IDYyLjYgNDkuMyA2Mi42IDUwLjggNjIuNyA1Mi4zIDYzIDU0LjEgNjMuNSA1NS4yIDY1LjIgNTQuOCA2NyA1NC40IDY4LjggNTIuNiA2OS45IDUwLjkgNjkuNSA0OS45IDY5LjMgNDguOCA2OS4yIDQ3LjggNjkuMiA0Ni44IDY5LjIgNDUuOCA2OS40IDQ0LjkgNjkuNkw0NC45IDY5LjZDNDMuMiA3MC4xIDQxLjcgNzAuOCA0MC40IDcxLjkgMzkuMSA3Mi45IDM4IDc0LjMgMzcuMiA3NS44Wk0xMjUuMiA5Mi43QzEyNS4yIDkwLjcgMTI0LjUgODguOSAxMjMuMyA4Ny42IDEyMi4yIDg2LjUgMTIwLjYgODUuNyAxMTkgODUuNyAxMTcuMyA4NS43IDExNS44IDg2LjUgMTE0LjcgODcuNiAxMTMuNSA4OC45IDExMi44IDkwLjcgMTEyLjggOTIuNyAxMTIuOCA5NC42IDExMy41IDk2LjQgMTE0LjcgOTcuNyAxMTUuOCA5OC45IDExNy4zIDk5LjYgMTE5IDk5LjYgMTIwLjYgOTkuNiAxMjIuMiA5OC45IDEyMy4zIDk3LjcgMTI0LjUgOTYuNCAxMjUuMiA5NC42IDEyNS4yIDkyLjdaTTEyOC4yIDgzLjJDMTMwLjQgODUuNiAxMzEuOCA4OSAxMzEuOCA5Mi43IDEzMS44IDk2LjQgMTMwLjQgOTkuNyAxMjguMiAxMDIuMiAxMjUuOCAxMDQuNyAxMjIuNiAxMDYuMyAxMTkgMTA2LjMgMTE1LjQgMTA2LjMgMTEyLjEgMTA0LjcgMTA5LjggMTAyLjIgMTA3LjUgOTkuNyAxMDYuMSA5Ni40IDEwNi4xIDkyLjcgMTA2LjEgODkgMTA3LjUgODUuNiAxMDkuOCA4My4yIDExMi4xIDgwLjYgMTE1LjQgNzkuMSAxMTkgNzkuMSAxMjIuNiA3OS4xIDEyNS44IDgwLjYgMTI4LjIgODMuMlpNNTMuOSA5Mi43QzUzLjkgOTAuNyA1My4yIDg4LjkgNTIgODcuNiA1MC45IDg2LjUgNDkuNCA4NS43IDQ3LjcgODUuNyA0NiA4NS43IDQ0LjUgODYuNSA0My40IDg3LjYgNDIuMiA4OC45IDQxLjUgOTAuNyA0MS41IDkyLjcgNDEuNSA5NC42IDQyLjIgOTYuNCA0My40IDk3LjcgNDQuNSA5OC45IDQ2IDk5LjYgNDcuNyA5OS42IDQ5LjQgOTkuNiA1MC45IDk4LjkgNTIgOTcuNyA1My4yIDk2LjQgNTMuOSA5NC42IDUzLjkgOTIuN1pNNTYuOSA4My4yQzU5LjIgODUuNiA2MC41IDg5IDYwLjUgOTIuNyA2MC41IDk2LjQgNTkuMiA5OS43IDU2LjkgMTAyLjIgNTQuNSAxMDQuNyA1MS4zIDEwNi4zIDQ3LjcgMTA2LjMgNDQuMSAxMDYuMyA0MC45IDEwNC43IDM4LjUgMTAyLjIgMzYuMiA5OS43IDM0LjggOTYuNCAzNC44IDkyLjcgMzQuOCA4OSAzNi4yIDg1LjYgMzguNSA4My4yIDQwLjkgODAuNiA0NC4xIDc5LjEgNDcuNyA3OS4xIDUxLjMgNzkuMSA1NC41IDgwLjYgNTYuOSA4My4yWiIgZmlsbD0icmdiKDEsMjIsMzkpIiBmaWxsLW9wYWNpdHk9IjAuMiIvPjwvZz48L3N2Zz4K"}}]);