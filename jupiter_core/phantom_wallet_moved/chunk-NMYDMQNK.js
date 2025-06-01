import{a as g}from"./chunk-FS5WEDFF.js";import{a as u,b as m,e as x}from"./chunk-V4KRVOHD.js";import{db as f}from"./chunk-ATEHMOFB.js";import{a as d,e}from"./chunk-2P7VAWV5.js";import{m as s}from"./chunk-G7PMLIMH.js";import{a as w}from"./chunk-6MAAUKN7.js";import{f as R,h as a,n as p}from"./chunk-3KENBVE7.js";a();p();var t=R(w());var I=e.div`
  display: flex;
  height: 49px;
  padding: 0 16px;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  &:last-of-type {
    margin-bottom: 0;
  }
  background-color: ${o=>o.customBackground??"#2a2a2a"};
  ${o=>o.onClick?d`
          :hover {
            background-color: #333333;
          }
          cursor: pointer;
        `:""}
`,y=e.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`,v=e.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`,L=e.div`
  display: flex;
  margin: 2px 4px 0 0;
`,P=e(f).attrs(o=>({color:o.color||"#777",size:14,lineHeight:17,weight:400,noWrap:!0,paddingLeft:8}))`
  cursor: ${o=>o.onClick?"pointer":"default"};
  text-decoration: none;
`,A=({children:o,icon:n,fontWeight:r,label:b,lineHeight:h,customBackground:k,color:T,tooltipContent:i,isLoading:l=!1,error:c,onClick:C})=>t.default.createElement(I,{customBackground:k,onClick:l?void 0:C},t.default.createElement(v,null,t.default.createElement(y,null,n?t.default.createElement(L,null,n):null,t.default.createElement(x,{tooltipAlignment:"topLeft",iconSize:12,lineHeight:h??17,fontWeight:r??400,info:i?t.default.createElement(W,{tooltipContent:i}):null,textColor:T||"#FFF"},b)),c?t.default.createElement(s,{color:"accentAlert",font:"label",children:c}):null),l?t.default.createElement(g,{width:"75px",height:"15px",borderRadius:"50px",backgroundColor:"#434343"}):o),W=({tooltipContent:o})=>t.default.createElement(m,null,typeof o=="string"?t.default.createElement(u,null,o):o),S=({children:o,color:n,onClick:r})=>t.default.createElement(P,{onClick:r,color:n||"#777"},o||"-");export{A as a,W as b,S as c};
//# sourceMappingURL=chunk-NMYDMQNK.js.map
