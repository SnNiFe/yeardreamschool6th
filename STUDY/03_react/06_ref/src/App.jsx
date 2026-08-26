import GetElem from "./component/GetElem.jsx";
import RefVar from "./component/RefVar.jsx";
// export default 는 이 안의 많은 함수(모듈) 중 이게 대표로 나갈거다.
export default function App(){
    return(
        <div>
            <GetElem/>
            <RefVar/>
        </div>
    );
}