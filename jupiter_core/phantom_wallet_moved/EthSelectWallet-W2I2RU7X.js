import{e as f,g,h as A,i as k}from"./chunk-VG53HREX.js";import"./chunk-4K67M6WP.js";import{a as h}from"./chunk-6ZOJTCTS.js";import"./chunk-SHAEZV7V.js";import"./chunk-VJ2KIAYM.js";import"./chunk-W27Z2YZM.js";import{db as x,pa as d}from"./chunk-ATEHMOFB.js";import{e}from"./chunk-2P7VAWV5.js";import"./chunk-UCBZOSRF.js";import"./chunk-SWF27PRY.js";import"./chunk-BTKBODVJ.js";import{L as r}from"./chunk-EF7ER3CO.js";import{c as m,r as l,w as u}from"./chunk-G7PMLIMH.js";import"./chunk-24ISZ5TA.js";import"./chunk-2J2WSGCG.js";import"./chunk-DHK5JDA3.js";import{m as c}from"./chunk-FI5JCZQR.js";import"./chunk-7XYHSLSH.js";import"./chunk-RISGBUNP.js";import"./chunk-X6UT6LAC.js";import"./chunk-HTY4DAML.js";import{a as T}from"./chunk-6MAAUKN7.js";import"./chunk-LYAMJYNC.js";import"./chunk-UNDMYLJW.js";import{f as E,h as p,n as a}from"./chunk-3KENBVE7.js";p();a();var t=E(T());var _=e.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-bottom: 6px;
`,w=e.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`,S=e.div`
  background: #2a2a2a;
  border-radius: 6px;
  padding: 12px 16px;
`,I=e.div`
  display: flex;
  flex-direction: row;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  width: fit-content;
  margin-bottom: 8px;

  > span {
    min-height: 14px !important;
    height: 14px !important;
    min-width: 14px !important;
    width: 14px !important;
    border-radius: 3px !important;
  }
`,W=e.div`
  display: flex;
  gap: 16px;
`,b=e.div`
  padding: 27px 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
`,G=t.default.memo(({requestId:i})=>{let{t:n}=c(),s=f(),[o,y]=(0,t.useState)(!1),C=(0,t.useCallback)(()=>{s({jsonrpc:"2.0",id:i,result:o?r.user_selectEthWallet.result.enum.ALWAYS_USE_PHANTOM:r.user_selectEthWallet.result.enum.CONTINUE_WITH_PHANTOM})},[i,s,o]),M=(0,t.useCallback)(()=>{s({jsonrpc:"2.0",id:i,result:o?r.user_selectEthWallet.result.enum.ALWAYS_USE_METAMASK:r.user_selectEthWallet.result.enum.CONTINUE_WITH_METAMASK})},[i,s,o]);return t.default.createElement(A,null,t.default.createElement(g,{style:{display:"flex",alignItems:"center"}},t.default.createElement(b,null,t.default.createElement(h,{icon:t.default.createElement(W,null,t.default.createElement(m.LogoFill,{size:64,color:"accentPrimary"}),t.default.createElement(d,{width:64,height:64})),primaryText:n("whichExtensionToConnectWith"),headerStyle:"small"}))),t.default.createElement(k,{plain:!0},t.default.createElement(_,null,t.default.createElement(w,null,t.default.createElement(l,{onClick:M,testID:"select_wallet--metamask"},n("useMetaMask"))),t.default.createElement(w,null,t.default.createElement(l,{theme:"primary",onClick:C,testID:"select_wallet--phantom"},n("usePhantom"))),t.default.createElement(S,null,t.default.createElement(I,null,t.default.createElement(u,{checked:o,onChange:()=>y(!o),label:{text:n("dontAskMeAgain"),color:"textPrimary"},shape:"square"})),t.default.createElement(x,{color:"#777777",size:13,weight:500,lineHeight:16,textAlign:"left"},n("configureInSettings"))))))}),L=G;export{G as EthSelectWallet,L as default};
//# sourceMappingURL=EthSelectWallet-W2I2RU7X.js.map
