export default function Blog({posts}) {
    console.log(posts); // for 이용해서 값을 꺼냄 -> html 태그 생성 -> 변수에 넣는다.
    /*
    let list = []; // react 에서 변수에 태그를 넣으면 하나의 객체로 인식
    for (const post of posts) {
        list.push(<div key={post.id}>
            <h3>{post.id} : {post.title}</h3>
            <p>category : {post.category}</p>
        </div>);
    }
    */

    // map 은 배열의 내용을 하나씩 꺼내 작업한 다음 새로운 배열로 내보내는 함수
    let list = posts.map(function(post){
        return (<div key={post.id}>
            <h3>{post.id} : {post.title}</h3>
            <p>category : {post.category}</p>
        </div>);
    });

    return (<>{list}</>);
}