import{a as P}from"./chunk-G67D6P6H.js";import{b as le}from"./chunk-B22LDNQT.js";import{a as at}from"./chunk-K4RIO6ZZ.js";import{b as it,c as dt,d as be}from"./chunk-MQYVKNLB.js";import{a as K}from"./chunk-6ZOJTCTS.js";import{a as se,c as st}from"./chunk-NJ4HEJET.js";import{a as De}from"./chunk-KPH7I3T4.js";import{l as nt,m as rt}from"./chunk-W27Z2YZM.js";import{i as ae,j as N}from"./chunk-5LRZ7IFN.js";import{db as G,ua as ct}from"./chunk-ATEHMOFB.js";import{e as s}from"./chunk-2P7VAWV5.js";import{a as Je}from"./chunk-3HK6ZC5T.js";import{a as et,l as tt,x as ce}from"./chunk-U5F4RDP5.js";import{b as Ce,h as Ze}from"./chunk-T3HNWLEC.js";import{Id as Qe,Jd as we,Kd as Re,Le as ot,Md as ye,_a as Xe,aa as $e,ba as Ke,ca as Ye,gb as M,xd as Se}from"./chunk-XKUMOCJO.js";import{c as Ge}from"./chunk-DHK5JDA3.js";import{m as v}from"./chunk-FI5JCZQR.js";import{Pa as Ve,Ra as qe}from"./chunk-RISGBUNP.js";import{D as je,e as ke,fa as ze,la as Ue}from"./chunk-HTY4DAML.js";import{a as ee}from"./chunk-6MAAUKN7.js";import{f as R,h as g,n as A}from"./chunk-3KENBVE7.js";g();A();var Ht={existingAccounts:{data:[],isFetched:!1,isError:!1},hardwareStepStack:[],hardwareStepSubStack:{},selectedChains:[],selectedChainsMap:new Map,chainImportStep:1,derivedAccountGroups:[],discoveredAccounts:[],activeAccountsFound:!1,selectedAccounts:{},onConnectHardwareAccounts:e=>Promise.resolve(),onConnectHardwareDone:()=>{}},I=ot((e,o)=>({...Ht,pushStep:t=>{let r=o().hardwareStepStack;e({hardwareStepStack:r.concat(t)})},popStep:()=>{let r=o().hardwareStepStack.length-1;if((o().hardwareStepSubStack[r]??[]).length)return e(Se(d=>{d.hardwareStepSubStack[r]=d.hardwareStepSubStack[r].slice(0,-1)}));e(Se(d=>{d.hardwareStepStack=d.hardwareStepStack.slice(0,-1)}))},pushSubStep:t=>{let c=o().hardwareStepStack.length-1,d=o().hardwareStepSubStack[c]??[];e(Se(S=>{S.hardwareStepSubStack[c]=d.concat([t])}))},currentStep:()=>{let t=o().hardwareStepStack,r=o().hardwareStepSubStack,c=t.length>0?t.length-1:t.length;return r[c]?.length?ke(r[c]):ke(t)},setExistingAccounts:t=>{e({existingAccounts:t})},setSelectedChains:(t,r)=>{e({selectedChains:t,selectedChainsMap:r})},setDecrementChainImportStep:()=>{let t=o().chainImportStep;e({chainImportStep:t-1})},setIncrementChainImportStep:()=>{let t=o().chainImportStep;e({chainImportStep:t+1})},setDerivedAccountGroups:t=>{e({derivedAccountGroups:t})},setDiscoveredAccounts:(t,r)=>{e({discoveredAccounts:t,activeAccountsFound:r})},selectAccount:t=>{let c={...o().selectedAccounts};c[t]=!0,e({selectedAccounts:c})},deselectAccount:t=>{let c={...o().selectedAccounts};delete c[t],e({selectedAccounts:c})},setSelectedAccounts:t=>{e({selectedAccounts:t})},setOnConnectHardwareAccounts:t=>{e({onConnectHardwareAccounts:t})},setOnConnectHardwareDone:t=>{e({onConnectHardwareDone:t})}}));g();A();g();A();g();A();var pt=s.main`
  width: ${420}px;
  min-height: ${480}px;
  position: relative;
  overflow: hidden;
  background-color: #222222;
  border: 1px solid #323232;
  border-radius: 16px;
  box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.4);
`;var ho=s(pt)`
  display: flex;
  flex-direction: column;
`,fo=s.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 100%;
  padding: 20px 20px;
