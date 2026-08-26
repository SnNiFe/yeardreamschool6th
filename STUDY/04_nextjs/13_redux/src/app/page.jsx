'use client'
import {store} from "@/redux/store";
import {useSelector} from "react-redux";

export default function App(){

    // action 을 통해 reducer 호출 -> dispatch
    const upHit = function(){
        store.dispatch({type:'counter/increment'});
    };

    const downHit = function(){
        store.dispatch({type:'counter/decrement'});
    };

    // 구독
    // useSelector : store 에 등록된 모든 slice 의 state 정보를 가져온다.
    let count = useSelector((state)=>{
        console.log(state);
        return state.counter.value;
    });

    return(<div>
        <h3>COUNT : {count}</h3>
        <button onClick={upHit}>증가</button>
        <button onClick={downHit}>감소</button>
    </div>);
}