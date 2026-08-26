import {useEffect} from 'react'
export  default function DomOne(){
    useEffect(() => {
        const title = document.getElementById('title');
        // console.log(title.textContent);
    })

    return(
        <><h1 id='title'>DOM 복습 1단계 : 데이터 접근하기</h1><p>oh?</p></>
    );
}