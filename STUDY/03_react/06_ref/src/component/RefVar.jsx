import {useRef, useState} from "react";

export default function RefVar(){

    const [val,setVal] = useState(0);
    const refVal = useRef(0);

    const updateState = ()=>{
        setVal(val+1);
    }

    const updateRef = ()=>{
        refVal.current += 1;
    }

    return (
        <div>
            <button onClick={updateState}>state count : {val}</button>
            <button onClick={updateRef}>ref count : {refVal.current}</button>
        </div>
    );
}