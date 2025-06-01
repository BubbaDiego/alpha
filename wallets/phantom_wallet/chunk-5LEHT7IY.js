import{e as y}from"./chunk-NGO5FOJW.js";import{z as N}from"./chunk-2LU4YM7A.js";import{c as B}from"./chunk-E6VR42GU.js";import{a as M,b as A}from"./chunk-5LRZ7IFN.js";import{$ as L,P as C,ba as S,db as b}from"./chunk-ATEHMOFB.js";import{e as c}from"./chunk-2P7VAWV5.js";import{d as D}from"./chunk-O3DDAITN.js";import{a as F}from"./chunk-WFPABEAU.js";import{he as H,xd as V}from"./chunk-XKUMOCJO.js";import{e as k,la as p}from"./chunk-HTY4DAML.js";import{a as x}from"./chunk-6MAAUKN7.js";import{f as h,h as f,n as g}from"./chunk-3KENBVE7.js";f();g();var O=h(F()),i=h(x());var T=(0,i.createContext)({pushDetailViewCallback:()=>p,pushDetailView:p,popDetailView:p,resetDetailView:p,detailViewStackLength:0}),z=c(M.div)`
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  max-height: ${e=>e.theme?.detailViewMaxHeight??"100%"};
  min-height: ${e=>e.theme?.detailViewMinHeight??"initial"};
`,ae=i.default.memo(({children:e,shouldResetOnAccountChange:t,shouldPushDetailView:o})=>{let{detailViewStack:r,setDetailViewStack:l,pushDetailView:a,...s}=_(),{data:d}=H();return(0,i.useEffect)(()=>{t&&l([])},[d,l,t]),(0,i.useEffect)(()=>{o&&a(e)},[e,o,a]),i.default.createElement(T.Provider,{value:{...s,pushDetailView:a,detailViewStackLength:r.length}},i.default.createElement(J,{stack:r},e))}),U=navigator.webdriver?0:500,_=()=>{let[e,t]=(0,i.useState)([]),o=(0,i.useMemo)(()=>(0,O.default)(s=>{t(d=>V(d,u=>{u.push(s)}))},U,{leading:!0,trailing:!1}),[t]),r=(0,i.useCallback)(()=>{t(s=>V(s,d=>{d.pop()}))},[t]),l=(0,i.useCallback)(s=>()=>{o(s)},[o]),a=(0,i.useCallback)(()=>()=>{t([])},[t]);return(0,i.useMemo)(()=>({detailViewStack:e,setDetailViewStack:t,pushDetailView:o,popDetailView:r,resetDetailView:a,pushDetailViewCallback:l}),[e,r,o,a,l])},G=.15,J=({children:e,stack:t})=>{let o=y(t,(u,m)=>u?.length===m.length),r=k(t),l=t.length>(o??[]).length,a=o===void 0,s=a?0:l?10:-10,d=a?1:0;return i.default.createElement(A,{mode:"wait"},i.default.createElement(z,{key:`${t.length}_${o?.length}`,initial:{x:s,opacity:d},animate:{x:0,opacity:1},exit:{opacity:0},transition:{duration:G},ref:X},r||e))},P=()=>{let e=(0,i.useContext)(T);if(!e)throw new Error("Missing detail view context");return e},X=e=>{e&&e.parentElement&&(e.parentElement.scrollTop=0)};f();g();var w=h(x()),q=(0,w.createContext)({isOpen:!1,showSettingsMenu:p,hideSettingsMenu:p}),E=()=>(0,w.useContext)(q);f();g();var n=h(x());var W=c.section`
  z-index: 1;
  background-color: #222222;
  padding: 10px 16px;
  display: flex;
  flex-shrink: 0;
  flex-direction: row;
  align-items: center;
  justify-content: ${e=>e.justifyContent};
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #323232;
  height: ${e=>e.height}px;
  width: 100%;
`;W.defaultProps={justifyContent:"center",height:D};var R=c(b).attrs({size:16,weight:500,lineHeight:25})``;R.defaultProps={maxWidth:"280px",noWrap:!0};var K=c.div`
  display: flex;
  flex-shrink: 0;
  justify-content: center;
  align-items: center;
  padding-bottom: 17px;
  position: relative;
  width: 100%;
`,j=c(N)`
  position: absolute;
  right: 0;
`,v=c(B)`
  position: absolute;
  left: 0;
`,Se=({children:e,items:t,sections:o,icon:r,shouldWrap:l,onIconClick:a,onLeftButtonClick:s,useCloseButton:d})=>{let u=Y({withCloseButton:d??!1,onLeftButtonClick:s}),m=o&&o.length>0||t&&t.length>0;return n.default.createElement(K,null,u,n.default.createElement(b,{weight:500,size:22,noWrap:!l,maxWidth:"280px"},e),m||a?n.default.createElement(j,{sections:o,items:t,icon:r||n.default.createElement(L,null),onIconClick:a}):n.default.createElement("div",null))},$=c(W)`
  position: relative;
  border-bottom: none;

  &:after {
    content: "";
    position: absolute;
    bottom: 0;
    left: -20px;
    width: calc(100% + 40px);
    border-bottom: 1px solid #323232;
  }
`,Q=c.div`
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
`,be=({children:e,sections:t,items:o,icon:r,shouldWrap:l,onIconClick:a,onLeftButtonClick:s,disableIconBackground:d})=>{let u=Z(s),m=t&&t.length>0||o&&o.length>0;return n.default.createElement($,null,u,n.default.createElement(Q,null,typeof e=="string"?n.default.createElement(R,{noWrap:!l},e):e),m||a?n.default.createElement(j,{sections:t,items:o,icon:r,onIconClick:a,disableIconBackground:d}):n.default.createElement("div",null))};$.defaultProps={justifyContent:"center",height:D};var Y=({withCloseButton:e,onLeftButtonClick:t})=>{let{popDetailView:o,detailViewStackLength:r}=P();return(0,n.useMemo)(()=>r===0?n.default.createElement("div",null):n.default.createElement(v,{onClick:()=>{t?.(),o()},"data-testid":"header--back"},e?n.default.createElement(C,null):n.default.createElement(S,null)),[e])},Z=e=>{let{hideSettingsMenu:t}=E(),{popDetailView:o,detailViewStackLength:r}=P();return(0,n.useMemo)(()=>r>0?n.default.createElement(v,{onClick:()=>{o()},"data-testid":"header--back"},n.default.createElement(S,null)):n.default.createElement(v,{"data-testid":"settings-menu-close-button",onClick:e??t},n.default.createElement(C,null)),[])};export{ae as a,P as b,q as c,E as d,W as e,Se as f,be as g};
//# sourceMappingURL=chunk-5LEHT7IY.js.map
