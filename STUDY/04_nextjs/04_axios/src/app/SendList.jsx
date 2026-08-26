'use client'
import {useState} from "react";
import axios from "axios";
// useState 는 client 에서만 사용 가능
// Next.js 는 server 와 client 를 모두 다룬다.
// 그래서 컴포넌트 사용에 따라 어느포지션인지 명시해줘야 한다.

export default function SendList({url}) {
    console.log(url);
    let [list, setList] = useState([]);

    const send = async function(){
        let {data} = await axios.get(url);
        console.log(data);
        setList(data);
    };

    return (
        <div>
            <button onClick={send}>전송</button>
            <Post list={list}/>
        </div>
    );
}

function Post({list}){

    let posts = list.map(function(item,idx){
        return (<li key={item.id}>{item.title}</li>);
    });
    // 1. 데이터가 있고 없고를 어떻게 구분하는가?
    console.log(posts.length);
    // 2. 데이터가 없을때 어떻게 표시해 줄 것인가?
    if (posts.length === 0){
        //return (<ul><li>포스트 내용이 없습니다.</li></ul>); // 내가 한 거
        posts = <li>불러온 포스트가 없습니다.</li>;
    }
    // 3. 있을때는?
    return (<ul>{posts}</ul>);
}