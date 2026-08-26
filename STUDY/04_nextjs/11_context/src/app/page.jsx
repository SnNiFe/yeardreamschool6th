'use client'
import {createContext, useContext} from "react";

const DataContext = createContext(''); // 공용으로 사용할 저장소 생성
export default function App(){
    // 공용으로 사용할 값 저장
    return(<DataContext.Provider value={"공용으로 사용할 데이터"}>
            <First/>
            <Island/>
        </DataContext.Provider>
    );
}

const First = ()=>(<><div>First Component</div><Second/></>);

const Second = ()=>(<><div>Second Component</div><Third/></>);

const Island = ()=>{
    const data = useContext(DataContext);
    return (<div>Island Component / 도착지 : {data}</div>);
}

const Third = ()=>{
    const data = useContext(DataContext);
    return (<div>Third Component / 도착지 : {data}</div>);
}