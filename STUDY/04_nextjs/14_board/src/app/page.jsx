'use client'
import "./common.css";
import {useEffect, useState} from "react";
import axios from "axios";
import {store} from "@/redux/store";

export default function LoginPage(){

    const [info, setInfo] = useState({id:'',pw:''});

    useEffect(()=>{
        sessionStorage.removeItem("id");
        sessionStorage.removeItem("token");
    },[]);

    const inputVal = function (e){
        setInfo({
            ...info,
            [e.target.name]: e.target.value
        });
    }

    const login = async function(){
        let {data} = await axios.post('http://localhost/login',info);
        console.log(data);
        if(data.success){
            // token 값 저장
            sessionStorage.setItem('id',info.id);
            sessionStorage.setItem('token',data.token);
            // debugger;
            location.href = '/list/1';
        }else{
            alert('아이디 또는 비밀번호를 확인해 주세요!');
        }
    }

    return(
        <div>
            <h3>로 그 인</h3>
            <hr/>
            <table>
                <tbody>
                    <tr>
                        <th>ID</th>
                        <td>
                            <input type="text" name="id" value={info.id} onChange={inputVal}/>
                        </td>
                    </tr>
                    <tr>
                        <th>PW</th>
                        <td>
                            <input type="password" name="pw" value={info.pw} onChange={inputVal}/>
                        </td>
                    </tr>
                    <tr>
                        <th colSpan={2}>
                            <button onClick={login}>로그인</button>
                        </th>
                    </tr>
                </tbody>
            </table>
        </div>
    );
}