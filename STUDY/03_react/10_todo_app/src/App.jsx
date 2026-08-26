import Input from "./component/Input.jsx";
import {useEffect, useRef, useState} from "react";
import './App.css'
import List from "./component/List.jsx";

export default function App(){

    // 데이터는 부모에서 자식으로 흐르지만
    // 자식에서 부모로 흐를 수 없다.
    let [val,setVal] = useState('');
    let [list,setList] = useState([]);

    // 최초 렌더링 시 setList 를 통해 리스트 값을 넣는다.
    useEffect(function(){
        setList([
            {id:0,text:'python 공부하기',done:true},
            {id:1,text:'react.js 공부하기',done:false},
            {id:2,text:'next.js 공부하기',done:false}
        ]);
    },[]);

    const onChange = function(e){
        setVal(e.target.value);
    }

    //let idx = 3; // 렌더링이 돌면 초기화 되버린다.
    let idx = useRef(3);
    const onInsert = function(){
        //let idx = list.length; // 내가 해본거
        let todo = {id:idx.current,text:val,done:false};
        setList([...list, todo]);
        setVal('');
        idx.current++;
    }

    const onToggle = function(e,id){
        // 내가 체크한 녀석의 id 를 알아내기
        //console.log(e.target.id);
        //console.log(id);
        // 매개변수로 들어온 id 와 list 안의 id 가 일치하는 index
        let index = list.findIndex(function(item){
            return item.id === id;
        });
        console.log(id+' 가 속한 index 번호 : '+index); // 삭제 대응 id 와 index 별도 처리

        // 새로운 배열에 반전된 값을 걱용
        let new_arr = [...list];
        new_arr[index].done = !list[index].done;
        // 이후 setList 에 적용
        setList(new_arr);

    }

    const onDelete = function(e){
        const id = e.target.id;
        let index = list.findIndex(function(item){
            //console.log(item.id,id);
            return item.id === parseInt(id);
        });
        console.log(id+' 가 속한 index 번호 : '+index);

        let new_arr = [...list];
        // 어떻게 지울 것인가?
        // array.splice(index,del_count,add_data,....);
        new_arr.splice(index,1);
        setList(new_arr);

    }

    return (
        <div className={"app"}>
            <Input onChange={onChange} val={val} onInsert={onInsert}/>
            <List todos={list} onToggle={onToggle} onDelete={onDelete}/>
        </div>
    );
}