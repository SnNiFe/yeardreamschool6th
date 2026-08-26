'use client'
import {useContext, useMemo} from "react";
import {PostContext} from "@/app/page";

export default function PostComp() {

    const {cnt,setCnt} = useContext(PostContext);

    //  let html = <div>
    //     <h3>Post 에 대한 조회수 : {cnt}</h3>
    //     <button onClick={()=>setCnt(cnt+1)}>좋아요!</button>
    // </div>;
    // console.log('post component rendering...');

    let html = useMemo(function(){
        console.log('post component rendering...');
        return (<div>
            <h3>Post 에 대한 조회수 : {cnt}</h3>
            <button onClick={()=>setCnt(cnt+1)}>좋아요!</button>
        </div>);
    },[cnt]);

    return (<>{html}</>);
}