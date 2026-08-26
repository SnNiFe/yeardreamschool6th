import {configureStore} from "@reduxjs/toolkit";
import memberSlicer from "@/redux/memberSlicer";
import boardSlicer from "@/redux/boardSlicer";

export const store = configureStore({
    reducer:{
        member:memberSlicer,
        board:boardSlicer
    }
});