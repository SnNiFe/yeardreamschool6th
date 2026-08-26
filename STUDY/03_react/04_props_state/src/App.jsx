import PropBtn from "./component/PropBtn.jsx";
import StateBtn from "./component/StateBtn.jsx";

const App = ()=> (
    <>
        {/*Props : 부모가 자식에게 보내는 값*/}
        <PropBtn name="This is Prop Button"/>
        <StateBtn/>
    </>)

// 변수에 담은 함수는 export default 를 따로 해 줘야 한다.
export default App;