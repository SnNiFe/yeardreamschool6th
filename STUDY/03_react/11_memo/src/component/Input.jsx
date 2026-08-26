

export default function Input(props){
    //console.log(props);
    let {onChange, val, onInsert} = props;

    const send = function(e){
        //console.log(e);
        if(e.keyCode === 13){
            onInsert();
        }
    }

    return (
        <div>
            <h2> 해야할 일</h2>
            <hr/>
            <input
                type={"text"}
                onChange={onChange}
                value={val}
                onKeyUp={send}
            />
            <button onClick={onInsert}>추 가</button>
        </div>
    );
}