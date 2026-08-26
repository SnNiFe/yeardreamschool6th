import {configureStore} from "@reduxjs/toolkit";
import counterSlicer from "@/redux/counterSlicer";

// 2. 완성된 slicer 를 store 에 등록
export const store = configureStore({
    reducer: {
        counter:counterSlicer
    }
});