`,Y=s.div`
  padding-top: 44px;
`,E=s.div`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex: 1;
  width: 100%;
  overflow: auto;
`;g();A();var H=R(ee());g();A();var a=R(ee());g();A();var k=R(ee());g();A();var F=R(ee());var xe=()=>{let{t:e}=v(),{discoveredAccounts:o,selectedAccounts:t,onConnectHardwareAccounts:r,onConnectHardwareDone:c}=I(),{mutateAsync:d}=Qe(),[S,C]=(0,F.useState)(!1),f=(0,F.useMemo)(()=>o.filter(n=>!!t[n.discoveryIdentifier]),[o,t]);return(0,F.useEffect)(()=>{if(f.length){let n=[],w=new Set;for(let p of f){let{accounts:y,seedIndex:T,accountIndex:x}=p,B=[],D=[];for(let m of y)$e(m.derivationPathType)?(D.push({pathType:m.derivationPathType,value:m.publicKey}),(!("amount"in m)||parseFloat(m.amount)!==0)&&w.add(m.chainType)):(Ke(m.derivationPathType)||Ye(m.derivationPathType))&&B.push({pathType:m.derivationPathType,value:m.address});n.push({derivationIndex:T,addresses:B,publicKeys:D,accountIndex:x})}r({accounts:n}).then(()=>{w.size>0&&d({addressTypes:Array.from(w)})}).finally(()=>C(!0))}else C(!0)},[f,r,d]),F.default.createElement(E,null,F.default.createElement(Y,null,F.default.createElement(K,{icon:F.default.createElement(P,{type:"success"}),primaryText:e("connectHardwareAccountsAddedInterpolated",{numOfAccounts:f.length}),headerStyle:"large",secondaryText:e("connectHardwareFinishSecondaryText")})),F.default.createElement(N,{onClick:c,theme:"primary",disabled:!S},e("pastParticipleDone")))};g();A();var L=R(ee());g();A();var h=R(ee());var Dt=(e,o,t)=>{switch(o){case"seed":return e("onboardingImportAccountsAccountName",{walletIndex:t});case"ledger":return e("onboardingImportAccountsLedgerAccountName",{walletIndex:t})}},Ot=({account:e})=>{let{t:o}=v();return h.default.createElement(Ft,null,h.default.createElement(Pt,null,h.default.createElement(se,{networkID:e.chain.id,size:40,borderColor:"bgRow"})),h.default.createElement(Bt,null,h.default.createElement(Nt,null,h.default.createElement(st,{networkID:e.chain.id,walletAddress:e.address},h.default.createElement(Te,null,e.chain.name)),h.default.createElement(Te,null,Ze(e.address,4))),h.default.createElement(ve,null,"amount"in e&&"chain"in e?h.default.createElement(ut,null,ze(e.amount)," ",e.chain.symbol):null,"amount"in e&&e.lastActivityTimestamp?h.default.createElement(ut,null,o("onboardingImportAccountsLastActive",{formattedTimestamp:je(e.lastActivityTimestamp*1e3,!0)})):null)))},mt=h.default.memo(({accountType:e,accounts:o,checked:t,accountIndex:r,onPress:c})=>{let{t:d}=v(),S=r+1;return h.default.createElement(lt,null,h.default.createElement(Mt,null,h.default.createElement(Te,null,Dt(d,e,S)),h.default.createElement(le,{checked:t,onChange:c,"data-testid":"account-select-address-row-checkbox"})),o.map((C,f)=>h.default.createElement(Ot,{key:`${C.address}-${f}`,account:C})))}),Wo=h.default.memo(({totalAccounts:e,selectedAccounts:o,onPress:t})=>{let{t:r}=v();return h.default.createElement(lt,null,h.default.createElement(Lt,null,h.default.createElement(Te,null,r("onboardingSelectAccountsNoOfAccountsSelected",{numOfAccounts:o}))," ",h.default.createElement(Et,null,r("onboardingSelectAccountSelectAllText")," ",h.default.createElement(le,{checked:o===e,onChange:t,"data-testid":"account-select-all-checkbox"}))))}),lt=s.div`
  margin-bottom: 24px;
  width: 100%;
