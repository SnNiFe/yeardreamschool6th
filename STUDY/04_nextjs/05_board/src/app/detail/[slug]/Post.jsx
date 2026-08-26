'use client' // await async 사용 불가(Component, useEffect)
import {useEffect, useState} from "react";
import axios from "axios";
import Link from "next/link";
import './Post.css';

export default function Post({idx}){
    console.log(idx+'번 글 확인');

    const [post, setPost] = useState(null);

    const del = async function(){
        console.log(idx+' 번 글 삭제!!!');
        let {data} = await axios.get('http://localhost/delete/'+idx);
        console.log(data); // {success: true, idx: '40'}
        /*
        let msg = '이미 삭제 된 게시글 입니다.';
        if(data.success){
            msg = '삭제에 성공 했습니다.';
        }
        */
        let msg = data.success === true ? '삭제에 성공 했습니다.' : '이미 삭제 된 게시글 입니다.';
        alert(msg);
        location.href='/';
    }

    const makeHtml = function({post}){

        let content = <div>
            게시물이 존재하지 않습니다.
            <p><Link href="/">돌아가기</Link></p>
        </div>;

        if(post != null){
            content = <div>
                <div className="header">
                    <div>작성자 : {post.user_name}</div>
                    <div>조회수 : {post.bHit}</div>
                </div>
                <div className="title">제목 : {post.subject}</div>
                <hr/>
                <div>{post.content}</div>
                <hr/>
                <div className="btn_area">
                    <Link href="/">리스트</Link>
                    <button onClick={del}>삭제</button>
                </div>
            </div>;
        }

        setPost(content);

    }

    useEffect(function(){
        axios.get('http://localhost/detail/'+idx)
            .then(function({data}){
                console.log(data);
                makeHtml(data);
            });
    },[]);
    return(
        <div>{post}</div>
    );
}