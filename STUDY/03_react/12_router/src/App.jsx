// Router 사용을 위해서 react-router-dom 을 설치해야 한다.
// npm install react-router-dom
import {BrowserRouter, Link, Route, Routes} from 'react-router-dom'
import Home from "./Home.jsx";
import First from "./First.jsx";
import Second from "./Second.jsx";
import Topics from "./Topics.jsx";

export default function App() {
    return (
        <BrowserRouter>
            <div>
                {/*Link to == a href*/}
                <li><Link to={"/"}>Home</Link></li>
                <li><Link to={"/first"}>First</Link></li>
                <li><Link to={"/second"}>Second</Link></li>
                <li><Link to={"/topics"}>Topics</Link></li>
            </div>
            <Routes>
                {/*path = {Link to 요청} element={<컴포넌트/>}*/}
                <Route path={"/"} element={<Home/>}/>
                <Route path={"/first"} element={<First/>}/>
                <Route path={"/second"} element={<Second/>}/>
                {/*topics/뭐가 오더라도...*/}
                <Route path={"/topics/*"} element={<Topics/>}/>
            </Routes>
        </BrowserRouter>
    );
}