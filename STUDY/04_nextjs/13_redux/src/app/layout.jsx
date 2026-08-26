'use client'
import {Provider} from "react-redux";
import {store} from "@/redux/store";

export default function Layout({children}){
    // 3. Provider 를 통해 store 를 공유
    return(
        <html lang="ko">
        <head>
            <meta charSet="UTF-8" />
            <title>Counter</title>
        </head>
        <body>
        <Provider store={store}>{children}</Provider>
        </body>
        </html>
    );
}