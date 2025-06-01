import{a as tt}from"./chunk-G67D6P6H.js";import{a as ot,b as et,c as it}from"./chunk-2MTGVKD4.js";import{ia as nt}from"./chunk-6RSSZ6VM.js";import{b as R}from"./chunk-5LEHT7IY.js";import{a as L,b as E,j as Y}from"./chunk-5LRZ7IFN.js";import{Q,c as J,db as b,ka as X}from"./chunk-ATEHMOFB.js";import{a as Z,e as a}from"./chunk-2P7VAWV5.js";import{lb as q}from"./chunk-3HK6ZC5T.js";import{p as W}from"./chunk-U5F4RDP5.js";import{gb as y,ie as _}from"./chunk-XKUMOCJO.js";import{B as G,X as B,Y as K,l as U}from"./chunk-G7PMLIMH.js";import{m as C}from"./chunk-FI5JCZQR.js";import{Pa as z}from"./chunk-RISGBUNP.js";import{a as j}from"./chunk-6MAAUKN7.js";import{f as O,h as x,n as T}from"./chunk-3KENBVE7.js";x();T();var e=O(j());x();T();var i=O(j());var st=a.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  width: 100%;
  padding: ${t=>t.addScreenPadding?"16px":"0"};
`,Ct=a.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-grow: 1;
`,yt=a.div`
  width: 100%;
  > * {
    margin-top: 10px;
  }
  padding: 16px;
`,bt=a.div`
  display: flex;
  justify-content: flex-end;
  position: absolute;
  width: 100%;
  padding: 16px;
`,kt=a.div`
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
`,qt=a.div`
  position: relative;
`,Jt=a.div`
  position: absolute;
  top: 0;
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  svg {
    fill: #21e56f;
  }
`,ht=a(b).attrs({size:28,weight:500,color:"#FFFFFF"})`
  margin-top: 24px;
  margin-left: 12px;
  margin-right: 12px;
`,rt=a(b).attrs({size:16,weight:400,color:"#999999"})`
  margin-top: 9px;
  margin-left: 12px;
  margin-right: 12px;
  span {
    color: #999999;
    font-weight: bold;
  }
`,Bt=a(b).attrs({size:16,weight:500,color:"#AB9FF2"})`
  margin-top: 18px;
  text-decoration: none;
  ${t=>t.opacity!==0&&Z`
      &:hover {
        cursor: pointer;
        color: #e2dffe;
      }
    `}
`,Lt=({description:t,header:n,icon:o,onClose:s,title:p,txLink:m,isClosable:l,disclaimer:c})=>{let{t:r}=C(),d=()=>{m&&self.open(m)};return i.default.createElement(st,null,n,i.default.createElement(Ct,null,i.default.createElement(E,{mode:"wait",initial:!0},i.default.createElement(L.div,{key:p,initial:{opacity:0},animate:{opacity:1},exit:{opacity:0},transition:{duration:.2}},o)),i.default.createElement(ht,null,p),i.default.createElement(rt,null,t),m&&i.default.createElement(E,{mode:"wait",initial:!1},i.default.createElement(L.div,{key:m,initial:{opacity:0,y:16},animate:{opacity:1,y:0},exit:{opacity:0},transition:{duration:.2}},i.default.createElement(Bt,{opacity:1,onClick:d},r("swapTxConfirmationViewTransaction"))))),l&&s?i.default.createElement(yt,null,i.default.createElement(rt,null,c),l&&s?i.default.createElement(Y,{onClick:s},r("commandClose")):null):null)};var at=({ledgerAction:t,numberOfTransactions:n,cancel:o,ledgerApp:s})=>i.default.createElement(st,{addScreenPadding:!0},i.default.createElement(et,{ledgerAction:t,numberOfTransactions:n,cancel:o,ledgerApp:s}));var Et=t=>self.open(t,"_blank"),pt=({txErrorTitle:t,txErrorMessage:n,txErrorHelpButtonLink:o,txLink:s,onClose:p})=>i.default.createElement(Lt,{header:i.default.createElement(bt,null,i.default.createElement(kt,{onClick:()=>Et(o)},i.default.createElement(Q,{fill:"white"}))),icon:i.default.createElement(tt,{type:"failure"}),description:n,onClose:p,title:t,txLink:s,isClosable:!0});var At=t=>self.open(t,"_blank"),vt=()=>{let{handleHideModalVisibility:t}=nt(),n=J(),{popDetailView:o}=R(),{data:s}=_(),{data:[p]}=z(["enable-swapper-skip-review"]),l=s?.type==="ledger",c=p?"swapConfirmation":"swapReview",r=(0,e.useCallback)(()=>{t(c)},[t,c]),d=(0,e.useCallback)(()=>{o()},[o]),k=(0,e.useCallback)(()=>{r(),n("/notifications")},[r,n]);return q({isLedger:l,goToSwapTab:r,goToSwapReview:d,goToActivityTab:k})},Pt=({txError:t,txErrorTitle:n,txErrorMessage:o,txErrorHelpButtonLink:s,txLink:p,executeSwap:m,numberOfTransactions:l,addressType:c,onClose:r})=>ot(t)?e.default.createElement(it,{ledgerActionError:t,onRetryClick:m,onCancelClick:r}):t?e.default.createElement(pt,{txErrorTitle:n,txErrorMessage:o,txLink:p,onClose:r,txErrorHelpButtonLink:s}):e.default.createElement(at,{ledgerAction:m,numberOfTransactions:l,cancel:r,ledgerApp:W(c)}),Nt=e.default.memo(t=>{let n=(0,e.useRef)(null),{t:o}=C(),s=o("swapTxConfirmationViewTransaction"),{addressType:p,executeSwap:m,isLedger:l,isBridge:c,sellAsset:r,buyAsset:d,estimatedTime:k,isFailure:A,isSuccess:v,isClosable:mt,notEnoughSol:ct,numberOfTransactions:lt,txError:dt,txErrorTitle:P,txErrorMessage:N,txLink:h,txErrorHelpButtonLink:F,isReadyToExecute:ut,onClose:D,onSwapSuccess:ft}=t,[I,wt]=(0,e.useState)(!1),u,f,V,w,$=o("commandClose"),H,g,S=mt||!1;if((0,e.useEffect)(()=>{!g&&setTimeout(()=>{!I&&n.current?.start(),wt(!0)},200)},[I,g]),l&&!h&&ut)return e.default.createElement(Pt,{isBridge:c,txError:dt,txErrorTitle:P,txErrorMessage:N,txErrorHelpButtonLink:F,txLink:h,numberOfTransactions:lt,addressType:p,executeSwap:m,onClose:D});if(c&&r){let M=`${r.amount} ${r.symbol}`,gt=y.getNetworkName(r.networkID),St=`${d.amount} ${d.symbol}`,xt=y.getNetworkName(d.networkID);u=o("swapTxBridgeSubmitting"),f=o("swapTxBridgeSubmittingDescription",{sellAmount:M,sellNetwork:gt,buyAmount:St,buyNetwork:xt})}else f=`${d.symbol||o("swapTxConfirmationTokens")} ${o("swapTxConfirmationTokensWillBeDeposited")} `,u=o("swapTxConfirmationSwappingTokens");return ct&&(u=o("notEnoughSolPrimaryText"),f=o("notEnoughSolSecondaryText"),g=e.default.createElement(X,{width:B,height:B}),w={theme:"primary"},S=!0),v&&(c?(u=o("swapTxBridgeSubmitted"),f=o("swapTxBridgeSubmittedDescription",{estimatedTime:k}),V=o("swapTxBridgeSubmittedDisclaimer")):(u=o("swapTxConfirmationTokensDepositedTitle"),f=o("swapTxConfirmationTokensDepositedBody")),w={theme:"primary"},S=!0,n.current?.success()),A&&(u=P,f=N,w={theme:"secondary"},$=o("commandClose"),S=!0,H=e.default.createElement(U,{alignItems:"flex-end"},e.default.createElement(G,{icon:"HelpCircle",size:32,onClick:()=>At(F),backgroundColor:[null,"bgButton"],color:["textSecondary","textPrimary"],label:o("commandHelp")})),n.current?.fail()),e.default.createElement(K,{ref:n,title:u,txLink:h,txTitle:s,description:f,disclaimer:V,isClosable:S,buttonVariant:w,buttonText:$,onClose:v?ft:D,header:H,customIcon:g})}),Ft=()=>{let t=vt();return(0,e.useEffect)(()=>{!t.isReadyToExecute||t.isLedger||t.executeSwap()},[t.isReadyToExecute,t.isLedger]),e.default.createElement(Nt,{...t})},So=Ft;export{Ft as a,So as b};
//# sourceMappingURL=chunk-OSGFD7XJ.js.map
