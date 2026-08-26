'use client'

import {useEffect, useState} from "react";
import axios from "axios";
import '@/app/common.css';
import Link from "next/link";
import Image from "next/image";
import {Pagination, Stack} from "@mui/material";

export default function ListPage({params}){
    // console.log(params);
    useEffect(() => {
        params.then(({slug})=>{
            console.log(slug);
            callList(slug);
        });
    }, []);

    let [list, setList] = useState([]);
    let [pages, setPages] = useState(1);

    const callList = async function(page){
        // 서버에 요청하기
        // http://localhost/{id}/{page}
        // header:{Authorization:{JWT토큰}}
        const id = sessionStorage.getItem('id');
        const token = sessionStorage.getItem('token');
        let {data} = await axios.get(`http://localhost/list/${id}/${page}`,
            {headers:{Authorization:token}});

        console.log(data);

        if(!data.loginYN){
            alert('로그인이 필요한 서비스 입니다.');
            location.href = '/';
        }

        setPages(data.pages);

        // idx, subject, user_name, bHit, cnt, reg_date, content
        let content = data.list.length === 0 ?
            <tr><th colSpan={6}>작성된 글이 없습니다.</th></tr>
            : data.list.map((item)=>(<tr key={item.idx}>
                <td>{item.idx}</td>
                <td>
                    {item.cnt === 0 ? <Image src="/noimage.png" width={25} height={25} alt={"이미지없음"}/>
                        :<Image src="/image.png" width={25} height={25} alt={"이미지있음"}/>}
                </td>
                <td>
                    <Link href={`/detail/${item.idx}`}>{item.subject}</Link>
                </td>
                <td>{item.user_name}</td>
                <td>{item.bHit}</td>
                <td>{item.reg_date}</td>
            </tr>));

            setList(content);

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
                    {list}
                    <tr>
                        <th colSpan={6}>
                            <div style={{justifyContent:'center', display:'flex'}}>
                                <Stack>
                                    <Pagination
                                        count={pages} // 전체 페이지 수
                                        color={'primary'} // 선택한 색
                                        variant={'outlined'}
                                        shape={'rounded'}
                                        siblingCount={2} // 중간정도 왔을때 양쪽에 표시할 개수
                                        onChange={function(evt,page){
                                            //console.log(evt,page);
                                            //location.href='/list/'+page;
                                            callList(page);
                                        }}
                                    />
                                </Stack>
                            </div>
                        </th>
                    </tr>
                </tbody>
            </table>
        </>
    );
}