`,Pt=s.div`
  flex-shrink: 0;
  margin-right: 10px;
`,Bt=s.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`,ve=s.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
`,Nt=s(ve)`
  margin-bottom: 2px;
`,Lt=s(ve)`
  background: #2a2a2a;
  margin-bottom: 1px;
  padding: 12px 10px 12px 14px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`,Et=s.div`
  display: flex;
  align-items: center;
  gap: 10px;
`,Mt=s(ve)`
  background: #2a2a2a;
  margin-bottom: 1px;
  padding: 12px 16px 12px 14px;
  border-top-left-radius: 6px;
  border-top-right-radius: 6px;

  & > span {
    margin-right: 0;
  }
`,Ft=s.div`
  background: #2a2a2a;
  margin-top: 1px;
  padding: 17px 16px 17px 14px;
  width: 100%;
  display: flex;
  align-items: center;

  &:last-of-type {
    border-bottom-left-radius: 6px;
    border-bottom-right-radius: 6px;
  }
`,Te=s(G).attrs({size:16,lineHeight:19,weight:600})``,ut=s(G).attrs({size:14,lineHeight:17,weight:400,color:"#777777"})``;var ht=({activeAccounts:e})=>{let{t:o}=v(),{selectedAccounts:t,selectAccount:r,deselectAccount:c,pushSubStep:d}=I(),S=(0,L.useMemo)(()=>Object.values(t).filter(n=>!!n).length===0,[t]),C=(0,L.useCallback)(()=>{d(L.default.createElement(xe,{preventBack:!0}))},[d]);return L.default.createElement(E,null,L.default.createElement("div",{style:{marginBottom:15}},L.default.createElement("div",{style:{display:"flex",flexDirection:"column",alignItems:"center",marginBottom:30}},L.default.createElement(G,{weight:500,size:30,lineHeight:34,maxWidth:"320px"},o("connectHardwareSelectAccounts")),L.default.createElement(Wt,{wordBreak:"break-word",size:18,lineHeight:22,color:"#777777"},o("connectHardwareChooseAccountsToConnect"))),L.default.createElement("div",{style:{maxHeight:420,overflowY:"scroll"}},e.map(({accounts:f,discoveryIdentifier:n,accountIndex:w})=>{let W=!!t[n];return L.default.createElement(mt,{key:n,accountType:"ledger",accounts:f,accountIndex:w,checked:W,onPress:()=>{W?c(n):r(n)}})}))),L.default.createElement(N,{onClick:C,theme:"primary",disabled:S},o("commandContinue")))},Wt=s(G)`
  margin-top: 15px;
