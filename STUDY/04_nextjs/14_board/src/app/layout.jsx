'use client'
import {Provider} from "react-redux";
import {store} from "@/redux/store";

export default function Layout({children}) {
    return(
        <html>
        <head>
            <meta charSet="utf-8"/>
            <title>JWT 서비스</title>
        </head>
        <body>
        <Provider store={store}>{children}</Provider>
        </body>
        </html>
    );
}