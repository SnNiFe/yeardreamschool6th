// src/Counter.js
import React, { useState } from 'react';

function Counter() {
  /* 코드를 작성하세요. */
  const [cnt, setCnt] = useState(0);

  return(<>
    <p>{cnt}</p>
    <button id="add" onClick={()=>setCnt(cnt+1)}>증가</button>
    <button id="dec" onClick={()=>setCnt(cnt-1)}>감소</button>
  </>);
}

export default Counter;