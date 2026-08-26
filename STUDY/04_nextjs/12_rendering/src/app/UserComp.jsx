'use client'
import {UserContext} from "@/app/page";
import {useContext, useMemo} from "react";

export default function UserComp() {

    // 분해구조할당
    const {info,setInfo} = useContext(UserContext);

    const inputVal = function(e){
        setInfo({
            ...info,
            [e.target.name]:e.target.value
        });
    };

    // let html = <div>
    //     <p>ID: <input type="text" value={info.id} name="id"
    //                   onChange={inputVal}/></p>
    //     <p>PW:<input type="text" value={info.pw} name="pw"
    //                  onChange={inputVal}/></p>
    // </div>;
    // console.log('user component rendering...');

    let html = useMemo(function(){
        console.log('user component rendering...');
        return (<div>
            <p>ID: <input type="text" value={info.id} name="id"
                          onChange={inputVal}/></p>
            <p>PW:<input type="text" value={info.pw} name="pw"
                         onChange={inputVal}/></p>
        </div>);
    },[info]);

    return (<>{html}</>);
}