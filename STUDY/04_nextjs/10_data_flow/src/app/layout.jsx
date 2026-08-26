export default function Layout({ children }) {
    return(
        <html lang="ko">
            <head>
                <meta charSet={"UTF-8"} />
                <title>Props Drilling</title>
            </head>
            <body>
                {children}
            </body>
        </html>
    );
}