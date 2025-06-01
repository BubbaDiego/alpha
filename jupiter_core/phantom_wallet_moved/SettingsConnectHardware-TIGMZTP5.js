import{a as F,c as L,d as N,g as D}from"./chunk-DOOHBDKQ.js";import{a as f}from"./chunk-KU3YVZXI.js";import"./chunk-G67D6P6H.js";import"./chunk-4K67M6WP.js";import"./chunk-QUC76K5A.js";import"./chunk-B22LDNQT.js";import{a as T}from"./chunk-K4RIO6ZZ.js";import"./chunk-Z5P32G6A.js";import"./chunk-MQYVKNLB.js";import"./chunk-6ZOJTCTS.js";import"./chunk-SHAEZV7V.js";import"./chunk-6RSSZ6VM.js";import"./chunk-IUNHH544.js";import"./chunk-SWJ57CIZ.js";import"./chunk-LSEYVCUG.js";import"./chunk-BMUB2YXP.js";import"./chunk-BTQAICSK.js";import"./chunk-LJVOEF4C.js";import"./chunk-5R5I7UFN.js";import"./chunk-FS5WEDFF.js";import{a as _}from"./chunk-NJHVGQ3T.js";import"./chunk-V4KRVOHD.js";import"./chunk-PUJ7YG5C.js";import"./chunk-NJ4HEJET.js";import"./chunk-JOYNNZVI.js";import"./chunk-2WTSXO3L.js";import"./chunk-C5UDUURS.js";import"./chunk-5LEHT7IY.js";import{a as m}from"./chunk-DZ2NE3XW.js";import"./chunk-6PWMWQVM.js";import"./chunk-O2N6PUOM.js";import"./chunk-LO5C3EJB.js";import{e as E}from"./chunk-NGO5FOJW.js";import"./chunk-CSY6ZILA.js";import"./chunk-ZZPNXVUV.js";import"./chunk-VJ2KIAYM.js";import"./chunk-ZON27MKP.js";import{a as g}from"./chunk-4EE3FYTU.js";import"./chunk-GDRVC4A7.js";import"./chunk-2LU4YM7A.js";import"./chunk-E6VR42GU.js";import"./chunk-KPH7I3T4.js";import"./chunk-W27Z2YZM.js";import"./chunk-3SURQQID.js";import"./chunk-XJTFMD4C.js";import"./chunk-4LYBFKKF.js";import"./chunk-2XU6ODO7.js";import"./chunk-7ZVEM3WY.js";import"./chunk-VQVTLSDS.js";import{a as O,b as $}from"./chunk-5LRZ7IFN.js";import{q as P}from"./chunk-ATEHMOFB.js";import{e as c}from"./chunk-2P7VAWV5.js";import"./chunk-3HK6ZC5T.js";import"./chunk-UCBZOSRF.js";import"./chunk-FGZHIQDN.js";import"./chunk-ACZGMNYK.js";import"./chunk-YWEIY5NR.js";import"./chunk-U5F4RDP5.js";import"./chunk-LLAFONE3.js";import"./chunk-O3DDAITN.js";import"./chunk-ITDMYF4L.js";import"./chunk-SWF27PRY.js";import"./chunk-BTKBODVJ.js";import"./chunk-IBEI3NGL.js";import"./chunk-7DYYI5MT.js";import"./chunk-IQQ7P2L4.js";import"./chunk-VTNRGHVT.js";import"./chunk-P2WKOPZQ.js";import"./chunk-GXGQ5VTF.js";import"./chunk-W2BECDAL.js";import"./chunk-4CMCOVQN.js";import"./chunk-WFPABEAU.js";import"./chunk-WZYS47J2.js";import"./chunk-AIQ7AHJY.js";import"./chunk-6V7ED5GE.js";import"./chunk-T3HNWLEC.js";import"./chunk-T3JEJCOG.js";import{Td as v,_d as B}from"./chunk-XKUMOCJO.js";import"./chunk-EF7ER3CO.js";import"./chunk-2BA2A4Q2.js";import"./chunk-G7PMLIMH.js";import"./chunk-24ISZ5TA.js";import"./chunk-2J2WSGCG.js";import"./chunk-DHK5JDA3.js";import"./chunk-FI5JCZQR.js";import"./chunk-7XYHSLSH.js";import"./chunk-RISGBUNP.js";import"./chunk-X6UT6LAC.js";import{g as y}from"./chunk-HTY4DAML.js";import{a as H}from"./chunk-6MAAUKN7.js";import"./chunk-LYAMJYNC.js";import"./chunk-UNDMYLJW.js";import{f as b,h as r,n}from"./chunk-3KENBVE7.js";r();n();var o=b(H());r();n();var i=b(H());r();n();var G=c(m)`
  cursor: pointer;
  width: 24px;
  height: 24px;
  transition: background-color 200ms ease;
  background-color: ${t=>t.$isExpanded?"#000":"#333"} !important;
  :hover {
    background-color: #444444;
    svg {
      fill: white;
    }
  }
  svg {
    fill: ${t=>t.$isExpanded?"white":"#666666"};
    transition: fill 200ms ease;
    position: relative;
    ${t=>t.top?`top: ${t.top}px;`:""}
    ${t=>t.right?`right: ${t.right}px;`:""}
  }
`;var U=c(_).attrs({justify:"space-between"})`
  background-color: #222222;
  padding: 10px 16px;
  border-bottom: 1px solid #323232;
  height: 46px;
  opacity: ${t=>t.opacity??"1"};
`,V=c.div`
  display: flex;
  margin-left: 10px;
  > * {
    margin-right: 10px;
  }
`,I=c.div`
  width: 24px;
  height: 24px;
`,M=({onBackClick:t,totalSteps:a,currentStepIndex:p,isHidden:l,showBackButtonOnFirstStep:e,showBackButton:u=!0})=>i.default.createElement(U,{opacity:l?0:1},u&&(e||p!==0)?i.default.createElement(G,{right:1,onClick:t},i.default.createElement(P,null)):i.default.createElement(I,null),i.default.createElement(V,null,y(a).map(s=>{let d=s<=p?"#AB9FF2":"#333";return i.default.createElement(m,{key:s,diameter:12,color:d})})),i.default.createElement(I,null));r();n();var z=()=>{let{mutateAsync:t}=B(),{hardwareStepStack:a,pushStep:p,popStep:l,currentStep:e,setOnConnectHardwareAccounts:u,setOnConnectHardwareDone:w,setExistingAccounts:s}=F(),{data:d=[],isFetched:x,isError:k}=v(),C=E(a,(h,J)=>h?.length===J.length),W=a.length>(C??[]).length,A=C?.length===0,X={initial:{x:A?0:W?150:-150,opacity:A?1:0},animate:{x:0,opacity:1},exit:{opacity:0},transition:{duration:.2}},j=(0,o.useCallback)(()=>{e()?.props.preventBack||(e()?.props.onBackCallback&&e()?.props.onBackCallback?.(),l())},[e,l]);return T(()=>{u(async h=>{await t(h),await g.set(f,!await g.get(f))}),w(()=>self.close()),p(o.default.createElement(D,null))},a.length===0),(0,o.useEffect)(()=>{s({data:d,isFetched:x,isError:k})},[d,x,k,s]),o.default.createElement(L,null,o.default.createElement(M,{totalSteps:3,onBackClick:j,showBackButton:!e()?.props.preventBack,currentStepIndex:a.length-1}),o.default.createElement($,{mode:"wait"},o.default.createElement(O.div,{style:{display:"flex",flexGrow:1},key:`${a.length}_${C?.length}`,...X},o.default.createElement(N,null,e()))))},yt=z;export{yt as default};
//# sourceMappingURL=SettingsConnectHardware-TIGMZTP5.js.map
