import{a as O}from"./chunk-XQ5AWW2B.js";import{a as P}from"./chunk-G67D6P6H.js";import{a as H,b as q,c as I}from"./chunk-2MTGVKD4.js";import{a as B}from"./chunk-C5UDUURS.js";import{a as c}from"./chunk-3SURQQID.js";import{a as x,b as y,h as b,j as f,l as v}from"./chunk-5LRZ7IFN.js";import{db as V}from"./chunk-ATEHMOFB.js";import{e as d}from"./chunk-2P7VAWV5.js";import{i as F}from"./chunk-FGZHIQDN.js";import{p as A}from"./chunk-U5F4RDP5.js";import{l as E,m as k}from"./chunk-G7PMLIMH.js";import{R as g}from"./chunk-HTY4DAML.js";import{a as w}from"./chunk-6MAAUKN7.js";import{f as C,h as m,n as l}from"./chunk-3KENBVE7.js";m();l();var n=C(w());m();l();var t=C(w());var K=d.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  width: 100%;
  padding: ${r=>r.addScreenPadding?"16px":"0"};
`,J=d.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-grow: 1;
`,j=d.div`
  width: 100%;
  > * {
    margin-top: 10px;
  }
  padding: 16px;
`,G=d(B).attrs({align:"center",justify:"center",margin:"0 0 15px 0"})`
  position: relative;
  border-radius: 50%;
  background-color: ${g("#AB9FF2",.2)};
  box-shadow: 0 0 0 20px ${g("#AB9FF2",.2)};
`,W=d(V).attrs({size:28,weight:500,color:"#FFFFFF"})`
  margin-top: 24px;
  margin-left: 12px;
  margin-right: 12px;
`,X=()=>t.default.createElement(G,null,t.default.createElement(b,{diameter:54,color:"#AB9FF2",trackColor:"#181818"})),z=({message:r})=>t.default.createElement(E,{marginX:12,alignItems:"center"},Array.isArray(r)?r.map((i,o)=>t.default.createElement(k,{key:`message-${o}`,font:"body",color:"textSecondary",align:"center",marginX:12,marginTop:16},i)):t.default.createElement(k,{font:"body",marginTop:16,color:"textSecondary",align:"center"},r)),T=({header:r,icon:i,title:o,message:s,txHash:e,txHashTitle:u,isClosable:S,primaryButton:p,secondaryButton:a})=>t.default.createElement(K,null,r,t.default.createElement(J,null,t.default.createElement(y,{mode:"wait",initial:!0},t.default.createElement(x.div,{key:o,initial:{opacity:0},animate:{opacity:1},exit:{opacity:0},transition:{duration:.2}},i)),t.default.createElement(W,null,o),t.default.createElement(z,{message:s}),e&&t.default.createElement(y,{mode:"wait",initial:!1},t.default.createElement(x.div,{key:e,initial:{opacity:0,y:16},animate:{opacity:1,y:0},exit:{opacity:0},transition:{duration:.2}},t.default.createElement(O,{txHash:e},u)))),S?t.default.createElement(j,null,a&&p?t.default.createElement(v,{buttons:[{text:a.title,onClick:a.onPress},{theme:"primary",text:p.title,onClick:p.onPress}]}):p?t.default.createElement(f,{theme:"primary",onClick:p.onPress},p.title):a?t.default.createElement(f,{onClick:a.onPress},a.title):null):null),M=({ledgerAction:r,numberOfTransactions:i,cancel:o,ledgerApp:s})=>t.default.createElement(K,{addScreenPadding:!0},t.default.createElement(q,{ledgerAction:r,numberOfTransactions:i,cancel:o,ledgerApp:s})),$=({title:r,message:i,txHash:o,txHashTitle:s,primaryButton:e})=>t.default.createElement(T,{icon:t.default.createElement(X,null),message:i,title:r,txHash:o,txHashTitle:s,primaryButton:e,isClosable:!!o}),L=({title:r,message:i,txHash:o,txHashTitle:s,primaryButton:e})=>t.default.createElement(T,{icon:t.default.createElement(P,{type:"failure"}),message:i,title:r,txHash:o,txHashTitle:s,primaryButton:e,isClosable:!0}),N=({title:r,message:i,txHash:o,txHashTitle:s,primaryButton:e,secondaryButton:u})=>t.default.createElement(T,{icon:t.default.createElement(P,{type:"success"}),title:r,message:i,txHash:o,txHashTitle:s,isClosable:!0,primaryButton:e,secondaryButton:u});var h=d.a.attrs({target:"_blank",rel:"noopener noreferrer"})`
  color: ${r=>r.theme.purple};
  text-decoration: none;
  cursor: pointer;
`,U=({txError:r,addressType:i,statusPageProps:o,executeConvertStake:s,onClose:e})=>H(r)?n.default.createElement(I,{ledgerActionError:r,onRetryClick:s,onCancelClick:e}):o.type==="error"?n.default.createElement(L,{...o}):n.default.createElement(M,{ledgerAction:s,numberOfTransactions:1,cancel:e,ledgerApp:A(i)}),xt=n.default.memo(r=>{let{process:i,addressType:o,isLedger:s,statusPageProps:e,txError:u,onClose:S,executeLiquidStake:p,learnMoreLink:a}=r;if(s&&!e.txHash)return n.default.createElement(U,{txError:u,addressType:o,statusPageProps:e,executeConvertStake:p,onClose:S});switch(e.type){case"loading":return n.default.createElement($,{...e});case"error":return n.default.createElement(L,{...e});case"success":{let _=i==="convert"?[n.default.createElement(c,{i18nKey:"liquidStakeDepositStakeDisclaimer"},"You'll receive JitoSOL in 10 hours. ",n.default.createElement(h,{href:F},"Learn more")),n.default.createElement(c,{i18nKey:"convertStakeStatusSuccessMessage"},"Earn additional rewards with your JitoSOL ",n.default.createElement(h,{href:a},"here."))]:n.default.createElement(c,{i18nKey:"convertStakeStatusSuccessMessage"},"Earn additional rewards with your JitoSOL ",n.default.createElement(h,{href:a},"here."));return n.default.createElement(N,{title:e.title,txHash:e.txHash,txHashTitle:e.txHashTitle,primaryButton:e.primaryButton,secondaryButton:e.secondaryButton,message:_})}default:throw new Error("Unsupported status page type")}});export{xt as a};
//# sourceMappingURL=chunk-UJBBC32U.js.map
