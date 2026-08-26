export default function Layout({children}) {
    const API_KEY = 'd6ba0722fa0bc0c2e8339b71005166a4';

    return (
        <html>
            <head>
                <meta charSet={"UTF-8"} />
                <title>KAKAO MAP API</title>
                <script type="text/javascript" src={`https://dapi.kakao.com/v2/maps/sdk.js?appkey=${API_KEY}`}></script>
            </head>
            <body>
                {children}
            </body>
        </html>
    );
}