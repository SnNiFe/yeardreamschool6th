'use client'
import Link from "next/link";
import "./Write.css";
import {useState} from "react";
import axios from "axios";

export default function Write(){

    const [info, setInfo] = useState({user_name:'',subject:'',content:''});

    // const onchange = function(e){
    //     setInfo(e.target.value);
    //     console.log(info);
    // };
    const inputVal = function(e){
        console.log(e.target.name,e.target.value);
        setInfo({
            ...info,
            [e.target.name]: e.target.value
        });
    }

    const save = async function(e){
        // axios.post(url,{params})
        // obj.data == {data}
        let {data} = await axios.post('http://localhost/write',info);
        console.log(data);
        if(data.success){
            alert('글쓰기에 성공 했습니다.');
            location.href='detail/'+data.idx;
        }else{
            alert('글쓰기에 실패 했습니다.');
        }
    }

    return(
        <div className="write">
            <div className="header">
                <input type="text" name="user_name" value={info.user_name} placeholder="작 성 자" onChange={inputVal}/>
            </div>
            <div className="title">
                <input type="text" name="subject" value={info.subject} placeholder="글 제 목" onChange={inputVal}/>
            </div>
            <div>
                <textarea name="content" value={info.content} onChange={inputVal}></textarea>
            </div>
            <div className="btn_area">
                <Link href="/">리스트</Link>
                <button onClick={save}>저 장</button>
            </div>
        </div>
    );
}