import{ia as C}from"./chunk-6RSSZ6VM.js";import"./chunk-IUNHH544.js";import"./chunk-SWJ57CIZ.js";import"./chunk-LSEYVCUG.js";import"./chunk-BMUB2YXP.js";import"./chunk-BTQAICSK.js";import"./chunk-LJVOEF4C.js";import"./chunk-5R5I7UFN.js";import"./chunk-FS5WEDFF.js";import"./chunk-NJHVGQ3T.js";import"./chunk-V4KRVOHD.js";import"./chunk-PUJ7YG5C.js";import"./chunk-NJ4HEJET.js";import"./chunk-JOYNNZVI.js";import"./chunk-2WTSXO3L.js";import"./chunk-C5UDUURS.js";import"./chunk-5LEHT7IY.js";import"./chunk-DZ2NE3XW.js";import"./chunk-6PWMWQVM.js";import"./chunk-O2N6PUOM.js";import"./chunk-LO5C3EJB.js";import"./chunk-NGO5FOJW.js";import"./chunk-CSY6ZILA.js";import"./chunk-ZZPNXVUV.js";import"./chunk-ZON27MKP.js";import"./chunk-GDRVC4A7.js";import"./chunk-2LU4YM7A.js";import"./chunk-E6VR42GU.js";import"./chunk-W27Z2YZM.js";import{a as y}from"./chunk-3SURQQID.js";import"./chunk-XJTFMD4C.js";import"./chunk-4LYBFKKF.js";import"./chunk-2XU6ODO7.js";import"./chunk-7ZVEM3WY.js";import"./chunk-VQVTLSDS.js";import{k as T}from"./chunk-5LRZ7IFN.js";import{da as v,db as a}from"./chunk-ATEHMOFB.js";import{e as o}from"./chunk-2P7VAWV5.js";import{Va as u,va as S}from"./chunk-3HK6ZC5T.js";import"./chunk-UCBZOSRF.js";import"./chunk-FGZHIQDN.js";import"./chunk-ACZGMNYK.js";import"./chunk-YWEIY5NR.js";import"./chunk-U5F4RDP5.js";import"./chunk-LLAFONE3.js";import"./chunk-O3DDAITN.js";import"./chunk-ITDMYF4L.js";import"./chunk-SWF27PRY.js";import"./chunk-BTKBODVJ.js";import"./chunk-IBEI3NGL.js";import"./chunk-7DYYI5MT.js";import"./chunk-IQQ7P2L4.js";import"./chunk-VTNRGHVT.js";import"./chunk-P2WKOPZQ.js";import"./chunk-GXGQ5VTF.js";import"./chunk-W2BECDAL.js";import"./chunk-4CMCOVQN.js";import"./chunk-WFPABEAU.js";import"./chunk-WZYS47J2.js";import"./chunk-AIQ7AHJY.js";import"./chunk-6V7ED5GE.js";import"./chunk-T3HNWLEC.js";import"./chunk-T3JEJCOG.js";import"./chunk-XKUMOCJO.js";import"./chunk-EF7ER3CO.js";import"./chunk-2BA2A4Q2.js";import"./chunk-G7PMLIMH.js";import"./chunk-24ISZ5TA.js";import"./chunk-2J2WSGCG.js";import"./chunk-DHK5JDA3.js";import{m as w}from"./chunk-FI5JCZQR.js";import"./chunk-7XYHSLSH.js";import{Pa as d,w as m,x as f}from"./chunk-RISGBUNP.js";import"./chunk-X6UT6LAC.js";import"./chunk-HTY4DAML.js";import{a as O}from"./chunk-6MAAUKN7.js";import"./chunk-LYAMJYNC.js";import"./chunk-UNDMYLJW.js";import{f as x,h as c,n as p}from"./chunk-3KENBVE7.js";c();p();var e=x(O());var h=o.div`
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  height: 100%;
  width: 100%;
  overflow-y: scroll;
  padding: 16px;
`,k=o.div`
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-top: -20px;
`,b=o(a).attrs({size:28,weight:500,color:"#FFFFFF"})`
  margin-top: 24px;
`,P=o(a).attrs({size:16,weight:500,color:"#777777"})`
  padding: 0px 5px;
  margin-top: 9px;
  span {
    color: #ffffff;
  }
  label {
    color: #ab9ff2;
    cursor: pointer;
  }
`,F=o.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  height: fit-content;
`,A=o.div`
  margin-top: auto;
  width: 100%;
`,M=()=>{let{t:i}=w(),{mutateAsync:n}=u(),{handleHideModalVisibility:r,handleShowModalVisibility:t}=C(),{data:[s]}=d(["enable-swapper-skip-review"]),g=(0,e.useCallback)(()=>{t("swapConfirmation",void 0,{event:"showSwapModal",payload:{data:{uiContext:"SwapConfirmation"}}}),r("swapTermsOfService")},[t,r]),l=S({goToConfirmation:g});return{onAgreeClick:(0,e.useCallback)(()=>{n(!0),s?l():(t("swapReview",void 0,{event:"showSwapModal",payload:{data:{uiContext:"SwapReview"}}}),r("swapTermsOfService"))},[t,n,r,s,l]),onCancelClick:()=>{r("swapTermsOfService")},t:i}},B=()=>{self.open(m,"_blank")},L=()=>{self.open(f,"_blank")},_=e.default.memo(({onAgreeClick:i,onCancelClick:n,t:r})=>e.default.createElement(h,null,e.default.createElement(k,null,e.default.createElement(F,null,e.default.createElement(v,null),e.default.createElement(b,null,r("termsOfServicePrimaryText")),e.default.createElement(P,null,e.default.createElement(y,{i18nKey:"termsOfServiceDiscliamerFeesEnabledInterpolated"},"We have revised our Terms of Service. By clicking ",e.default.createElement("span",null,'"I Agree"')," you agree to our new",e.default.createElement("label",{onClick:B},"Terms of Service"),".",e.default.createElement("br",null),e.default.createElement("br",null),"Our new Terms of Service include a new ",e.default.createElement("label",{onClick:L},"fee structure")," for certain products.")))),e.default.createElement(A,null,e.default.createElement(T,{primaryText:r("termsOfServiceActionButtonAgree"),secondaryText:r("commandCancel"),onPrimaryClicked:i,onSecondaryClicked:n})))),V=()=>{let i=M();return e.default.createElement(_,{...i})},Z=V;export{V as SwapTermsOfServicePage,Z as default};
//# sourceMappingURL=SwapTermsOfServicePage-MWJQEN62.js.map
