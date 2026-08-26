import {useEffect, useState} from "react";
// lc 는 life cycle 의 줄임말 이다.
export default function Comp({cnt}){
    //console.log(cnt);
    const [num, setNum] = useState(cnt);
    /*
    useEffect(function(){
        console.log('렌더링 될 때마다 실행');
    });
    */
    /*
    useEffect(function(){
        // 생성자와 비슷
        console.log('컴포넌트가 최초 렌더링 할 때 실행');
    },[]);
    */

    // [] 안에 명시된 state 변화에만 동작
    // [a.b.c] : a 또는 b 또는 c 의 state 가 변화하면 동작
    useEffect(function(){
        console.log('num state 변경시에만 실행');
    },[num]);

    useEffect(function(){
        console.log('컴포넌트가 최초 렌더링 할 때 실행');
        return function(){
            console.log('컴포넌트 삭제될때 실행');
        }
    },[]);

    const incNum = () => {
        setNum(num+1);
    }
    const decNum = () => {
        setNum(num-1);
    }

    return(
        <div>
            <h1>Counter : {num}</h1>
            <button onClick={incNum}> + </button>
            <button onClick={decNum}> - </button>
        </div>
    );
}