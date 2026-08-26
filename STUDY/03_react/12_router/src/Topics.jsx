import {Link, Route, Routes, useParams} from "react-router-dom";

export default function Topics(){
    // 원래 Link to 는 Browser Router 로 감싸져 있어야 한다.
    // 하지만 현재 최상위에 감싸져 있으므로 이곳에서는 쓰지 않아도 된다.
    return(
        <div>
            <h2>Topics</h2>
            <ul>
                <li><Link to={"/topics/comment/1"}>comment</Link></li>
                <li><Link to={"/topics/detail/357"}>상세글</Link></li>
            </ul>
            <Routes>
                <Route path={"/:cate/:topicId"} element={<Topic/>}/>
            </Routes>
        </div>
    );
}

function Topic(){
    console.log(useParams());
    let {cate, topicId} = useParams();
    return (<h3>Request Topic : {cate} / {topicId}</h3>);
}