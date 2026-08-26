import {createSlice} from "@reduxjs/toolkit";
import axios from "axios";
// reducer 함수에 등록되지 말아야 할것들
// 1. Promise 객체를 반환하는 비동기 기능(예 : axios)
// 2. payload 로 전달되는 객체중 함수가 포함된 객체(직렬화가 안되는 객체는 받지 않는다.)
const memberSlicer = createSlice({
    name:'member',
    initialState:{
        info:{id:'',pw:''}
    },
    reducers:{

    }
});

export default memberSlicer.reducer;