import{f as ue}from"./chunk-O7S62B4R.js";import{a as W,c as z,d as K,e as H,f as _}from"./chunk-SQ2J5G23.js";import{a as S}from"./chunk-NJHVGQ3T.js";import{a as E}from"./chunk-NJ4HEJET.js";import{a as me,b as $}from"./chunk-2WTSXO3L.js";import{a as le,b as ce}from"./chunk-GDRVC4A7.js";import{db as g,p as L}from"./chunk-ATEHMOFB.js";import{e as s}from"./chunk-2P7VAWV5.js";import{b as pe}from"./chunk-ITDMYF4L.js";import{b as ie}from"./chunk-6V7ED5GE.js";import{a as Y,h as Z}from"./chunk-T3HNWLEC.js";import{Jd as M,Md as re,Me as de,Pd as ne,Wd as ae,Xc as R,dd as ee,gb as A,ia as J,md as te,ne as se,rd as oe,te as V}from"./chunk-XKUMOCJO.js";import{n as b,v}from"./chunk-G7PMLIMH.js";import{m as w}from"./chunk-FI5JCZQR.js";import{F as q,G,fa as Q,va as U}from"./chunk-RISGBUNP.js";import{a as C}from"./chunk-6MAAUKN7.js";import{f as I,h as l,n as c}from"./chunk-3KENBVE7.js";l();c();var fe=I(C());var Ge=e=>{let t=te(),o=R(),{data:d=[]}=oe(),{mutateAsync:i}=se(),{mutateAsync:m}=ae(),h=Q();return{handleImportSeed:(0,fe.useCallback)(async({mnemonic:P,accountMetas:T,accountName:x,offsetIndex:D=0,seedlessOnboardingType:F})=>{let N={},y=await(e==="seed"?le(P,T,x):ce(P,T,x));if(y.forEach((f,p)=>{N[f.identifier]=Y({account:f,syncedAccounts:d,index:p,offsetIndex:D})}),y.length===0)throw new Error("Failed to set seed phrase");await m({metadataBatch:N}),await i({identifier:y[0].identifier});try{await t.downloadSyncedAccounts()}catch{}if(e==="seedless"&&F==="seedlessBackup"){try{let f=new Set(y.map(p=>p.seedIdentifier));await Promise.all([...f].map(p=>o.addAuthFactor({secretIdentifier:p})))}catch{U.captureError(new Error("Unable to add auth factor for se*dless!"),"Auth")}try{await t.uploadSyncedAccounts(y.map(f=>f.identifier))}catch{U.captureError(new Error("Unable to sync accounts se*dless!"),"Auth")}}pe.capture("addSeedAccount",{data:{walletIndex:D+1}}),ee(h)},[d,m,i,e,t,h,o])}};l();c();var n=I(C());l();c();var r=I(C());var he=({onChange:e,value:t,networkID:o})=>{let d=M(),i=(0,r.useMemo)(()=>{if(!o)return[];let h=A.getAddressTypes(o);return d.filter(u=>h.includes(u))},[d,o]);if(!i||i.length===0)return null;let m=i.includes(t)?t:i[0];return r.default.createElement(ve,{onChange:e,value:m},({isExpanded:h})=>r.default.createElement(r.default.Fragment,null,r.default.createElement(Te,{isActive:h},r.default.createElement(ye,{networkID:o,addressType:m},r.default.createElement(Se,null,r.default.createElement(L,{fill:"#777",width:10})))),r.default.createElement(ke,{portal:!1},r.default.createElement(H,{maxHeight:"300px"},i?.filter(u=>u!==m)?.map(u=>r.default.createElement(Pe,{key:u,value:u},r.default.createElement(ye,{networkID:o,addressType:u})))))))},ye=({addressType:e,networkID:t,children:o})=>!t||!e?null:r.default.createElement(S,{justify:"space-between"},r.default.createElement(S,null,r.default.createElement(E,{networkID:t,size:32}),r.default.createElement(De,null,J.getDisplayName(e))),o),ve=s(W)`
  width: 100%;
  position: relative;
`,Se=s.div`
  display: inline-flex;
  line-height: 0;
`,Te=s(({isActive:e,...t})=>r.default.createElement(z,{...t}))`
  padding: 8px 16px 8px 12px;

  ${Se} {
    svg {
      transform: rotate(${e=>e.isActive?"-180deg":"0"});
      transition: transform 0.2s ease-in-out;
    }
  }
`,ke=s(K)`
  z-index: 2;
  width: 100%;
`,Pe=s(_)`
  padding: 8px 16px 8px 12px;
  min-height: 50px;
`,De=s(g).attrs({size:16,weight:400,lineHeight:19,margin:"0 0 0 8px"})``;l();c();var a=I(C());var Fe=s(W)`
  width: 100%;
  position: relative;
`,Ae=s.div`
  display: inline-flex;
  line-height: 0;
`,Ne=s(({isActive:e,...t})=>a.default.createElement(z,{...t}))`
  padding: 8px 16px 8px 12px;

  ${Ae} {
    svg {
      transform: rotate(${e=>e.isActive?"-180deg":"0"});
      transition: transform 0.2s ease-in-out;
    }
  }
`,Be=s(K)`
  z-index: 2;
  width: 100%;
`,Me=s(_)`
  padding: 8px 16px 8px 12px;
  min-height: 50px;
`,Le=s(g).attrs({size:16,weight:400,lineHeight:19,margin:"0 0 0 8px"})``,ge=({onChange:e,value:t})=>{let o=re();return a.default.createElement(Fe,{onChange:e,value:t},({isExpanded:d})=>a.default.createElement(a.default.Fragment,null,a.default.createElement(Ne,{isActive:d},a.default.createElement(we,{networkID:t},a.default.createElement(Ae,null,a.default.createElement(L,{fill:"#777",width:10})))),a.default.createElement(Be,{portal:!1},a.default.createElement(H,{maxHeight:"300px"},o.filter(i=>i!==t).map(i=>a.default.createElement(Me,{key:i,value:i},a.default.createElement(we,{networkID:i})))))))},we=({networkID:e,children:t})=>a.default.createElement(S,{justify:"space-between"},a.default.createElement(S,null,a.default.createElement(E,{networkID:e,size:32}),a.default.createElement(Le,null,A.getNetworkName(e))),t);var _t=({onClick:e,disabled:t})=>{let{t:o}=w(),d=ne();return n.default.createElement(b,{topLeft:{text:o("addAccountImportWalletPrimaryText"),font:"bodyMedium"},bottomLeft:{text:o(d?"addAccountImportWalletSolanaSecondaryText":"addAccountImportWalletSecondaryText")},start:n.default.createElement(v,{backgroundColor:"borderPrimary",color:"textPrimary",icon:"Download",shape:"circle",size:32}),onClick:e,disabled:t})},Ot=({control:e,getValues:t,register:o,setValue:d,trigger:i,errors:m,nameValidations:h,privateKey:u,privateKeyValidations:P,addressPreview:T})=>{let{t:x}=w(),D=de(p=>p.editableAccountMetadata),F=t("networkID"),N=A.getAddressTypes(F),y=M(),f=y.filter(p=>N.includes(p));return n.default.createElement(ue,null,n.default.createElement(V,{name:"networkID",control:e,render:({field:{onChange:p,value:O}})=>y.length===1?n.default.createElement(n.default.Fragment,null):n.default.createElement(ge,{onChange:B=>{p(B);let Ie=A.getAddressTypes(B),Ce=y.filter(be=>Ie.includes(be));d("addressType",Ce[0]),u&&i("privateKey")},value:O})}),n.default.createElement(V,{name:"addressType",control:e,render:({field:{onChange:p,value:O}})=>f.length===1?n.default.createElement(n.default.Fragment,null):n.default.createElement(he,{onChange:B=>{p(B),u&&i("privateKey")},value:O,networkID:F})}),n.default.createElement($.WithWarning,{placeholder:x("addAccountImportAccountName"),defaultValue:D?.name,warning:!!m.name,warningMessage:m.name?.message,autoComplete:"off",maxLength:ie,...o("name",h)}),n.default.createElement(xe.WithWarning,{placeholder:x("addAccountImportAccountPrivateKey"),defaultValue:"",warning:!!m.privateKey,warningMessage:m.privateKey?.message,autoComplete:"off",...o("privateKey",P)}),T?n.default.createElement(Ee,{label:x("settingsWalletAddress"),pubkey:T}):null)},Ee=n.default.memo(({label:e,pubkey:t})=>n.default.createElement(S,{justify:"space-between",align:"center",margin:"-7px 0 0"},n.default.createElement(g,{size:16,weight:600},e),n.default.createElement(g,{size:16},Z(t,4)))),We=s($.withComponent("textarea"))`
  height: 120px;
  text-align: start;
  resize: none;
  -webkit-text-security: disc;
`,xe=me(We);xe.defaultProps={fontSize:"16px"};l();c();var j=I(C());var Gt=({onClick:e,disabled:t})=>{let{t:o}=w(),d=q||G;return j.default.createElement(b,{topLeft:{text:o("addAccountHardwareWalletPrimaryText"),font:"bodyMedium"},bottomLeft:{text:o("addAccountHardwareWalletSecondaryText")},start:j.default.createElement(v,{backgroundColor:"borderPrimary",color:"textPrimary",icon:"WalletHardware",shape:"circle",size:32}),onClick:e,disabled:t||d})};l();c();var X=I(C());var eo=({onClick:e,disabled:t})=>{let{t:o}=w();return X.default.createElement(b,{topLeft:{text:o("addAccountImportSeedPhrasePrimaryText"),font:"bodyMedium"},bottomLeft:{text:o("addAccountImportSeedPhraseSecondaryText")},start:X.default.createElement(v,{backgroundColor:"borderPrimary",color:"textPrimary",icon:"File",shape:"circle",size:32}),onClick:e,disabled:t})};export{Ge as a,ge as b,_t as c,Ot as d,Gt as e,eo as f};
//# sourceMappingURL=chunk-5X2BHVFM.js.map
