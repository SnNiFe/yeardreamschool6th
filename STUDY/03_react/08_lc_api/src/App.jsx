import Comp from "./component/Comp.jsx";
import {useState} from "react";

export default function App(){

    const [comp, setComp] = useState(<Comp cnt={1}/>);

    return(
        <div>
            {comp}
            <button onClick={()=>{setComp(null)}}>
                component 삭제
            </button>
        </div>
    );
}