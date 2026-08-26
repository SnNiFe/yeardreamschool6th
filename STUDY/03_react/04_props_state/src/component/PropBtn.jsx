const PropBtn = ({name}) => {
    console.log(name);

    const sendMsg = (name)=>{
        alert(`Your name is ${name}`);
    }

    return (<div>
        <button onClick={()=>{sendMsg(name)}}>{name}</button>
    </div>);
}

export default PropBtn;