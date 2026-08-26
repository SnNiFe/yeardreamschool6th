// Ref 를 이용해서 DOM 객체 가져오기

import {useRef, useState} from "react"; // react 로 부터 useState, useRef 를 불러온다.

export default function GetElem(){ // GetElem 함수를 기본(대표)으로 공개한다.

    const [input,setInput] = useState(''); // useState 사용, 기본값 : '', input(text) 과 setInput(setText) 을 선언(getter,setter)
    let inputRef = useRef(null);

    const Input = function(e){ // Input(chgText) 라는 함수는 이벤트객체(e) 를 매개변수로...
        // console.log(e.target.value);
        setInput(e.target.value); // 이벤트 당한 당사자(target) 의 값(value) 를 state 에 넣는다.
    }

    const inputFocus = ()=>{
        // ref 는 current 라는 속성에 값을 저장하고 있다.
        console.log([inputRef.current]);
        inputRef.current.focus();
    }

    // 반환(render 함수를 포함한다.)
    return(
        <div>
            {/*state 의 input(text) 을 적용 - 값이 변화되면 렌더링이 되면서 변화된 값이 보인다.*/}
            <h2>입력값 : {input}</h2>
            {/*onChange 이벤트가 일어나면 Input(chgText) 함수를 실행(e 객체는 기본으로 주어지기에 표시안해도 된다.)*/}
            {/*ref 는 해당 요소를 담을 변수에 대해 명시하는 속성*/}
            <input type={"text"} value={input} onChange={(e)=>{Input(e)}} ref={inputRef}/> {/*onChange={chgText}*/}
            <button onClick={inputFocus}>TAB</button>
        </div>
    );
}