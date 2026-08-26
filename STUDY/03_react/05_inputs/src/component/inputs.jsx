import {useState} from "react";

export default function Inputs(){

    /* 요소가 늘어날 때 마다 state를 추가해 줄 순 없다.
    const [id, setId] = useState('');
    const [nick, setNick] = useState('');
     */

    const [inputs, setInputs] = useState({nick:'',id:''});

    const typing = function(key,e){
        console.log(key,e.target.value);
        // inputs[key] = e.target.value;
        // ...inputs 를 통해 기존 오브젝트의 값을 확보(control) 후 무언가를 해라
        setInputs({
            ...inputs,
            [key]:e.target.value
        });
        // if (key === 'id'){
        //     setId(e.target.value);
        // }else if (key === 'nick'){
        //     setNick(e.target.value);
        // }
    }

    let {id, nick} = inputs; // 분해구조 할당

    const init = function(e){
        console.log(e); // 매개변수를 아무것도 안줘도 이벤트 객체는 무조건 받아 올 수 있다.
        setInputs({id:'',nick:''});
    }

    return(
        <div>
            아이디 : <input type={"text"} placeholder={"id"} value={id} onChange={(e)=>{typing('id',e)}}/><br/>
            닉네임 : <input type={"text"} placeholder={"nick"} value={nick} onChange={(e)=>{typing('nick',e)}}/><br/>
            {/* 매개변수가 없다면 아래처럼 사용도 가능 */}
            <button onClick={init}>초기화</button>
            <p>아이디 : {id}/ 닉네임 : {nick}</p>
        </div>
    );
}