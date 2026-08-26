export default function List({todos, onToggle, onDelete}) {
    //console.log(todos);

    let items = todos.map(function(todo){
        return (
            <div key={todo.id} className={"item"}>
                <input id={todo.id} type={"checkbox"}
                        // /*className={todo.id} // 내가 한거*/
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
    return (
        <div>{items}</div>
    );
}