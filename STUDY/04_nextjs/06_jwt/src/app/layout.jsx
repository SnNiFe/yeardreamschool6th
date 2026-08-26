export default function Layout({children}) {
    return(
        <html>
        <head>
            <meta charSet="utf-8"/>
            <title>JWT 서비스</title>
        </head>
        <body>{children}</body>
        </html>
    );
}