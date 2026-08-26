import {useState} from "react";

export default function Input() {

    const [text,setText] = useState('');

    const getText = (e)=>{
        console.log(e.target.value);
        setText(e.target.value); // state 안에 값을 넣어줘야 UI에 적용
    }
    return(
        <div>
            <h3>입력 내용 : {text}</h3>
            <input id="inputStr" type="text"
                   placeholder="아무거나 입력 하세요"
                   value={text}
                   onChange={(e)=>{getText(e)}}
            />
        </div>
    );
}