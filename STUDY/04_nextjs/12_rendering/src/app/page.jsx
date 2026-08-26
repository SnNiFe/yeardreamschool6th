'use client'
import PostComp from "@/app/PostComp";
import UserComp from "@/app/UserComp";
import {createContext, useState} from "react";

const PostContext = createContext({cnt:0,setCnt:()=>{}});
const UserContext = createContext({info:{id:'',pw:''},setInfo:()=>{}});

export default function App(){

    // state 의 원래 선언법
    const [cnt,setCnt] = useState(0);
    const [info,setInfo] = useState({id:'',pw:''});

    return (<>
        <PostContext.Provider value={{cnt:cnt,setCnt:setCnt}}>
            <PostComp/>
        </PostContext.Provider>
        <UserContext.Provider value={{info:info,setInfo:setInfo}}>
            <UserComp/>
        </UserContext.Provider>
    </>);
}

export {PostContext, UserContext}; // == {PostContext:PostContext}