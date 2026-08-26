import {useMemo} from "react";

export default function List({todos, onToggle, onDelete}) {
    //console.log(todos);
    /*
    let items = todos.map(function(todo){
        console.log('rendering');
        return (
            <div key={todo.id} className={"item"}>
                <input id={todo.id} type={"checkbox"}
                       checked={todo.done}
                       onChange={function(e){
                           onToggle(e,todo.id);
                       }}/>
                <div className={`text ${todo.done}`}>
                    {todo.id}. {todo.text}
                </div>
                <div id={todo.id}
                     className={"delete"}
                     onClick={onDelete}>
                    [삭제]
                </div>
            </div>
        );
    });
    */

    
    // useMemo 는 특정 값의 변화가 있을떄만 안의 내용을 실행해 준다.
    let items = useMemo(function(){
        console.log('list rendering...');

        return(
            todos.map(function(todo){
                console.log('rendering');
                return (
                    <div key={todo.id} className={"item"}>
                        <input id={todo.id} type={"checkbox"}
                               checked={todo.done}
                               onChange={function(e){
                                   onToggle(e,todo.id);
                               }}/>
                        <div className={`text ${todo.done}`}>
                            {todo.id}. {todo.text}
                        </div>
                        <div id={todo.id}
                             className={"delete"}
                             onClick={onDelete}>
                            [삭제]
                        </div>
                    </div>
                );
            })
        );
    },[todos]);

    return (
        <div>{items}</div>
    );
}