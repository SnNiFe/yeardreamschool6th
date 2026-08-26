// state 는 변경시 렌더링을 다시하는 객체
// class 형 컴포넌트에서만 사용 가능했음
// 함수형에선 useState 라는 hooks 를 써서 사용 가능함
// hook 는 갈고리처럼 돌아서 간다는뜻(편법)
import {useState} from "react";

export default function StateBtn(){

    // state 를 통해 값을 변경해야 render() 가 실행 된다.
    const[cnt,setCnt] = useState(100); // UI 변화
    //let cnt = 100; // 일반 연산

    const updateCnt = ()=>{
        setCnt(cnt-1);
        //cnt--;
        console.log(cnt);
    }

    return(
        <div>
            <button onClick={()=>{updateCnt()}}>
                down count : {cnt}
            </button>
        </div>
    );

}