import{a as P}from"./chunk-LJVOEF4C.js";import{a as C,e as S}from"./chunk-V4KRVOHD.js";import{M as L,r as I}from"./chunk-ATEHMOFB.js";import{e as i}from"./chunk-2P7VAWV5.js";import{b as T}from"./chunk-ITDMYF4L.js";import{Jc as k}from"./chunk-4CMCOVQN.js";import{$ as B}from"./chunk-6V7ED5GE.js";import{h as b}from"./chunk-T3HNWLEC.js";import{$ as z,b as y,l as h,m as x}from"./chunk-G7PMLIMH.js";import{K as w}from"./chunk-HTY4DAML.js";import{a as V}from"./chunk-6MAAUKN7.js";import{f as v,h as p,n as g}from"./chunk-3KENBVE7.js";p();g();var t=v(V());p();g();var R={header:"_14rx5di1 _51gazn5a _51gazn3o _51gazn6w _51gazn22 _51gazn1kj _51gazn1nq _51gazn1mv _51gaznkv _51gazn2cp _51gazns2 _51gaznxd",summaryContainer:"_51gazn1c8 _51gazn1xp"};p();g();var u=v(V()),N=u.default.memo(({address:e,networkID:o,showConcise:a})=>{let{getExistingAccount:l,getKnownAddressLabel:n}=B(),{data:f}=k(e,o),d=f?.address;if(!e)return null;let r=l(e),m=n(e,o),c=r?r.name:m;return d?u.default.createElement(x,null,e," ",u.default.createElement(x,{color:"textSecondary"},"(",b(d,4),")")):c?u.default.createElement(x,null,c," ",u.default.createElement(x,{color:"textSecondary"},"(",b(e,4),")")):u.default.createElement(x,null,a?b(e,4):e)});function _(e){if(!e){let a=parseInt(y.radiusRow.replace("px",""),10);return{borderTopLeftRadius:a,borderTopRightRadius:a,borderBottomRightRadius:a,borderBottomLeftRadius:a}}let o=e.split(" ").map(a=>a.replace("px","")).map(a=>parseInt(a,10));return o.length===1?{borderTopLeftRadius:o[0],borderTopRightRadius:o[0],borderBottomRightRadius:o[0],borderBottomLeftRadius:o[0]}:o.length===2?{borderTopLeftRadius:o[0],borderTopRightRadius:o[1],borderBottomRightRadius:o[0],borderBottomLeftRadius:o[1]}:{borderTopLeftRadius:o[0],borderTopRightRadius:o[1],borderBottomRightRadius:o[2],borderBottomLeftRadius:o[3]}}var F=i.div`
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid #222222;
  border-bottom-width: ${e=>e.border?1:0}px;
  padding: ${e=>e.padding?e.padding:14}px;
  cursor: ${e=>e.onClick?"pointer":"default"};
`,A=i.div`
  padding-top: 3px;
`,O=i.div`
  display: flex;
  justify-content: space-between;
  font-size: ${e=>e.fontSize?e.fontSize:14}px;
`,j=i.div`
  display: flex;
  justify-content: space-between;
`,E=i.div`
  text-align: left;
  flex: 1;
`,M=i.div`
  text-align: right;
  flex: 1;
`,H=i.div`
  display: flex;
  align-items: center;
  ${e=>e.truncate?"flex: 1; min-width: 0; justify-content:end;":""}
`,W=i.div`
  padding-left: 8px;
  color: #999;
`,$=({children:e,showArrow:o})=>t.createElement(H,{truncate:!o},e,o&&t.createElement(W,null,t.createElement(I,{height:12}))),s=i.span`
  color: ${e=>e.color||"white"};
  text-align: ${e=>e.align||"left"};
  font-weight: ${e=>e.weight||400};
  overflow-wrap: break-word;
  ${e=>e.margin?"margin: "+e.margin+";":""};
  ${e=>e.size?"font-size: "+e.size+"px;":""}
  ${e=>e.truncate?"white-space: nowrap; text-overflow: ellipsis; overflow:hidden; width: 100%;"+(e.size?"line-height: "+e.size*1.2+"px;":"line-height: 17px;"):""}
`,U=i.a.attrs({target:"_blank",rel:"noopener noreferrer"})`
  color: #ab9ff2;
  text-decoration: none;
  cursor: pointer;
`,q=i.div`
  text-align: center;
  width: 100%;
`,K=({children:e,label:o,tooltipContent:a,fontSize:l})=>t.createElement(t.Fragment,null,t.createElement(S,{tooltipAlignment:"topLeft",iconSize:12,lineHeight:17,fontSize:l,fontWeight:500,info:a?t.createElement(C,null,a):null},o),e),G=e=>{T.capture("activityItemDetailLinkClicked",{data:{hostname:w(e)}})},J=e=>"designSystemOptIn"in e&&e.designSystemOptIn===!0?t.createElement(Q,{...e}):t.createElement(X,{...e}),Q=({header:e,rows:o,borderRadius:a})=>{let l=_(a);return t.createElement(h,{className:R.summaryContainer,...l},e?t.createElement("div",{className:R.header},e):null,t.createElement(z,{rows:o.map(n=>({...n.onPress?{onClick:n.onPress}:{},topLeft:n.tooltipContent?{component:()=>t.createElement(S,{textColor:y.colors.legacy.textSecondary,iconColor:y.colors.legacy.textSecondary,tooltipAlignment:"topLeft",iconSize:12,lineHeight:17,fontSize:14,fontWeight:500,info:t.createElement(C,null,n.tooltipContent)},n.label)}:{text:n.label,font:"captionMedium",color:"textSecondary"},topRight:{text:n.value,font:"captionMedium",color:"textPrimary"}}))}))},X=({header:e,rows:o,borderRadius:a,padding:l,fontSize:n,networkID:f})=>{let d=_(a);return t.createElement(h,{className:R.summaryContainer,...d}," ",e?t.createElement("div",{className:R.header},e):null,o.map((r,m)=>{if(r.value===void 0)return null;let c=r.onClick?{role:"button"}:void 0;return t.createElement(F,{border:o.length-1!==m,padding:l,onClick:r.onClick,key:`summary-row-${m}`,...c},t.createElement(O,{key:r.label,fontSize:n},typeof r.value=="string"?r.type==="link"?t.createElement(q,null,t.createElement(U,{href:r.value,onClick:()=>G(r.value)},r.label)):t.createElement(K,{label:r.label,tooltipContent:r.tooltipContent,fontSize:n},t.createElement($,{showArrow:!!r.onClick},r.type==="address"?t.createElement(N,{address:r.value,networkID:f??"solana:101"}):t.createElement(s,{color:r.color,weight:500,align:"right",truncate:!r.onClick},r.value))):t.createElement(t.Fragment,null,t.createElement(s,{color:"#777777",size:n},r.label),t.createElement($,{showArrow:!!r.onClick},r.value))),t.createElement(j,null,r.leftSubtext?t.createElement(E,null,t.createElement(A,null,t.createElement(s,{color:r.leftSubtextColor||"#777777",size:13},r.leftSubtext))):null,r.rightSubtext?t.createElement(M,null,t.createElement(A,null,t.createElement(s,{color:r.rightSubtextColor||"#777777",size:13},r.rightSubtext))):null))}))},st=({name:e,imageURL:o})=>t.createElement("div",{style:{display:"flex",flexDirection:"row",alignItems:"center"}},t.createElement(P,{iconUrl:o,width:16}),t.createElement(s,{margin:"0 0 0 5px",weight:500},e)),Y=i.div`
  height: 100%;
  overflow: scroll;
  margin-top: -16px;
  padding-top: 16px;
  padding-bottom: 64px;
`,Z=i.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
`,ee=i.div`
  margin-top: 10px;
  margin-bottom: 10px;
