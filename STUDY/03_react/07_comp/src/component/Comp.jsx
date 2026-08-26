import {useRef, useState} from "react";

export default function Comp(){

    const [count, setCount] = useState(0);
    let refVal = useRef(0);

    const updateCount = ()=>{
        setCount(count + 1); // state 는 render 함수와 관련이 있다.
        refVal.current += 1;
    }

    const alertCount = ()=>{
        // alert 이 아니라 setTimeout 과 render 함수와의 관계
        setTimeout(()=>{ // 비동기 상태
            // state : render 함수가 돌아간 값 : 3
            // ref : 현재 ref 객체를 저장

            // 초반에 가져온 값을 그대로 표시 : 3
            console.log('state',count);
            // 초반에 가져온 ref 객체에서 현재값(current) 을 물었다.
            console.log('ref',refVal.current);

            // (아님) alert 을 사용하면 render 함수도 차단된다.// 그래서 최신의 state 값을 받아 올 수가 없다.// render 함수가 실행되지 않는 상황에서는 state 의 최신값을 받을 수 없다.// alert(`3초 동안 ${count}번 클릭 하셨습니다.`);
            // alert(`3초 동안 ${refVal.current}번 클릭 하셨습니다.`);
        },3000);
    }

    return(
        <div>
            <h3>{count} 번 클릭!</h3>
            <button onClick={updateCount}>click me</button>
            <button onClick={alertCount}>show alert me</button>
        </div>
    );
}