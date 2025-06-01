import{h as m}from"./chunk-2WTSXO3L.js";import{j as l}from"./chunk-5LRZ7IFN.js";import{db as e}from"./chunk-ATEHMOFB.js";import{e as o}from"./chunk-2P7VAWV5.js";import{m as a}from"./chunk-FI5JCZQR.js";import{a as v}from"./chunk-6MAAUKN7.js";import{f as T,h as r,n as p}from"./chunk-3KENBVE7.js";r();p();var t=T(v());var y=o.div`
  position: relative;
  width: 100%;
`,B=o.div`
  position: absolute;
  right: 12px;
  top: calc(50% - 27px / 2);
  display: flex;
  align-items: center;
`,S=o(e)`
  margin-right: ${n=>`calc(120px - (${n.textLength}px * 5))`};
`,w=o(e)`
  margin-right: 10px;
`,C=o(l)`
  height: 27px;
`,I=o.div`
  position: relative;
  width: 100%;
  padding: 0px 8px;
  overflow: hidden;
  text-overflow: ellipsis;
`,P=({symbol:n,alignSymbol:g,buttonText:s,width:d,borderRadius:u,onSetTarget:x,targetButtonDisabled:h,placeholder:c,...i})=>{let{t:f}=a(),b=i.value.toString().length;return t.default.createElement(y,null,t.default.createElement(m,{placeholder:c??f("maxInputAmount"),borderRadius:u,...i}),t.default.createElement(B,null,g==="left"?t.default.createElement(S,{size:16,textLength:b,color:"#777777"},n):t.default.createElement(w,{size:16,color:"#777777"},n),t.default.createElement(C,{disabled:h,fontSize:13,width:`${d}px`,borderRadius:"100px",paddingY:4,onClick:x},t.default.createElement(I,null,s))))};export{P as a};
//# sourceMappingURL=chunk-TEKKEVSO.js.map