`;var ft=()=>{let{t:e}=v(),{discoveredAccounts:o,activeAccountsFound:t,setSelectedAccounts:r,pushSubStep:c}=I(),d=(0,k.useMemo)(()=>{let f;if(t){let n=o.filter(w=>w.status==="undiscovered"||w.isSelectedByDefault);f=e(n.length===1?"connectHardwareFoundAccountsWithActivitySingular":"connectHardwareFoundAccountsWithActivity",{numOfAccounts:n.length})}else f=e("connectHardwareFoundSomeAccounts");return f},[t,e,o]),S=(0,k.useCallback)(()=>{c(k.default.createElement(ht,{activeAccounts:o}))},[c,o]),C=(0,k.useCallback)(()=>{c(k.default.createElement(xe,{preventBack:!0}))},[c]);return(0,k.useEffect)(()=>{let f=o.reduce((n,w,W)=>((w.status==="discovered"&&w.isSelectedByDefault||W===0)&&(n[w.discoveryIdentifier]=!0),n),{});r(f)},[o,r,t,e]),k.default.createElement(E,null,k.default.createElement(_t,null,k.default.createElement(K,{icon:k.default.createElement(P,{type:"success"}),primaryText:e("connectHardwareConnectAccounts"),headerStyle:"large",secondaryText:d})),k.default.createElement(Gt,{onClick:S,theme:"default"},e("connectHardwareSelectAccounts")),k.default.createElement(N,{onClick:C,theme:"primary"},e("commandContinue")))},_t=s(Y)`
  margin-bottom: 35px;
`,Gt=s(N)`
  margin-bottom: 10px;
