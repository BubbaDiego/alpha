import{a as F}from"./chunk-5XFTDVKB.js";import{a as b}from"./chunk-OSGFD7XJ.js";import{a as w}from"./chunk-JDJZTN4M.js";import"./chunk-NMYDMQNK.js";import"./chunk-G67D6P6H.js";import"./chunk-2MTGVKD4.js";import"./chunk-MQYVKNLB.js";import"./chunk-6ZOJTCTS.js";import"./chunk-SHAEZV7V.js";import{D as x,ia as T}from"./chunk-6RSSZ6VM.js";import"./chunk-IUNHH544.js";import"./chunk-SWJ57CIZ.js";import"./chunk-LSEYVCUG.js";import"./chunk-BMUB2YXP.js";import"./chunk-BTQAICSK.js";import"./chunk-LJVOEF4C.js";import"./chunk-5R5I7UFN.js";import"./chunk-FS5WEDFF.js";import"./chunk-NJHVGQ3T.js";import"./chunk-V4KRVOHD.js";import"./chunk-PUJ7YG5C.js";import"./chunk-NJ4HEJET.js";import"./chunk-JOYNNZVI.js";import"./chunk-2WTSXO3L.js";import"./chunk-C5UDUURS.js";import{b as g}from"./chunk-5LEHT7IY.js";import"./chunk-DZ2NE3XW.js";import{a as y}from"./chunk-6PWMWQVM.js";import"./chunk-O2N6PUOM.js";import"./chunk-LO5C3EJB.js";import"./chunk-NGO5FOJW.js";import"./chunk-CSY6ZILA.js";import"./chunk-ZZPNXVUV.js";import"./chunk-ZON27MKP.js";import"./chunk-GDRVC4A7.js";import"./chunk-2LU4YM7A.js";import"./chunk-E6VR42GU.js";import"./chunk-W27Z2YZM.js";import"./chunk-3SURQQID.js";import"./chunk-XJTFMD4C.js";import"./chunk-4LYBFKKF.js";import"./chunk-2XU6ODO7.js";import"./chunk-7ZVEM3WY.js";import"./chunk-VQVTLSDS.js";import{j as P}from"./chunk-5LRZ7IFN.js";import"./chunk-ATEHMOFB.js";import{e as i}from"./chunk-2P7VAWV5.js";import{Pa as S,jb as R,ka as c,kb as h,qa as f,wa as v}from"./chunk-3HK6ZC5T.js";import"./chunk-UCBZOSRF.js";import"./chunk-FGZHIQDN.js";import"./chunk-ACZGMNYK.js";import"./chunk-YWEIY5NR.js";import"./chunk-U5F4RDP5.js";import{x as C}from"./chunk-LLAFONE3.js";import"./chunk-O3DDAITN.js";import"./chunk-ITDMYF4L.js";import"./chunk-SWF27PRY.js";import"./chunk-BTKBODVJ.js";import"./chunk-IBEI3NGL.js";import"./chunk-7DYYI5MT.js";import"./chunk-IQQ7P2L4.js";import"./chunk-VTNRGHVT.js";import"./chunk-P2WKOPZQ.js";import"./chunk-GXGQ5VTF.js";import"./chunk-W2BECDAL.js";import"./chunk-4CMCOVQN.js";import"./chunk-WFPABEAU.js";import"./chunk-WZYS47J2.js";import"./chunk-AIQ7AHJY.js";import"./chunk-6V7ED5GE.js";import"./chunk-T3HNWLEC.js";import"./chunk-T3JEJCOG.js";import{ie as u}from"./chunk-XKUMOCJO.js";import"./chunk-EF7ER3CO.js";import"./chunk-2BA2A4Q2.js";import"./chunk-G7PMLIMH.js";import"./chunk-24ISZ5TA.js";import"./chunk-2J2WSGCG.js";import"./chunk-DHK5JDA3.js";import{m as d}from"./chunk-FI5JCZQR.js";import"./chunk-7XYHSLSH.js";import"./chunk-RISGBUNP.js";import"./chunk-X6UT6LAC.js";import"./chunk-HTY4DAML.js";import{a as M}from"./chunk-6MAAUKN7.js";import"./chunk-LYAMJYNC.js";import"./chunk-UNDMYLJW.js";import{f as I,h as l,n as m}from"./chunk-3KENBVE7.js";l();m();var e=I(M());var D=i.div`
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  overflow-y: scroll;
  padding: 16px 16px ${78}px; // footer height + padding
`,E=i.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
`,H=i.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 16px;
  position: absolute;
  bottom: 0;
`,Q=i.div`
  background-color: #2a2a2a;
  border-radius: 6px;
  width: 100%;

  > *:first-child {
    border-bottom: 1px solid #222222;
  }
`,W=()=>{let{t}=d(),{handleHideModalVisibility:r}=T(),{pushDetailView:n}=g(),{resume:p}=f(),o=c(a=>a.quoteResponse),{data:s}=u(),V=(0,e.useMemo)(()=>s?.addresses.find(a=>a.networkID===o?.sellToken.chainId),[s,o]);(0,e.useEffect)(()=>{S()},[]),C(V,"SWAP_FUNGIBLE");let B=(0,e.useCallback)(()=>n(e.default.createElement(b,null)),[n]),k=v({goToConfirmation:B}),A=(0,e.useCallback)(()=>{p(),r("swapReview")},[r,p]);return{...k,hideSwapReview:A,t}},q=e.default.memo(({buyToken:t,sellToken:r,hideSwapReview:n,onSwap:p,t:o})=>{let{infoRowDisplayStrategy:s}=h();return e.default.createElement(D,null,e.default.createElement(E,null,e.default.createElement(x,{leftButton:{type:"close",onClick:n}},o("swapReviewFlowPrimaryText")),e.default.createElement(Q,null,e.default.createElement(w,{...r,title:o("swapReviewFlowYouPay")}),e.default.createElement(w,{...t,title:o("swapReviewFlowYouReceive")})),e.default.createElement(F,{isSwapReview:!0,rowDisplayStrategy:s})),e.default.createElement(H,null,e.default.createElement(y,{removeFooterExpansion:!0,removeShadowFooter:!0},e.default.createElement(P,{theme:"primary",onClick:p},o("swapReviewFlowActionButtonPrimary")))))}),N=()=>{let t=W();return e.default.createElement(R,null,e.default.createElement(q,{...t}))},Y=()=>e.default.createElement(N,null),ne=Y;export{Y as SwapReviewPage,ne as default};
//# sourceMappingURL=SwapReviewPage-57RM72NB.js.map
