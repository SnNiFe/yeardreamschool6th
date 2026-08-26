"use client"
import {useEffect, useState} from "react";
import axios from "axios";
import Link from "next/link";
import './List.css';

export default function PostList({page}){ // props.page

    const [posts, setPosts] = useState([]);

    // useEffect 에는 await async 사용 안됨
    useEffect(function(){
        axios.get('http://localhost/list/'+page).then(({data})=>{
            console.log(data); // 데이터를 받아온 다음
            // html 태그로 만들어서 -> state 에 저장
            makeHtml(data);
        });
    },[]);

    const makeHtml = function ({list}){
        //console.log(list);
        let content = list.map(item=>(
            <div key={item.idx} className="post">
                <Link href={`/detail/${item.idx}`}>
                    <div className="title">
                        {item.idx} : {item.subject}
                        <span className="cnt">[{item.bHit}]</span>
                    </div>
                </Link>
                <div className="sub">{item.user_name}</div>
            </div>));
        setPosts(content);
    }

    return (
        <div>{posts}</div>
    );
}