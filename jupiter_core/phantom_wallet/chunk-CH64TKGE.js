import{m as L,r as A}from"./chunk-3L46OIZC.js";import{b as w}from"./chunk-OA3E7PE3.js";import{ia as D}from"./chunk-6RSSZ6VM.js";import{b as S,d as I}from"./chunk-5LEHT7IY.js";import{c as P}from"./chunk-E6VR42GU.js";import{b as p}from"./chunk-W27Z2YZM.js";import{ba as v,c as x,ca as y}from"./chunk-ATEHMOFB.js";import{e as o}from"./chunk-2P7VAWV5.js";import{a as k}from"./chunk-6MAAUKN7.js";import{f as C,h as a,n as s}from"./chunk-3KENBVE7.js";a();s();var t=C(k());var M=o.div`
  height: 0;
  transition: height 0.2s ease-in-out;
  width: 100%;
  ${e=>e.animate?`height: ${e.shouldCollapse?e.itemHeight+26:e.itemHeight+46}px`:""}
`,$=o.div`
  transition: transform 0.5s ease;
  width: 100%;
`,B=o(P)``,H=o.div`
  visibility: ${e=>e.isVisible?"visible":"hidden"};
`,E=o.div`
  align-items: center;
  display: flex;
  justify-content: space-between;
`,T=o.ul`
  align-items: center;
  display: flex;
  margin-bottom: 8px;
  transition: transform 0.5s ease;
  transform: ${e=>`translateX(${e.currentIndex*-100}%)`};
`,j=o.li`
  align-items: center;
  display: flex;
  flex: 0 0 100%;
  padding: ${e=>e.isActive?"0":e.isNext||e.isPrevious?"0 6px":"0"};
  height: ${e=>e.isActive?e.itemHeight:.9*e.itemHeight}px; /* 0.9 is taken from parallaxAdjacentItemScale from the carousel on mobile */
`,X=({items:e,onIndexChange:r,itemHeight:m})=>{let[n,u]=(0,t.useState)(0),h=(0,t.useCallback)(()=>{u(i=>i+1)},[]),d=(0,t.useCallback)(()=>{u(i=>i-1)},[]),g=n<e.length-1,f=n>0;(0,t.useEffect)(()=>{!e.length||n>e.length-1||r(n)},[e,r,n]),(0,t.useEffect)(()=>{e.length>0&&n>=e.length&&u(e.length-1)},[n,e]);let c=e.length<=1;return t.default.createElement(M,{animate:e.length>0,shouldCollapse:c,itemHeight:m},t.default.createElement($,null,t.default.createElement(T,{currentIndex:n},e.map((i,b)=>t.default.createElement(j,{key:i.key,isActive:n===b,isNext:n+1===b,isPrevious:n-1===b,itemHeight:m},i.node))),!c&&t.default.createElement(E,null,t.default.createElement(H,{isVisible:f},t.default.createElement(B,{onClick:d},t.default.createElement(v,null))),t.default.createElement(w,{numOfItems:e.length,currentIndex:n,maxVisible:5}),t.default.createElement(H,{isVisible:g},t.default.createElement(B,{onClick:h},t.default.createElement(y,null))))))};a();s();var l=C(k());a();s();var V=e=>{if(e==="Settings: Security & Privacy")return A;if(e==="Settings: Currency")return L};var U=l.default.lazy(()=>import("./FungibleDetailPage-JTWMWE3F.js")),ce=()=>{let{showSettingsMenu:e}=I(),{handleShowModalVisibility:r}=D(),{pushDetailView:m}=S(),n=x();return(0,l.useCallback)((h,d)=>{let{destinationType:g,url:f,caip19:c}=d;switch(g){case"External Link":p({url:f});break;case"Buy":r("onramp");break;case"Collectibles":n("/collectibles");break;case"Explore":n("/explore");break;case"Swapper":n("/swap");break;case"Settings: Claim Username":r("claimUsername");break;case"Settings: Import Seed Phrase":p({url:"onboarding.html?append=true"});break;case"Connect Hardware Wallet":p({url:"connect_hardware.html"});break;case"Convert to Jito":r("convertJitoInfo",{skipDismissRouting:!0});break;case"Token":{if(!c)return;m(l.default.createElement(U,{caip19:c,title:void 0,entryPoint:"actionBanner"}));break}default:{let i=V(g);if(!i)return;e(h,l.default.createElement(i,null))}}},[n,e,r,m])};export{ce as a,X as b};
//# sourceMappingURL=chunk-CH64TKGE.js.map
