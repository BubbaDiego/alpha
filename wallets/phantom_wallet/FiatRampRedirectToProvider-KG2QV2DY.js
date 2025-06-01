import{a as k,b as F}from"./chunk-2BA2A4Q2.js";import{C as b,c as v,l as e,m as s,r as h,v as w}from"./chunk-G7PMLIMH.js";import"./chunk-24ISZ5TA.js";import"./chunk-2J2WSGCG.js";import"./chunk-DHK5JDA3.js";import{m as f}from"./chunk-FI5JCZQR.js";import"./chunk-7XYHSLSH.js";import"./chunk-X6UT6LAC.js";import"./chunk-HTY4DAML.js";import{a as C}from"./chunk-6MAAUKN7.js";import{f as x,h as g,n as u}from"./chunk-3KENBVE7.js";g();u();var i=x(C()),S=()=>{let m=F(),{url:t,provider:o,sessionId:p,caip19:c}=m||{},[W,I]=(0,i.useState)(1),y=k(),{t:a}=f(),[T,P]=(0,i.useState)(!1),l=(0,i.useCallback)(()=>{let r=self.open(t,"_blank");r?(r.focus(),y.to("fiat-ramp-waiting-on-ramp",{params:{sessionId:p,caip19:c}})):P(!0)},[y,p,c,t]);return(0,i.useEffect)(()=>{let r=setInterval(()=>{I(d=>d<=0?(l(),clearInterval(r),d):d-1)},1e3);return()=>clearInterval(r)},[t,l]),!t||!o?null:i.default.createElement(e,{height:"100%",flex:1,justifyContent:"space-between",alignItems:"center",padding:24},i.default.createElement("style",null,`
          @keyframes opacity {
            0% {
              opacity: 1;
            }

            30% {
              opacity: 1;
            }
            50% {
              opacity: 0;
            }

            70% {
              opacity: 1;
            }

            100% {
              opacity: 1;
            }
          }   
          `),i.default.createElement(e,{justifyContent:"center",alignItems:"center",gap:16,style:{paddingTop:"120px"}},i.default.createElement(e,{direction:"row",alignItems:"center",gap:8,marginBottom:24},i.default.createElement(e,{width:72,height:72},i.default.createElement(w,{icon:"LogoFill",size:72,color:"textPrimary"})),i.default.createElement(e,{direction:"row",alignItems:"center",gap:6},i.default.createElement(n,{opacity:.5,animationDelay:"0s"}),i.default.createElement(n,{opacity:.8,animationDelay:"0.1s"}),i.default.createElement(n,{opacity:1,animationDelay:"0.2s"}),i.default.createElement(v.Link,{size:24,color:"accentPrimary"}),i.default.createElement(n,{opacity:1,animationDelay:"0.3s"}),i.default.createElement(n,{opacity:.8,animationDelay:"0.4s"}),i.default.createElement(n,{opacity:.5,animationDelay:"0.5s"})),i.default.createElement(e,{style:{animation:"animateRightLeft 2s ease-in-out infinite"},borderRadius:16,overflow:"hidden",backgroundColor:"bgWallet"},i.default.createElement(b,{src:o?.logo,width:72,height:72}))),i.default.createElement(e,{alignItems:"center",gap:8},i.default.createElement(s,{align:"center",font:"title1",color:"textPrimary",style:{wordBreak:"break-all"}},a("fiatRampTransferringToProvider",{provider:o?.name})),i.default.createElement(s,{font:"body",color:"textSecondary",align:"center"},a("fiatRampLeavingPhantomApp",{provider:o?.name})),T&&i.default.createElement(e,{padding:16,backgroundColor:"accentWarning",borderRadius:8},i.default.createElement(s,{font:"body",color:"bgWallet",align:"center"},a("fiatRampWindowOpenBlocked",{provider:o?.name}))))),i.default.createElement(e,{width:"100%"},i.default.createElement(h,{theme:"secondary",onClick:l},a("fiatRampOpen",{provider:o?.name}))))},n=({opacity:m,animationDelay:t})=>i.default.createElement(e,{width:4,height:4,borderRadius:4,backgroundColor:"accentPrimary",style:{opacity:m,animationDelay:t,animationName:"opacity",animationDuration:"1s",animationTimingFunction:"ease-in-out",animationIterationCount:"infinite"}});export{S as FiatRampRedirectToProvider};
//# sourceMappingURL=FiatRampRedirectToProvider-KG2QV2DY.js.map
