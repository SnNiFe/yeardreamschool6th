// src/App.jsx
import React from "react";

function App() {
  const fruits = ["사과", "바나나", "오렌지"];

  /* 코드를 작성하세요. */
  return(
    <ul>
      {fruits.map((fruit,idx)=>{
        return <li key={idx}>{fruit}</li>;
      })}
    </ul>
  );
}

export default App;