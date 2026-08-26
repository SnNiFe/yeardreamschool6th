'use client'
import "@/app/common.css";
import {useState} from "react";
import Image from "next/image";
import axios from "axios";
import Link from "next/link";

export default function WritePage(){

    const [info, setInfo] = useState({subject:'', content:''});  // , user_name:''
    const id = window.sessionStorage.getItem("id");
    const token = window.sessionStorage.getItem('token');

    const [upload,setUpload] = useState([]); // 업로드 할 사진 저장소
    const [prev,setPrev] = useState([]); // 사진 미리보기

    const inputVal = function(e){
        // dict[key] = val
        setInfo({
            ...info,
            [e.target.name]: e.target.value
        });
        //console.log(info);
    };

    const fileSelect = function(e){
        //console.log(e);
        let file = e.target.files[0]; // 파일 정보를 추출
        setUpload([...upload,file]); // 업로드시킬 정보에 등록
        // 미리보기
        // 1. 파일을 읽을 리더 준비
        let reader = new FileReader();
        reader.readAsDataURL(file); // 2. 데이터를 base64 형식으로 읽어온다. (바이너리를 16진수 형태 문자로 읽음)
        reader.onloadend = function(e){ // 3. 파일을 다 읽었을 때...
            console.log(e); //e.target.result 를 Image 에 넣으면 된다.
            setPrev([...prev,<Image key={e.timeStamp} src={e.target.result} alt={file.name} width={100} height={100}/>]);
        };

    };

    // file upload 시 지켜야할 법칙
    // 1. POST 방식으로 보낼것
    // 2. enctype = multipart/form-data 지정할 것 (문자+바이너리+..)
    const save = async function(){

        let formData = new FormData();
        formData.append('user_name',id);
        formData.append('subject',info.subject);
        formData.append('content',info.content);

        // 올려둔 파일을 하나씩 추가
        for (const file of upload) {
            formData.append('files',file);
        }
        // post(url,param,option)
        let {data} = await axios.post('http://localhost/write',formData,{headers:{Authorization:token}});
        console.log(data);
        if(data.success === true){
            alert('글쓰기에 성공 하였습니다.');
            location.href = '/detail/'+data.idx;
        }else{
            alert('글쓰기에 실패 했습니다.');
        }
    };

    return(<>
        <h3>글 쓰 기</h3>
        <hr/>
        <table className={"form"}>
            <tbody>
                <tr>
                    <th>제목</th>
                    <td><input type={"text"} name={"subject"} onChange={inputVal} value={info.subject}/></td>
                </tr>
                <tr>
                    <th>작성자</th>
                    <td><input type={"text"} name={"user_name"} value={id} readOnly={true}/></td>
                </tr>
                <tr>
                    <th>내용</th>
                    <td>
                        <textarea name={"content"} onChange={inputVal} value={info.content}></textarea>
                    </td>
                </tr>
                <tr>
                    <th>사진</th>
                    <td>
                        <input type={"file"} name={"files"} onChange={fileSelect}/>
                        <div>{prev}</div>
                    </td>
                </tr>
                <tr>
                    <th colSpan={2}>
                        <button onClick={save}>저장</button>
                        <Link href="/list/1">리스트</Link>
                    </th>
                </tr>
            </tbody>
        </table>
    </>);

}