// 요청시 파라메터는 props 를 통해서 받아낼 수 있다.
export default async function Page(props){
    /*
    props.params.then(function(res){
        console.log(res);
    });
    */
    // console.log(props.searchParams);
    // props.searchParams.then(function(res){
    //     console.log(res);
    // });
    // console.log(props);

    let search = await props.searchParams;
    console.log(search); // object

    // 키를 하나씩 추출
    let items = Object.keys(search).map(function(key){
        console.log(key,search[key]);  // 키에 해당하는 값 추출
        return (<li key={key}>{key}:{search[key]}</li>);  // html 로 보여주기 위해 조립
    });

    return (
        <div>
            <h1>blog/page.jsx</h1>
            <ul>{items}</ul>
        </div>
    );
}