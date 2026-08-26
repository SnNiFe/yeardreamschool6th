// params           : 경로 뒤에 오는 파라메터
// searchParams  : ? 뒤에 오는 파라메터
// await async 는 서버에서 사용 가능
import Post from "@/app/detail/[slug]/Post";

export default async function Detail(props){
    //let {slug} = await props.params;
    let idx = (await props.params).slug;
    console.log(idx);
    return(
        <div>
            <h3>{idx} 번 글 상세보기</h3>
            <hr/>
            <Post idx={idx}/>
        </div>
    );
}