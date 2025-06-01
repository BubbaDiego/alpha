import{a as O}from"./chunk-FS5WEDFF.js";import{a as P}from"./chunk-NJHVGQ3T.js";import{g as fe}from"./chunk-2WTSXO3L.js";import{a as A}from"./chunk-C5UDUURS.js";import{c as le}from"./chunk-LO5C3EJB.js";import{h as pe}from"./chunk-5LRZ7IFN.js";import{db as w,ma as ue,r as ce}from"./chunk-ATEHMOFB.js";import{a as se,e as i}from"./chunk-2P7VAWV5.js";import{Oc as K,Pc as j}from"./chunk-4CMCOVQN.js";import{Mb as oe}from"./chunk-XKUMOCJO.js";import{N as ae,b as N}from"./chunk-G7PMLIMH.js";import{m as M}from"./chunk-FI5JCZQR.js";import{U as ie,V as ne,f as G,m as re}from"./chunk-HTY4DAML.js";import{a as L}from"./chunk-6MAAUKN7.js";import{c as k,f as C,g as $,h as n,i as f,n as o}from"./chunk-3KENBVE7.js";var de=k(U=>{"use strict";n();o();Object.defineProperty(U,"__esModule",{value:!0});var Ue=L(),Ve=function(e){Ue.useEffect(e,[])};U.default=Ve});var he=k(V=>{"use strict";n();o();Object.defineProperty(V,"__esModule",{value:!0});var Re=(j(),$(K)),Xe=L(),Je=Re.__importDefault(de()),Ye=function(e){var r=Xe.useRef(e);r.current=e,Je.default(function(){return function(){return r.current()}})};V.default=Ye});var ge=k(X=>{"use strict";n();o();Object.defineProperty(X,"__esModule",{value:!0});var Ze=(j(),$(K)),R=L(),et=Ze.__importDefault(he()),tt=function(e){var r=R.useRef(0),a=R.useState(e),p=a[0],s=a[1],x=R.useCallback(function(l){cancelAnimationFrame(r.current),r.current=requestAnimationFrame(function(){s(l)})},[]);return et.default(function(){cancelAnimationFrame(r.current)}),[p,x]};X.default=tt});var ye=k(y=>{"use strict";n();o();Object.defineProperty(y,"__esModule",{value:!0});y.isNavigator=y.isBrowser=y.off=y.on=y.noop=void 0;var rt=function(){};y.noop=rt;function it(e){for(var r=[],a=1;a<arguments.length;a++)r[a-1]=arguments[a];e&&e.addEventListener&&e.addEventListener.apply(e,r)}y.on=it;function nt(e){for(var r=[],a=1;a<arguments.length;a++)r[a-1]=arguments[a];e&&e.removeEventListener&&e.removeEventListener.apply(e,r)}y.off=nt;y.isBrowser=typeof self<"u";y.isNavigator=typeof navigator<"u"});var ve=k(J=>{"use strict";n();o();Object.defineProperty(J,"__esModule",{value:!0});var ot=(j(),$(K)),at=L(),st=ot.__importDefault(ge()),xe=ye(),lt=function(e){f.NODE_ENV==="development"&&(typeof e!="object"||typeof e.current>"u")&&console.error("`useScroll` expects a single ref argument.");var r=st.default({x:0,y:0}),a=r[0],p=r[1];return at.useEffect(function(){var s=function(){e.current&&p({x:e.current.scrollLeft,y:e.current.scrollTop})};return e.current&&xe.on(e.current,"scroll",s,{capture:!1,passive:!0}),function(){e.current&&xe.off(e.current,"scroll",s)}},[e]),a};J.default=lt});n();o();var S=C(L());var qe=i(A).attrs({align:"center"})`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
`,We=i.div`
  width: 48px;
  height: 48px;
  position: relative;
  margin-bottom: 15px;
  border-radius: 100%;
  background: rgba(255, 220, 98, 0.2);
`,$e=i(P).attrs({align:"center",justify:"center"})`
  height: 100%;
`,Ge=i(w).attrs({size:17,weight:500,lineHeight:22,margin:"0 0 10px 0"})``,Ke=i(w).attrs({size:15,weight:500,lineHeight:21,margin:"0 0 15px 0",color:"#777777"})``,je=i(w).attrs({size:16,weight:500,lineHeight:22,margin:"0",color:"#AB9FF2"})``,Bt=S.default.memo(e=>{let{t:r}=M();return S.default.createElement(qe,null,S.default.createElement(We,null,S.default.createElement($e,null,S.default.createElement(ue,{width:22,exclamationFill:"transparent",circleFill:"#FFE920"}))),S.default.createElement(Ge,null,e.title),S.default.createElement(Ke,null,e.description),e.refetch?S.default.createElement(je,{onClick:e.refetch},e.buttonText?e.buttonText:r("commandRetry")):null)});n();o();var v=C(L());var Qe=i.div`
  width: 44px;
  height: 44px;
  margin-right: 10px;
`,H=i(O).attrs({height:"8px",backgroundColor:"#484848",borderRadius:"8px"})``,me=({hideTextRight:e})=>v.default.createElement(O,{align:"center",width:"100%",height:"74px",backgroundColor:"#2D2D2D",borderRadius:N.radiusRow,margin:"0 0 10px 0",padding:"15px"},v.default.createElement(Qe,null,v.default.createElement(O,{width:"44px",height:"44px",backgroundColor:"#434343",borderRadius:"50%"})),v.default.createElement(A,null,v.default.createElement(P,{margin:"0 0 10px",justify:"space-between"},v.default.createElement(H,{width:"120px"}),!e&&v.default.createElement(H,{width:"60px"})),v.default.createElement(P,{justify:"space-between"},v.default.createElement(H,{width:"75px"}),!e&&v.default.createElement(H,{width:"35px"}))));n();o();var t=C(L());n();o();var Q=i(w)`
  margin: 25px 0;
  height: 75%;
  font-weight: 500;
  font-size: 18px;
  line-height: 22px;
  color: #666;
  display: flex;
  text-align: center;
  align-items: center;
  justify-content: center;
`;n();o();var B="ALL";n();o();var u=C(L()),Le=C(ve());var ct=i.div`
  position: relative;
`,ut=i.div`
  display: flex;
  flex-direction: row;
  overflow: auto;
`,pt=i.div`
  background: ${({active:e})=>e?"#AB9FF2":"#333333"};
  height: 32px;
  border-radius: 32px;
  padding: 0 12px 1px;
  margin-right: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  &:hover {
    background: ${({active:e})=>e?"#e2dffe":"#444444"};
  }
`,ft=i(w).attrs({weight:600,size:15,noWrap:!0})``,mt=i.div`
  position: absolute;
  top: 0;
  bottom: 0;
  width: 30px;
  display: flex;
  align-items: center;
  z-index: 2;
`,Se=i(mt)`
  background: linear-gradient(90deg, transparent 0%, #222222 30%);
  justify-content: flex-end;
  right: 0;
  padding-right: 5px;
`,dt=i(Se)`
  transform: rotate(180deg);
  right: auto;
  left: 0;
  padding-left: 5px;
`,be=i(ce).attrs({fill:"#FFFFFF"})``,Te=u.default.memo(({onPress:e,filters:r})=>{let[a,p]=u.default.useState(!1),[s,x]=u.default.useState(!1),l=(0,u.useRef)(null),{x:h}=(0,Le.default)(l);(0,u.useEffect)(()=>{l.current&&(p(h>0),x(Math.ceil(h)+l.current.offsetWidth<l.current.scrollWidth))},[h]);let m=(0,u.useCallback)(d=>{if(!l.current)return;let _=d*self.innerWidth*.75;l.current.scrollBy({left:_,behavior:"smooth"})},[]),g=(0,u.useCallback)(()=>m(-1),[m]),F=(0,u.useCallback)(()=>m(1),[m]);return u.default.createElement(ct,null,a?u.default.createElement(dt,{onClick:g},u.default.createElement(be,null)):null,u.default.createElement(ut,{ref:l},r.map(d=>u.default.createElement(pt,{key:d.id,onClick:()=>e(d.id),active:d.active},u.default.createElement(ft,{color:d.active?"#000000":"#FFFFFF"},d.label)))),s?u.default.createElement(Se,{onClick:F},u.default.createElement(be,null)):null)});n();o();n();o();var Fe=ht;function ht(e,r,a){if(!e)return a;var p,s;if(Array.isArray(r)&&(p=r.slice(0)),typeof r=="string"&&(p=r.split(".")),typeof r=="symbol"&&(p=[r]),!Array.isArray(p))throw new Error("props arg must be an array, a string or a symbol");for(;p.length;)if(s=p.shift(),!e||(e=e[s],e===void 0))return a;return e}var Ie=e=>{let{data:r,activeFilterId:a,filterKey:p,filterLabels:s,alwaysShowFilters:x}=e;if(s.length===0)return[];if(x)return s.map(m=>({label:m.label,id:m.id,active:a===m.id}));let l=[],h=s.find(m=>m.id===B);h&&l.push({label:h.label,id:h.id,active:a===h.id});for(let m of r){let g=Fe(m,p);if(l.some(d=>d.id===g))continue;let F=s.findIndex(d=>d.id===g);if(F!==-1&&(l[F]={label:s[F].label,id:g,active:a===g},l.filter(G).length===s.length))break}return l.filter(G)};var gt=74,yt=10,xt=gt+yt,we=i.div`
  display: flex;
  flex-direction: column;
  flex: 1;
`,Ce=i.div`
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
`,Ee=i.div`
  margin-bottom: 16px;
`,vt=i.div``,bt=i.div`
  flex: 1 1 auto; // https://github.com/bvaughn/react-virtualized-auto-sizer#can-i-use-this-component-with-flexbox
`,Lt=()=>t.default.createElement(t.default.Fragment,null,t.default.createElement(vt,null,[...Array(4)].map((e,r)=>t.default.createElement(me,{key:`row-loader-${r}`,hideTextRight:!0})))),St=t.default.memo(e=>t.default.createElement(Ce,null,t.default.createElement(Q,null,e.localizedError.message))),Tt=t.default.memo(e=>t.default.createElement(Ce,null,t.default.createElement(Q,null,e.text))),Ft=e=>{let{localizedError:r,isFetching:a,fuseOptions:p,filterKey:s,initialFilterKey:x,filterLabels:l=[],alwaysShowFilters:h=!1,emptyListCopy:m="",data:g,renderItem:F,keyExtractor:d,enableLiveSearch:_,setLiveSearchQuery:q}=e,[Y,Z]=(0,t.useState)(""),ke=ie(Y)??"",[I,D]=(0,t.useState)(""),ee=(0,t.useRef)(null),te=(0,t.useRef)(null),Pe=(0,t.useMemo)(()=>!s||l.length===0||I===B?g:g.filter(c=>re(c,s)===I),[I,g,s,l.length]),z=ne(Pe,ke,p,_),{t:Be}=M(),De=Be("assetListSearch");(0,t.useEffect)(()=>{setTimeout(()=>te.current?.focus(),200)},[]),(0,t.useEffect)(()=>{let c=ee.current;return c&&c.scrollTop!==0&&(c.scrollTop=0),()=>{c?.current&&(c.current=null)}},[Y,I]);let ze=(0,t.useCallback)(c=>{_&&q?q(c.currentTarget.value):Z(c.currentTarget.value)},[Z,_,q]),b=(0,t.useMemo)(()=>!s||l.length===0?[]:Ie({data:g,activeFilterId:I,filterKey:s,filterLabels:l,alwaysShowFilters:h}),[I,l,s,h,g]);(0,t.useEffect)(()=>{if(I||b.length===0)return;let c=x&&b.find(E=>E.id===x);if(c){D(c.id);return}D(b[0].id)},[b,x,D,I]);let Me=(0,t.useMemo)(()=>b.length>2||b.length===2&&!b.find(c=>c.id===B),[b]),Ne=(0,t.useCallback)(({index:c,style:E,data:Oe})=>{let W=Oe[c];if(!W)return null;let He=d(W,c);return t.default.createElement("div",{key:He,style:E},F({item:W,index:c}))},[d,F]),Ae=(0,t.useMemo)(()=>z.length===0?()=>t.default.createElement(Tt,{text:m}):void 0,[m,z.length]);return r?t.default.createElement(we,null,t.default.createElement(St,{localizedError:r})):t.default.createElement(we,null,t.default.createElement(Ee,null,t.default.createElement(fe,{ref:te,tabIndex:0,placeholder:De,onChange:ze,maxLength:oe})),Me?t.default.createElement(Ee,null,t.default.createElement(Te,{onPress:D,filters:b})):null,a?t.default.createElement(Lt,null):t.default.createElement(bt,null,t.default.createElement(ae,null,({height:c,width:E})=>t.default.createElement(le,{outerRef:ee,innerElementType:Ae,height:c,itemSize:xt,itemData:z,itemCount:z.length,width:E},Ne))))},qr=t.default.memo(Ft);n();o();var Qr=i.div`
  background: ${e=>e.isHighlighted?"#333":"#2a2a2a"};
  ${e=>e.opacity!==void 0?`opacity: ${e.opacity};`:""}
  border-radius: ${N.radiusRow};
  padding-top: 15px;
  padding-bottom: 15px;
  padding-left: 10px;
  padding-right: 15px;
  display: flex;
  margin-bottom: 10px;
  align-items: center;
  width: 100%;
  cursor: ${e=>e.isDisabled?"auto":"pointer"};
  ${e=>!e.isDisabled&&se`
      &:hover {
        opacity: 1;
        background: #333333;
      }
    `}
`;n();o();var T=C(L());var It=i.div`
  display: flex;
  align-items: center;
  justify-content: center;
`,_e=({className:e,children:r,isLoading:a,spinnerColor:p,showingDelayMs:s=500})=>{let[x,l]=(0,T.useState)(!0);return(0,T.useEffect)(()=>{let h=setTimeout(()=>l(!1),s);return()=>{clearTimeout(h)}},[s]),a?x?null:T.default.createElement(It,{className:e},T.default.createElement(pe,{color:p})):T.default.createElement(T.default.Fragment,null,r)};_e.defaultProps={isLoading:!1};var Yr=i(_e)`
  height: 100%;
`;export{he as a,Q as b,Bt as c,B as d,me as e,Te as f,Ie as g,bt as h,qr as i,Qr as j,Yr as k};
//# sourceMappingURL=chunk-SWJ57CIZ.js.map
