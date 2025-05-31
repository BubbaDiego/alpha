import{a as T,b as E}from"./chunk-LAM77KQX.js";import{a as S}from"./chunk-IUNHH544.js";import{a as C}from"./chunk-NJHVGQ3T.js";import"./chunk-JOYNNZVI.js";import{a as g}from"./chunk-C5UDUURS.js";import{f as P}from"./chunk-5LEHT7IY.js";import"./chunk-NGO5FOJW.js";import"./chunk-2LU4YM7A.js";import"./chunk-E6VR42GU.js";import{j as c}from"./chunk-5LRZ7IFN.js";import{db as h}from"./chunk-ATEHMOFB.js";import{e as t}from"./chunk-2P7VAWV5.js";import"./chunk-O3DDAITN.js";import"./chunk-WFPABEAU.js";import{k as b}from"./chunk-T3HNWLEC.js";import"./chunk-XKUMOCJO.js";import"./chunk-EF7ER3CO.js";import{m as x}from"./chunk-G7PMLIMH.js";import"./chunk-24ISZ5TA.js";import"./chunk-2J2WSGCG.js";import"./chunk-DHK5JDA3.js";import{m as A}from"./chunk-FI5JCZQR.js";import"./chunk-7XYHSLSH.js";import"./chunk-RISGBUNP.js";import"./chunk-X6UT6LAC.js";import"./chunk-HTY4DAML.js";import{a as y}from"./chunk-6MAAUKN7.js";import"./chunk-LYAMJYNC.js";import"./chunk-UNDMYLJW.js";import{f as u,h as m,n as l}from"./chunk-3KENBVE7.js";m();l();var w=u(E()),o=u(y());m();l();var p=u(y());var I=t(c).attrs({borderRadius:"100px",theme:"primary",width:"auto",fontSize:14,fontWeight:600})`
  flex-shrink: 0;
  padding: 5px 12px;
`,k=p.default.memo(s=>{let{copyText:e,className:d}=s,{buttonText:r,copy:n}=T(e),f=(0,p.useCallback)(a=>{a.stopPropagation(),n()},[n]);return p.default.createElement(I,{className:d,onClick:f},r)});var v=t(g).attrs({align:"center",justify:"space-between"})`
  height: 100%;
`,B=t(w.default)`
  padding: 8px;
  background: #ffffff;
  border-radius: 6px;
`,D=t(C).attrs({align:"center",justify:"space-between"})`
  padding: 12px 15px;
  background: #181818;
  border: 1px solid #2f2f2f;
  border-radius: 6px;
  box-shadow: inset 0px 0px 4px rgba(0, 0, 0, 0.25);
`,F=t(g).attrs({align:"center"})`
  ${D} {
    margin-top: 32px;
    margin-bottom: 11px;
  }
`,z=t(C)`
  p:first-child {
    margin-right: 6px;
  }
`,H=s=>{let{accountName:e,walletAddress:d,address:r,symbol:n,onClose:f}=s,a=n||(r?b(r):void 0),{t:i}=A();return{i18nStrings:(0,o.useMemo)(()=>({depositAssetInterpolated:i("depositAssetDepositInterpolated",{tokenSymbol:a}),secondaryText:i("depositAssetSecondaryText"),transferFromExchange:i("depositAssetTransferFromExchange"),depositAssetShareAddressError1:i("sendInvalidQRCodeLoadingError1"),depositAssetShareAddressError2:i("sendInvalidQRCodeLoadingError2"),close:i("commandClose")}),[i,a]),accountName:e,walletAddress:d,onClose:f}},M=o.default.memo(s=>{let{i18nStrings:e,accountName:d,walletAddress:r,onClose:n}=s;return o.default.createElement(v,null,o.default.createElement(P,null,e.depositAssetInterpolated),o.default.createElement(F,null,r?o.default.createElement(o.default.Fragment,null,o.default.createElement(B,{value:r,size:160}),o.default.createElement(D,null,o.default.createElement(z,null,o.default.createElement(S,{name:d,publicKey:r})),o.default.createElement(k,{copyText:r})),o.default.createElement(h,{size:14,color:"#777777",lineHeight:20},e.secondaryText)):o.default.createElement(o.default.Fragment,null,o.default.createElement(x,{align:"center",font:"labelSemibold",children:e.depositAssetShareAddressError1}),o.default.createElement(x,{align:"center",font:"body",children:e.depositAssetShareAddressError2}))),o.default.createElement(g,null,o.default.createElement(c,{onClick:n},e.close)))}),Q=o.default.memo(s=>{let e=H(s);return o.default.createElement(M,{...e})}),ro=Q;export{Q as DepositAddressPage,ro as default};
//# sourceMappingURL=DepositAddressPage-XVRKUXBZ.js.map
