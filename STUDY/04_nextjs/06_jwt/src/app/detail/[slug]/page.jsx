'use client'
import '@/app/common.css';
import {useEffect, useState} from "react";
import axios from "axios";
import Link from "next/link";

export default function DetailPage({params}){

    const [info,setInfo] = useState({}); // 글에대한 정보
    const [photos,setPhotos] = useState([]); // 사진들 정보

    const ip = 'http://localhost';

    useEffect(()=>{
        // slug 로 부터 받아온 idx 를 이용해 게시판글 가져오기
        params.then(({slug})=>{
            //console.log(slug); // == idx
            getDetail(slug);
        });
    },[]);

    const getDetail = async function(idx){
        let id = sessionStorage.getItem('id');
        let token = sessionStorage.getItem('token');
        // http://{server IP}/detail/{id}/{idx}
        let {data} = await axios.get(`${ip}/detail/${id}/${idx}`,{headers: {Authorization:token}});
        console.log(data);
        if(data.loginYN === false){
            alert('로그인이 필요한 서비스 입니다.');
            location.href='/';
        }
        setInfo(data.detail);

        let photoList = data.photos.map(photo=>
            <div key={photo.file_idx}>
                <p><img src={`${ip}/photo/${photo.file_idx}`} width={300} alt={photo.ori_filename}/></p>
                <a href={`${ip}/download/${photo.file_idx}`}>다운로드</a>
            </div>
        );
        setPhotos(photoList);
    };

    const del = async function(){
        let id = sessionStorage.getItem('id');
        let token = sessionStorage.getItem('token');
        // method : DELETE
        // {ip}/del/{id}/{idx}
        let {data} = await axios.delete(`${ip}/del/${id}/${info.idx}`,{headers: {Authorization:token}});
        console.log(data);
        alert('삭제되었습니다.');
        location.href='/list/1';
    };

    return(<>
        <h3>{info.idx} 상세보기</h3>
        <hr/>
        <table className={"form"}>
            <tbody>
            <tr>
                <th>제목</th>
                <td>{info.subject}</td>
            </tr>
            <tr>
                <th>조회수</th>
                <td>{info.bHit}</td>
            </tr>
            <tr>
                <th>작성자</th>
                <td>{info.user_name}</td>
            </tr>
            <tr>
                <th>내용</th>
                <td>{info.content}</td>
            </tr>
            <tr>
                <th>사진</th>
                <td>{photos}</td>
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