`;var jt=19,zt=e=>{let o=new Set;for(let t of e)for(let{address:r}of t.addresses)o.add(r);return o},he=()=>{let{chainImportStep:e,setIncrementChainImportStep:o,selectedChains:t,selectedChainsMap:r,pushStep:c,pushSubStep:d,setDiscoveredAccounts:S,setDerivedAccountGroups:C}=I(),f=(0,a.useRef)(I.getState().derivedAccountGroups),{t:n,i18n:w}=v(),W=e-1,p=t[W],{data:y=[],isFetched:T,isError:x}=I(u=>u.existingAccounts),[B,D]=(0,a.useState)(!1),m=(0,a.useMemo)(()=>{let u=[],l=r.get(p)||{};for(let[_,Z]of Object.entries(l))Z&&u.push(_);return[u[0]]},[p,r]),{chainNameTextOr:j,chainNameTextAnd:X}=(0,a.useMemo)(()=>{let u=m.map(Z=>M.getChainName(ce.get(Z).ledgerAppOverride??Z)),l=new Intl.ListFormat(w.resolvedLanguage,{style:"long",type:"disjunction"}),_=new Intl.ListFormat(w.resolvedLanguage,{style:"long",type:"conjunction"});return{chainNameTextOr:l.format(u),chainNameTextAnd:_.format(u)}},[m,w]),te=(0,a.useMemo)(()=>m.map(u=>{let l=ce.get(u).ledgerAppOverride??u;return a.default.createElement(se,{key:M.getMainnetNetworkID(ce.get(l).ledgerAppOverride??l),networkID:l,size:72,borderColor:"bgWallet"})}),[m]);(0,a.useEffect)(()=>{let u=I.subscribe(l=>f.current=l.derivedAccountGroups);return()=>u()},[]);let $=(0,a.useMemo)(()=>{let u=[];switch(p){case"solana":{u.push({pathType:"bip44Root"});break}case"eip155":{u.push({pathType:"bip44RootEthereum"});break}case"bip122_p2tr":case"bip122_p2wpkh":case"bip122_p2sh":case"bip122_p2pkh":case"sui":break}for(let l=0;l<jt;++l)switch(p){case"solana":{u.push({index:l,pathType:"bip44Change"}),u.push({index:l,pathType:"bip44"});break}case"eip155":{u.push({index:l,pathType:"bip44Ethereum"}),u.push({index:l,pathType:"bip44EthereumSecondary"});break}case"bip122_p2tr":case"bip122_p2wpkh":case"bip122_p2sh":case"bip122_p2pkh":{u.push({index:l,pathType:"bitcoinTaproot"},{index:l,pathType:"bitcoinNativeSegwit"});break}case"sui":throw new Xe("connect hardware")}return u},[p]),[ie,de]=(0,a.useState)(!0),{data:oe=et}=dt(ie,!0),{data:[He]}=Ve(["kill-ledger-xpub-derivation"]),{data:J,error:Be,fetchStatus:At,refetch:Ne}=it(oe,$,!0,!He),Ct=At==="fetching",Ie=!oe.isConnected&&oe.status!=="reconnecting",[St,wt]=(0,a.useState)(!1),{data:fe,refetch:Le}=be(St,!0);(0,a.useEffect)(()=>{Ie&&de(!1)},[Ie]),(0,a.useEffect)(()=>{fe?.type==="granted"&&(de(!0),wt(!1))},[fe]);let Ee=Re(),Me=(0,a.useCallback)(async()=>{if(J&&Object.keys(J).length){let u=[...f.current],l=0;for(let _ of Object.values(J)){let pe={accounts:{...(u[l]??{accounts:{}}).accounts},derivationIndex:$[l].index},ge=M.getChainIDs(_.addressType).filter(Ae=>Ee.includes(Ae));for(let Ae of ge){let ue=M.getNetworkIDs(Ae);for(let re of ue)m.includes(re)&&(pe.accounts[`${re}-${_.address}`]={chainType:_.addressType,chainId:re,address:_.address,publicKey:_.publicKey,pathParams:$[l]})}u[l]=pe,l++}if(C(u),T&&t.length===e){D(!0);let _=zt(y),Z=u.reduce((i,O)=>{let me=!1;for(let{address:We}of Object.values(O.accounts))me=me||_.has(We);return me||i.push(O),i},[]),pe=[],ge=[];for(let i=0;i<Z.length;i+=De.extension){let O=Z.slice(i,i+De.extension).map(me=>Object.entries(me.accounts).reduce((_e,[Tt,vt])=>(_e[Tt]={account:vt},_e),{}));ge.push(O)}for(let i of ge)pe.push(Je(i));let ue=(await Promise.all(pe)).flat().map(i=>{switch(i.status){case"discovered":return{...i,accounts:i.accounts.filter(O=>O.hasAccountActivity||Ce(O.derivationPathType))};case"undiscovered":return{...i,accounts:i.accounts.filter(O=>Ce(O.derivationPathType))}}}).filter(i=>i.accounts.length>0).map(i=>{let O=Ge();return{...i,discoveryIdentifier:O}}),re=ue.filter(i=>i.status==="undiscovered"||i.isSelectedByDefault),yt=ue.filter(i=>!(i.status==="undiscovered"||i.isSelectedByDefault)).slice(0,2),Fe=re.length>0,bt=y.filter(i=>i.type==="ledger").length,xt=(Fe?[...re,...yt]:ue.filter(i=>!i.accounts.some(O=>!Ce(O.derivationPathType))).slice(0,3)).map((i,O)=>({...i,accountIndex:bt+O}));S(xt,Fe),c(a.default.createElement(ft,{preventBack:!0}))}}},[J,C,T,t.length,e,$,Ee,m,y,S,c]);(0,a.useEffect)(()=>{J&&Object.keys(J).length===$.length&&(Me(),t.length!==e&&(o(),d(a.default.createElement(he,{preventBack:!0}))))},[J,$,c,d,e,t,Me,o]);let z,U,V,Q,ne=()=>{};return x?(z=a.default.createElement(P,{type:"failure"}),U=n("connectHardwareErrorLedgerGeneric"),V=n("connectHardwareErrorLedgerPhantomLocked"),ne=async()=>{let u=await nt();u.id!==void 0&&rt(u.id)},Q=n("commandClose")):fe&&fe.type!=="granted"?(z=a.default.createElement(P,{type:"warning"}),U=n("connectHardwarePermissionDeniedPrimary"),V=n("connectHardwarePermissionDeniedSecondary"),Q=n("homeErrorButtonText"),ne=Le):Ie?(z=a.default.createElement(P,{type:"warning"}),U=n("connectHardwarePermissionUnableToConnect"),V=n("connectHardwarePermissionUnableToConnectDescription"),Q=n("commandConnect"),ne=Le):Be instanceof tt?(z=a.default.createElement(P,{type:"failure"}),U=n("connectHardwareErrorLedgerLocked"),V=n("connectHardwareErrorLedgerLockedDescription"),Q=n("homeErrorButtonText"),ne=Ne):Be?(z=a.default.createElement(P,{type:"failure"}),U=n("connectHardwareErrorLedgerGeneric"),V=n("connectHardwareErrorLedgerGenericDescription"),Q=n("homeErrorButtonText"),ne=Ne):oe.status=="reconnecting"?(z=a.default.createElement(P,{defaultIcon:a.default.createElement(ae,null),type:"default"}),U=n("connectHardwareConnecting"),V=n("connectHardwareConnectingDescription")):B?(z=a.default.createElement(P,{defaultIcon:a.default.createElement(ae,null),type:"default"}),U=n("connectHardwareDiscoveringAccounts"),V=n("connectHardwareDiscoveringAccountsDescription")):Ct?(z=a.default.createElement(P,{defaultIcon:a.default.createElement(ae,null),type:"default"}),U=n("connectHardwareConnectingAccounts"),V=n("connectHardwareFindingAccountsWithActivity",{chainName:X})):(z=a.default.createElement(Vt,null,te),U=n("connectHardwareMobileOpenAppSingleChain",{chainName:j}),V=n("connectHardwareOpenAppDescription")),a.default.createElement(E,null,a.default.createElement(Y,null,a.default.createElement(K,{icon:z,primaryText:U,headerStyle:"large",secondaryText:V})),Q?a.default.createElement(N,{onClick:ne,theme:"primary"},Q):a.default.createElement(Ut,null,a.default.createElement(G,{color:"#999999",size:14},n("connectHardwareAccountsStepOfSteps",{stepNum:e,totalSteps:t.length}))))},Ut=s.div`
  align-self: center;
  background-color: rgba(255, 255, 255, 0.03);
  border-radius: 80px;
  padding: 8px 16px;
  max-width: 150px;
