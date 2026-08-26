export default async function Page(props){
    console.log("props",props);

    let params = await props.params;
    // [slug] 일 경우 slug:11
    console.log("params",params.slug);
    // [...slug] 일 경우 blog/11 -> slug:['11']
    // [...slug] 일 경우 blog/food/11 -> slug:['food','11']
    // [...slug] 일 경우 blog/food/korea/11 -> slug:['food','korea','11']

    let list = params.slug.map((item,idx)=> <li key={idx}>{idx} : {item}</li>);

    return (
        <>
            <p>경로로 받은 파라메터</p>
            <ul>{list}</ul>
        </>
    );
}