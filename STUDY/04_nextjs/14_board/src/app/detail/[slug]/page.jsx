'use client'
import '@/app/common.css';
import {useEffect, useState} from "react";
import axios from "axios";
import Link from "next/link";
import {useSelector} from "react-redux";
import {store} from "@/redux/store";
import PhotosComp from "@/app/detail/photosComp";

export default function DetailPage({params}){

    const ip = 'http://localhost';

    useEffect(()=>{
        // slug 로 부터 받아온 idx 를 이용해 게시판글 가져오기
        params.then(({slug})=>{
            //console.log(slug); // == idx
            getDetail(slug);
        });
    },[]);

    let board = useSelector(function(state){
        console.log(state.board);
        return state.board;
    });

    const getDetail = async function(idx){
        let {data} = await axios.get(`${ip}/detail/${board.id}/${idx}`,{headers: {Authorization:board.token}});
        console.log(data);
        if(data.loginYN === false){
            alert('로그인이 필요한 서비스 입니다.');
            location.href='/';
        }

        store.dispatch({
            type:'board/setDetail',
            payload:{info:data.detail,photos:data.photos}
        });

    };

    const del = async function(){

        let {data} = await axios.delete(`${ip}/del/${board.id}/${board.info.idx}`,
            {headers: {Authorization:board.token}});
        console.log(data);
        alert('삭제되었습니다.');
        location.href='/list/1';
    };

    return(<>
        <h3>{board.info.idx} 상세보기</h3>
        <hr/>
        <table className={"form"}>
            <tbody>
            <tr>
                <th>제목</th>
                <td>{board.info.subject}</td>
            </tr>
            <tr>
                <th>조회수</th>
                <td>{board.info.bHit}</td>
            </tr>
            <tr>
                <th>작성자</th>
                <td>{board.info.user_name}</td>
            </tr>
            <tr>
                <th>내용</th>
                <td>{board.info.content}</td>
            </tr>
            <tr>
                <th>사진</th>
                <td>
                    <PhotosComp photos={board.photos} ip={ip}/>
                </td>
            </tr>
            <tr>
                <th colSpan={2}>
                    <button onClick={del}>삭제</button>
                    <Link href="/list/1">리스트</Link>
                </th>
            </tr>
            </tbody>
        </table>
    </>);
}