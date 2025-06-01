import{a as l,c as s}from"./chunk-NMYDMQNK.js";import{a as I}from"./chunk-G67D6P6H.js";import{aa as h,ia as T}from"./chunk-6RSSZ6VM.js";import"./chunk-IUNHH544.js";import"./chunk-SWJ57CIZ.js";import"./chunk-LSEYVCUG.js";import"./chunk-BMUB2YXP.js";import"./chunk-BTQAICSK.js";import"./chunk-LJVOEF4C.js";import"./chunk-5R5I7UFN.js";import"./chunk-FS5WEDFF.js";import"./chunk-NJHVGQ3T.js";import"./chunk-V4KRVOHD.js";import"./chunk-PUJ7YG5C.js";import"./chunk-NJ4HEJET.js";import"./chunk-JOYNNZVI.js";import"./chunk-2WTSXO3L.js";import"./chunk-C5UDUURS.js";import"./chunk-5LEHT7IY.js";import"./chunk-DZ2NE3XW.js";import"./chunk-6PWMWQVM.js";import"./chunk-O2N6PUOM.js";import"./chunk-LO5C3EJB.js";import"./chunk-NGO5FOJW.js";import"./chunk-CSY6ZILA.js";import"./chunk-ZZPNXVUV.js";import"./chunk-ZON27MKP.js";import"./chunk-GDRVC4A7.js";import"./chunk-2LU4YM7A.js";import"./chunk-E6VR42GU.js";import"./chunk-W27Z2YZM.js";import"./chunk-3SURQQID.js";import"./chunk-XJTFMD4C.js";import"./chunk-4LYBFKKF.js";import"./chunk-2XU6ODO7.js";import"./chunk-7ZVEM3WY.js";import"./chunk-VQVTLSDS.js";import{j as g,k as C}from"./chunk-5LRZ7IFN.js";import{db as c}from"./chunk-ATEHMOFB.js";import{e as o}from"./chunk-2P7VAWV5.js";import"./chunk-3HK6ZC5T.js";import"./chunk-UCBZOSRF.js";import"./chunk-FGZHIQDN.js";import"./chunk-ACZGMNYK.js";import"./chunk-YWEIY5NR.js";import"./chunk-U5F4RDP5.js";import"./chunk-LLAFONE3.js";import"./chunk-O3DDAITN.js";import"./chunk-ITDMYF4L.js";import"./chunk-SWF27PRY.js";import"./chunk-BTKBODVJ.js";import"./chunk-IBEI3NGL.js";import"./chunk-7DYYI5MT.js";import"./chunk-IQQ7P2L4.js";import"./chunk-VTNRGHVT.js";import"./chunk-P2WKOPZQ.js";import"./chunk-GXGQ5VTF.js";import"./chunk-W2BECDAL.js";import"./chunk-4CMCOVQN.js";import"./chunk-WFPABEAU.js";import"./chunk-WZYS47J2.js";import"./chunk-AIQ7AHJY.js";import"./chunk-6V7ED5GE.js";import"./chunk-T3HNWLEC.js";import"./chunk-T3JEJCOG.js";import{Db as x,gb as r,ob as y}from"./chunk-XKUMOCJO.js";import"./chunk-EF7ER3CO.js";import"./chunk-2BA2A4Q2.js";import{l as B}from"./chunk-G7PMLIMH.js";import"./chunk-24ISZ5TA.js";import"./chunk-2J2WSGCG.js";import"./chunk-DHK5JDA3.js";import{m as d}from"./chunk-FI5JCZQR.js";import"./chunk-7XYHSLSH.js";import"./chunk-RISGBUNP.js";import"./chunk-X6UT6LAC.js";import"./chunk-HTY4DAML.js";import{a as v}from"./chunk-6MAAUKN7.js";import"./chunk-LYAMJYNC.js";import"./chunk-UNDMYLJW.js";import{f as k,h as p,n as u}from"./chunk-3KENBVE7.js";p();u();var n=k(v());var M=o.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow-y: scroll;
`,D=o.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 90px;
`,P=o(c).attrs({size:28,weight:500,color:"#FFF"})`
  margin: 16px;
`,S=o(c).attrs({size:14,weight:400,lineHeight:17,color:"#999"})`
  max-width: 275px;

  span {
    color: white;
  }
`,V=({networkId:t,token:a})=>{let{t:i}=d(),{handleHideModalVisibility:f}=T(),m=(0,n.useCallback)(()=>{f("insufficientBalance")},[f]),b=t&&y(x(r.getChainID(t))),{canBuy:w,openBuy:F}=h({caip19:b||"",context:"modal",analyticsEvent:"fiatOnrampFromInsufficientBalance"}),e=t?r.getTokenSymbol(t):i("tokens");return n.default.createElement(M,null,n.default.createElement("div",null,n.default.createElement(D,null,n.default.createElement(I,{type:"failure",backgroundWidth:75}),n.default.createElement(P,null,i("insufficientBalancePrimaryText",{tokenSymbol:e})),n.default.createElement(S,null,i("insufficientBalanceSecondaryText",{tokenSymbol:e})),a?n.default.createElement(B,{borderRadius:8,gap:1,marginTop:32,width:"100%"},n.default.createElement(l,{label:i("insufficientBalanceRemaining")},n.default.createElement(s,{color:"#EB3742"},`${a.balance} ${e}`)),n.default.createElement(l,{label:i("insufficientBalanceRequired")},n.default.createElement(s,null,`${a.required} ${e}`))):null)),w?n.default.createElement(C,{primaryText:i("buyAssetInterpolated",{tokenSymbol:e}),onPrimaryClicked:F,secondaryText:i("commandCancel"),onSecondaryClicked:m}):n.default.createElement(g,{onClick:m},i("commandCancel")))},K=V;export{V as InsufficientBalance,K as default};
//# sourceMappingURL=InsufficientBalance-GCX5M75G.js.map
