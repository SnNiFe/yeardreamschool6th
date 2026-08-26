import {createSlice} from "@reduxjs/toolkit";

// slice? state+reducer 가 쪼개져서 들어가 있다는 의미
// 1. 실행할 reducer 와 state 를 선언해 slicer 를 만든다.
const counterSlicer = createSlice({
    name:'counter', // 슬라이스 이름
    initialState:{ // 사용 스테이트
        value:0
    },
    reducers:{ // 리듀서 등록(state 를 변화시키는 함수)
        increment:(state,action)=>{
            console.log('state',state);
            console.log('action',action);
            state.value = state.value + 1; // state 안의 value 속성을 변경 후
            return state; // 밖으로 던진다.
        },
        decrement:(state,action)=>{
            console.log('state',state);
            console.log('action',action);
            state.value = state.value - 1;
            return state;
        }
    }
});

export default counterSlicer.reducer;