`,Vt=s.div`
  display: flex;
  align-items: center;

  & > *:not(:last-child) {
    margin-right: -12.5px;
  }
`;g();A();var b=R(ee());var gt=()=>{let{t:e}=v(),{pushSubStep:o,selectedChains:t,setSelectedChains:r,selectedChainsMap:c}=I(),d=ye(),S=(0,b.useMemo)(()=>d.filter(p=>ce.get(p).isLedgerEnabled),[d]),C=we(),f=(0,b.useCallback)(p=>{let y=new Map(c),T=M.getAddressTypes(p);for(let B of T){let D=c.get(B),m=D?.[p];y.set(B,{...D,[p]:!m})}let x=C.filter(B=>{let D=y.get(B)||{};return Object.values(D).reduce((j,X)=>X?++j:j,0)>0});r(x,y)},[C,r,c]),n=()=>{o(b.default.createElement(he,{preventBack:!0}))};at(()=>{let p=new Map;for(let y of C)p.set(y,{});for(let y of S){let T=M.getAddressTypes(y);for(let x of T){let B=p.get(x);p.set(x,{...B,[y]:!1})}}r(t,p)},C.length>0&&S.length>0);let w=(0,b.useMemo)(()=>S.map(p=>{let y=M.getAddressTypes(p),T=!1;for(let x of y)T=c.get(x)?.[p]||T;return b.default.createElement(qt,{key:p,icon:b.default.createElement(se,{networkID:p,size:40}),networkID:p,onPressChain:f,isChecked:T})}),[S,c,f]),W=(0,b.useMemo)(()=>{let p=0;for(let y of c.values())p+=Object.values(y).reduce((T,x)=>x?++T:T,0);return p===0},[c]);return b.default.createElement(E,null,b.default.createElement(G,{weight:500,size:28,lineHeight:34},e("connectHardwareSelectChains")),b.default.createElement(Yt,null,w),b.default.createElement(N,{onClick:n,theme:"primary",disabled:W},e("commandContinue")))},qt=({networkID:e,icon:o,onPressChain:t,isChecked:r})=>b.default.createElement($t,{onClick:()=>{t(e)}},b.default.createElement(Xt,null,b.default.createElement(Kt,null,o),b.default.createElement(G,{size:16,weight:600},M.getNetworkName(e))),b.default.createElement(le,{checked:r})),$t=s.div`
  align-items: center;
  background-color: #2a2a2a;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 16px 24px 16px 12px;

  :last-child {
    margin-bottom: 28px;
  }

  > span {
    margin-right: 0px;
  }
