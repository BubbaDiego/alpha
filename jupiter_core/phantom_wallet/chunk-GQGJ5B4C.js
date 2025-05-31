import{a as K}from"./chunk-C3YL4Q4B.js";import{a as _}from"./chunk-TEKKEVSO.js";import{a as W}from"./chunk-LSEYVCUG.js";import{b as H,c as U,f as G,i as O}from"./chunk-BMUB2YXP.js";import{b as D}from"./chunk-PUJ7YG5C.js";import{f}from"./chunk-5LEHT7IY.js";import{a as z}from"./chunk-3SURQQID.js";import{h as I,k as N}from"./chunk-5LRZ7IFN.js";import{db as n}from"./chunk-ATEHMOFB.js";import{e as i}from"./chunk-2P7VAWV5.js";import{b as L,o as F,x as M}from"./chunk-FGZHIQDN.js";import{x as B}from"./chunk-LLAFONE3.js";import{Cc as V,nd as E,rc as P}from"./chunk-4CMCOVQN.js";import{h as k}from"./chunk-T3HNWLEC.js";import{Db as h,H as v,He as w,I as A,L as So}from"./chunk-XKUMOCJO.js";import{m as p}from"./chunk-FI5JCZQR.js";import{c as y}from"./chunk-HTY4DAML.js";import{a as go}from"./chunk-6MAAUKN7.js";import{f as fo,h as b,n as T}from"./chunk-3KENBVE7.js";b();T();var o=fo(go());var xo=a=>{let{t}=p(),{voteAccountPubkey:s}=a,{showStakeAccountCreateAndDelegateStatusModal:Y,closeAllModals:j}=D(),J=()=>{a.onClose(),j()},{data:X}=w("solana"),{fungible:Z}=E({key:"SolanaNative"}),$=Z?.data.amount??"";B(X,"STAKE_FUNGIBLE");let{cluster:R,connection:u}=V(),r=M(u),oo=h("solana"),{data:to}=P({query:{data:oo}}),eo=to?.usd,e=(0,o.useMemo)(()=>r.results?.find(po=>po.voteAccountPubkey===s),[r.results,s]),no=e?.info?.name??e?.info?.keybaseUsername??k(s),io=H(u),[l,g]=(0,o.useState)(""),m=y(l),c=v(1+(G(u).data??0)),S=U({balance:$,cluster:R,rentExemptionMinimum:c}),ao=()=>g(S.toString()),ro=m.isLessThan(c),so=m.isGreaterThan(S),lo=m.isFinite(),d=l&&ro?t("validatorViewAmountSOLRequiredToStakeInterpolated",{amount:c}):l&&so?t("validatorViewInsufficientBalance"):"",mo=io.isPending,x=lo&&!d&&!mo,uo=()=>{Y({lamports:A(m).toNumber(),votePubkey:s,usdPerSol:eo,onClose:J,validatorName:no})},{data:C=null}=O(),co=C?F(C,e?.commission??0):null;return o.default.createElement(Co,null,r.isPending?o.default.createElement(I,null):r.isError||!e?o.default.createElement(o.default.Fragment,null,o.default.createElement(f,null,t("validatorViewPrimaryText")),o.default.createElement(q,null,o.default.createElement(n,{size:16,color:"#777777",lineHeight:20},t("validatorViewErrorFetching")," ",r.error?.message??""))):o.default.createElement(o.default.Fragment,null,o.default.createElement(f,null,t("validatorViewPrimaryText")),o.default.createElement(q,null,o.default.createElement(n,{size:16,color:"#777777",lineHeight:20,margin:"0 0 20px 0"},o.default.createElement(z,{i18nKey:"validatorViewDescriptionInterpolated"},"Choose how much SOL you\u2019d like to ",o.default.createElement("br",null),"stake with this validator. ",o.default.createElement(Q,{href:L},"Learn more"))),o.default.createElement(_,{value:l,symbol:"SOL",alignSymbol:"right",buttonText:t("maxInputMax"),width:47,warning:!!d,onSetTarget:ao,onUserInput:g}),o.default.createElement(To,null,o.default.createElement(n,{color:d?"#EB3742":"transparent",size:16,textAlign:"left"},d)),o.default.createElement(vo,{onEdit:a.onClose}),o.default.createElement(K,{identifier:e.voteAccountPubkey,name:e.info?.name,keybaseUsername:e.info?.keybaseUsername,iconUrl:e.info?.iconUrl,website:e.info?.website,data:[{label:t("validatorCardEstimatedApy"),value:o.default.createElement(n,{textAlign:"right",weight:500,size:14,noWrap:!0},co,"%")},{label:t("validatorCardCommission"),value:o.default.createElement(n,{textAlign:"right",weight:500,size:14,noWrap:!0},e.commission,"%")},{label:t("validatorCardTotalStake"),value:o.default.createElement(n,{textAlign:"right",weight:500,size:14,noWrap:!0},o.default.createElement(W,null,e.activatedStake))}]})),o.default.createElement(bo,null,o.default.createElement(N,{primaryText:t("validatorViewActionButtonStake"),secondaryText:t("commandClose"),onPrimaryClicked:uo,onSecondaryClicked:a.onClose,primaryTheme:x?"primary":"default",primaryDisabled:!x}))))},Ro=xo,Co=i.div`
  display: grid;
  grid-template-rows: 42px auto 47px;
  height: 100%;
`,q=i.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`,Q=i.a.attrs({target:"_blank",rel:"noopener noreferrer"})`
  color: #ab9ff2;
  text-decoration: none;
  cursor: pointer;
`,bo=i.section`
  display: flex;
  gap: 15px;
`,To=i.div`
  width: 100%;
`,yo=i(n)`
  width: 100%;
  margin-top: 15px;
  > a {
    color: #ab9ff2;
    cursor: pointer;
  }
`,vo=a=>{let{t}=p();return o.default.createElement(yo,{size:16,color:"#777777",lineHeight:20,textAlign:"left"},t("validatorViewValidator")," \u2022 ",o.default.createElement(Q,{onClick:a.onEdit},t("commandEdit")))};export{xo as a,Ro as b};
//# sourceMappingURL=chunk-GQGJ5B4C.js.map