`,te=i.div`
  margin-top: 10px;
  margin-bottom: 20px;
`,oe=i.div`
  margin-bottom: 10px;
`,re=i.div`
  position: relative;
  width: 100%;
  text-align: center;
  margin: 10px 0 10px 0;
`,ie=i(s)`
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
  max-width: 100%;
`,ae=i.div`
  background-color: #ffdc62;
  width: 100%;
  margin-top: 24px;
  margin-bottom: 14px;
  border-radius: 9px;
  padding: 16px;
  gap: 8px;
  display: flex;
  align-items: flex-start;
  align-self: stretch;
`,ne=i.div`
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
`,lt=({title:e,primaryText:o,secondaryText:a,image:l,sections:n,leftButton:f,warning:d})=>t.createElement(Y,null,t.createElement(Z,null,t.createElement(re,null,f||!1,t.createElement(s,{weight:500,size:22},e)),t.createElement(ee,null,l),o.value&&t.createElement(ie,{weight:600,size:34,color:o.color,align:"center",margin:"10px 0 10px 0"},o.value),a.value&&t.createElement(s,{size:16,color:"#777777",margin:"0 0 10px 0"},a.value),d&&t.createElement(ae,null,t.createElement(ne,null,t.createElement(L,null)),t.createElement(s,{size:14,color:"#222222",margin:"3px 0px 3px 8px"},d))),n.map(({title:r,rows:m},c)=>t.createElement(te,{key:`summary-item-${c}`},r&&t.createElement(oe,null,t.createElement(s,{size:14,weight:500,color:"#777777"},r)),t.createElement(J,{rows:m}))));export{K as a,J as b,st as c,lt as d};
//# sourceMappingURL=chunk-BTQAICSK.js.map