`,Kt=s.div`
  margin-right: 12px;
`,Yt=s.div`
  margin-top: 20px;
`,Xt=s.div`
  display: flex;
  align-items: center;
`;var Zt=()=>{qe();let{t:e}=v(),{pushStep:o,setSelectedChains:t}=I(),r=ye(),c=we(),{data:d,isFetching:S,refetch:C}=be(!0,!0),{buttonDisabled:f,defaultIcon:n,primaryText:w,secondaryText:W,buttonText:p,iconType:y,onClick:T}=(0,H.useMemo)(()=>{let x=!1,B=H.default.createElement(ae,null),D,m,j,X="default",te=Ue;if(S)D=e("connectHardwareSearching"),m=e("connectHardwareMakeSureConnected"),j=e("commandContinue"),x=!0;else if(d?.type==="granted"){let $=d.transport.deviceModel?.productName??"Ledger";X="success",D=e("connectHardwarePairSuccessPrimary",{productName:$}),m=e("connectHardwarePairSuccessSecondary",{productName:$}),j=e("commandContinue"),x=!1,te=()=>{if(c.length===1){let ie=new Map;ie.set(c[0],{});for(let de of r){let oe=M.getAddressTypes(de);for(let He of oe)ie.set(He,{[de]:!0})}t(c,ie),o(H.default.createElement(he,{preventBack:!0}))}else o(H.default.createElement(gt,{onBackCallback:()=>{t([],new Map)}}))}}else d?.type==="denied"?(X="failure",D=e("connectHardwarePermissionDeniedPrimary"),m=e("connectHardwarePermissionDeniedSecondary"),j=e("commandTryAgain"),x=!1,te=C):(!d||d.type==="unable-to-connect")&&(X="failure",D=e("connectHardwarePermissionUnableToConnect"),m=e("connectHardwareWaitingForApplicationSecondaryText"),j=e("commandTryAgain"),x=!1,te=C);return{buttonDisabled:x,defaultIcon:B,primaryText:D,secondaryText:m,buttonText:j,iconType:X,onClick:te}},[r,c,d,o,C,S,t,e]);return H.default.createElement(E,null,H.default.createElement(Y,null,H.default.createElement(K,{icon:H.default.createElement(P,{defaultIcon:n,type:y}),primaryText:w,headerStyle:"large",secondaryText:W})),H.default.createElement(N,{onClick:T,theme:"primary",disabled:f},p))},Ar=()=>{let{t:e}=v(),{pushSubStep:o}=I(),t=()=>o(H.default.createElement(Zt,null));return H.default.createElement(E,null,H.default.createElement(Y,null,H.default.createElement(K,{icon:H.default.createElement(ct,null),primaryText:e("connectHardwareLedger"),headerStyle:"large",secondaryText:e("connectHardwareStartConnection"),animateText:!0})),H.default.createElement(N,{onClick:t,theme:"primary"},e("commandConnect")))};export{I as a,pt as b,ho as c,fo as d,mt as e,Wo as f,Ar as g};
//# sourceMappingURL=chunk-DOOHBDKQ.js.map
