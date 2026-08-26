export default function App(){
    return(
        <>
            <First item={"Third에 보내는 데이터"}/>
            <Island item={"Island 에 보내는 데이터"}/>
        </>
    );

}

// 비(분해)구조 할당 안썼음
function First(props){
    return(
        <>
            <div>First Component / 거쳐가는 곳 1 : {props.item}</div>
            <Second item={props.item}/>
        </>
    );
}

function Island(props){
    return(
        <div>Island Component / 도착지 : {props.item}</div>
    );
}

// 비(분해)구조 할당 사용
function Second({item}){
    return(
        <>
            <div>Second Component / 거쳐가는 곳 2 : {item}</div>
            <Third item={item}/>
        </>
    );
}

function Third({item}){
    return(
        <div>Third Component / 도착지 : {item}</div>
    );
}