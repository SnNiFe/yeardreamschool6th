// 폴더의 대표는 page 라는 이름을 가지고 있어야 한다.
import Link from "next/link";

export default function Page(){
    return (
        <div>
            <h1>Main Page</h1>
            <p><Link href="/blog">페이지 이동</Link></p>
            <p><Link href="/blog?idx=11&method=detail">쿼리 파라메터</Link></p>
            <p><Link href="/blog/11">path variable</Link></p>
        </div>
    );
}