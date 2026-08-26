'use client'

import {useEffect, useState} from "react";
import axios from "axios";
import '@/app/common.css';
import Link from "next/link";
import Image from "next/image";
import {Pagination, Stack} from "@mui/material";
import {store} from "@/redux/store";
import {useSelector} from "react-redux";
import ListComp from "@/app/list/[slug]/ListComp";

export default function ListPage({params}){
    // console.log(params);
    useEffect(() => {
        params.then(({slug})=>{
            console.log(slug);
            callList(slug);
        });
    }, []);

    let board = useSelector(function(state){
        console.log(state.board);
        return state.board;
    });

    const callList = async function(page){

        let {data} = await axios.get(`http://localhost/list/${board.id}/${page}`,
            {headers:{Authorization:board.token}});
        console.log(data);

        if(!data.loginYN){
            alert('로그인이 필요한 서비스 입니다.');
            location.href = '/';
        }

        // list. pages
        store.dispatch({
            type:'board/setList',
            payload:{list:data.list,pages:data.pages}
        });
    };

    return(
        <>
            <Link href="/write">글쓰기</Link>
            <table className={"list"}>
                <thead>
                    <tr>
                        <th>번호</th>
                        <th>이미지</th>
                        <th>제목</th>
                        <th>작성자</th>
                        <th>조회수</th>
                        <th>작성일</th>
                    </tr>
                </thead>
                <tbody>
                    <ListComp board={board} onSubmit={callList}/>
                </tbody>
            </table>
        </>
    );
}