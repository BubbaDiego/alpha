import{a as O,c as V}from"./chunk-RCVXXPN7.js";import{a as G}from"./chunk-4NV2UNXD.js";import{j as W}from"./chunk-5LRZ7IFN.js";import{Aa as p,Ba as g,Ca as S,Da as f,Ea as x,Fa as k,Ga as y,Ha as w,Ia as L,Ja as T,Ka as v,La as C,Ma as P,Na as M,Oa as b,Pa as a,Qa as D,db as F,ya as I,za as d}from"./chunk-ATEHMOFB.js";import{e as o}from"./chunk-2P7VAWV5.js";import{b as l}from"./chunk-ITDMYF4L.js";import"./chunk-SWF27PRY.js";import"./chunk-BTKBODVJ.js";import"./chunk-WZYS47J2.js";import"./chunk-6V7ED5GE.js";import"./chunk-T3HNWLEC.js";import"./chunk-XKUMOCJO.js";import"./chunk-EF7ER3CO.js";import"./chunk-DHK5JDA3.js";import{b as u}from"./chunk-FI5JCZQR.js";import"./chunk-7XYHSLSH.js";import"./chunk-RISGBUNP.js";import"./chunk-X6UT6LAC.js";import"./chunk-HTY4DAML.js";import{a as h}from"./chunk-6MAAUKN7.js";import"./chunk-LYAMJYNC.js";import"./chunk-UNDMYLJW.js";import{f as m,h as i,n as c}from"./chunk-3KENBVE7.js";i();c();var t=m(h());i();c();var A=m(h());var z={[G]:a,vote:y,"vote-2":w,stake:L,"stake-2":T,view:v,chat:C,tip:P,mint:M,"mint-2":b,"generic-link":a,"generic-add":D,discord:I,twitter:d,"twitter-2":p,x:p,instagram:g,telegram:S,leaderboard:k,gaming:f,"gaming-2":x};function B({icon:s,...n}){let r=z[s];return A.default.createElement(r,{...n})}var E=o.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  margin-top: -16px; // compensate for generic screen margins
`,H=o.footer`
  margin-top: auto;
  flex-shrink: 0;
  min-height: 16px;
`,Y=o.div`
  overflow: scroll;
`,_=o.ul`
  flex: 1;
  max-height: 350px;
  padding-top: 16px; // compensate for the override of the generic screen margins
`,j=o.li``,q=o.div`
  display: flex;
  align-items: center;
  padding: 6px 12px;
`,N=o(F)`
  text-align: left;
`;N.defaultProps={margin:"12px 0px"};function J({shortcuts:s,...n}){let r=(0,t.useMemo)(()=>n.hostname.includes("//")?new URL(n.hostname).hostname:n.hostname,[n.hostname]);return t.default.createElement(E,null,t.default.createElement(Y,null,t.default.createElement(_,null,s.map(e=>t.default.createElement(j,{key:e.uri},t.default.createElement(W,{type:"button",onClick:()=>{l.capture("walletShortcutsLinkOpenClick",O(n,e)),self.open(e.uri)},theme:"text",paddingY:6},t.default.createElement(q,null,t.default.createElement(B,{icon:V(e.uri,e.icon)})),e.label))))),t.default.createElement(H,null,r&&t.default.createElement(N,{color:"#777777",size:14,lineHeight:17},u("shortcutsWarningDescription",{url:r}))))}var ct=J;export{J as ShortcutsModal,ct as default};
//# sourceMappingURL=ShortcutsModal-23DGXM7V.js.map
