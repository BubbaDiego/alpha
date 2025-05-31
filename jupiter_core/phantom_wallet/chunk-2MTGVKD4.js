import{c as O}from"./chunk-MQYVKNLB.js";import{a as k}from"./chunk-6ZOJTCTS.js";import{f as v}from"./chunk-5LEHT7IY.js";import{a as w}from"./chunk-DZ2NE3XW.js";import{b as N}from"./chunk-W27Z2YZM.js";import{h as B,j as M,k as F}from"./chunk-5LRZ7IFN.js";import{db as A,v as E}from"./chunk-ATEHMOFB.js";import{e as s}from"./chunk-2P7VAWV5.js";import{a as D,n as a}from"./chunk-U5F4RDP5.js";import{m as u}from"./chunk-FI5JCZQR.js";import{va as b}from"./chunk-RISGBUNP.js";import{c as h}from"./chunk-X6UT6LAC.js";import{R as P,la as S}from"./chunk-HTY4DAML.js";import{a as z}from"./chunk-6MAAUKN7.js";import{f as _,h as L,n as y}from"./chunk-3KENBVE7.js";L();y();var e=_(z());var G=s.div`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
  width: 100%;
`,U=s(k)`
  margin: auto 0px;
  padding-left: 10px;
  padding-right: 10px;
`,q=s.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`,K=s.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 55px;
`,p=s(A).attrs({size:28,lineHeight:34,weight:500})`
  margin-bottom: 8px;
  margin-top: 22px;
`,m=s(A).attrs({size:16,color:"#777"})`
  max-width: 275px;
  span {
    color: white;
  }
`,V={ledgerActionNeedToConfirm:"ledgerActionNeedToConfirm",ledgerActionNeedToConfirmMany:"ledgerActionNeedToConfirmMany",ledgerActionNeedToConfirmBlind:"ledgerActionNeedToConfirmBlind",ledgerActionNeedToConfirmBlindMany:"ledgerActionNeedToConfirmBlindMany",ledgerActionPleaseConnect:"ledgerActionPleaseConnect",ledgerActionConfirm:"ledgerActionConfirm",ledgerActionNeedPermission:"ledgerActionNeedPermission",ledgerActionPleaseConnectAndConfirm:"ledgerActionPleaseConnectAndConfirm",commandContinue:"commandContinue",commandCancel:"commandCancel"},ge=r=>!!(r&&(r.statusCode===26632||r.statusCode===27013||r.statusCode===27404||r.name==="DisconnectedDeviceDuringOperation")),H=r=>{switch(r){case"Bitcoin":return!1;case"EVM":return!0;case"Solana":return!0;case"Sui":return!1}},W=r=>{let{data:n=D}=O(!0,h());return(0,e.useMemo)(()=>({status:n.status,isConnected:n.isConnected,isExpectedSelectedAppOpen:n.isConnected&&n.selectedApp?.app===r,transport:n.isConnected?n.transport:void 0}),[r,n])},J=(r,n,o)=>{let{ledgerApp:t="Solana",ledgerAction:g,numberOfTransactions:c=1,cancel:f=S}=r,{t:i}=u(),l,d;c>1?H(t)?d=i(o.ledgerActionNeedToConfirmBlindMany,{numberOfTransactions:c,chainType:a(t)}):d=i(o.ledgerActionNeedToConfirmMany,{numberOfTransactions:c,chainType:a(t)}):H(t)?d=i(o.ledgerActionNeedToConfirmBlind,{chainType:a(t)}):d=i(o.ledgerActionNeedToConfirm,{chainType:a(t)});let T=i(o.commandCancel),C="default",x=f;switch(n.status){case"not-connected":{l=i(o.ledgerActionPleaseConnect);break}case"reconnecting":case"waiting-for-approval":case"connected":{l=i(o.ledgerActionConfirm);break}case"needs-permission":{l=i(o.ledgerActionNeedPermission),d=i(o.ledgerActionPleaseConnectAndConfirm),C="primary",T=i(o.commandContinue),x=()=>{N({url:"connect_hardware.html?permission=true"}),f()};break}}return(0,e.useEffect)(()=>{if(n.isConnected&&n.transport&&(n.isExpectedSelectedAppOpen===null||n.isExpectedSelectedAppOpen))try{g(n.transport)}catch(j){b.captureError(j,"ledger")}},[n]),{primaryText:l,secondaryText:d,buttonTheme:C,buttonText:T,buttonAction:x}},Q=e.default.memo(r=>{let{primaryText:n,secondaryText:o,buttonAction:t,buttonTheme:g,buttonText:c}=r;return e.default.createElement(G,null,e.default.createElement(U,{icon:e.default.createElement(B,{diameter:75}),primaryText:n,secondaryText:o}),e.default.createElement(M,{onClick:t,theme:g},c))}),X=r=>{let n=W(r.ledgerApp??"Solana"),o=J(r,n,V);return e.default.createElement(Q,{...o})},ue=r=>e.default.createElement(X,{...r}),Ae=({ledgerActionError:r,onRetryClick:n,onCancelClick:o})=>{let{t}=u();return e.default.createElement(q,null,e.default.createElement("div",null,e.default.createElement(v,null,t("ledgerActionErrorHeader")),e.default.createElement(K,null,e.default.createElement(w,{color:P("#EB3742",.1),diameter:94},e.default.createElement(E,{width:32})),r?.statusCode===26632?e.default.createElement(e.default.Fragment,null,e.default.createElement(p,null,t("ledgerActionErrorBlindSignDisabledPrimaryText")),e.default.createElement(m,null,t("ledgerActionErrorBlindSignDisabledSecondaryText"))):e.default.createElement(e.default.Fragment,null),r?.statusCode===27013?e.default.createElement(e.default.Fragment,null,e.default.createElement(p,null,t("ledgerActionErrorUserRejectionPrimaryText")),e.default.createElement(m,null,t("ledgerActionErrorUserRejectionSecondaryText"))):e.default.createElement(e.default.Fragment,null),r?.statusCode===27404?e.default.createElement(e.default.Fragment,null,e.default.createElement(p,null,t("ledgerActionErrorDeviceLockedPrimaryText")),e.default.createElement(m,null,t("ledgerActionErrorDeviceLockedSecondaryText"))):e.default.createElement(e.default.Fragment,null),r?.name==="DisconnectedDeviceDuringOperation"?e.default.createElement(e.default.Fragment,null,e.default.createElement(p,null,t("ledgerActionErrorDeviceDisconnectedDuringOperationPrimaryText")),e.default.createElement(m,null,t("ledgerActionErrorDeviceDisconnectedDuringOperationSecondaryText"))):e.default.createElement(e.default.Fragment,null))),e.default.createElement(F,{primaryText:t("commandRetry"),secondaryText:t("commandCancel"),onPrimaryClicked:n,onSecondaryClicked:o}))};export{ge as a,ue as b,Ae as c};
//# sourceMappingURL=chunk-2MTGVKD4.js.map
