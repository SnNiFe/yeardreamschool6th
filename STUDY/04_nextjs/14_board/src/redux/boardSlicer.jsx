import {createSlice} from "@reduxjs/toolkit";
import axios from "axios";

const boardSlicer = createSlice({
    name:'board',
    initialState:{
        id:typeof window == 'undefined'? '' : sessionStorage.getItem('id'),
        token:typeof window == 'undefined'? '' : sessionStorage.getItem('token'),
        list:[],
        pages:0,
        info:{},
        photos:[]
    },
    reducers:{
        setList(state,action){
            console.log('action.payload',action.payload);
            state['list'] = action.payload.list;
            state['pages'] = action.payload.pages;
            return state;
        },
        setDetail(state,action){
            state['info'] = action.payload.info;
            state['photos'] = action.payload.photos;
        }
    }
});

export default boardSlicer.reducer;