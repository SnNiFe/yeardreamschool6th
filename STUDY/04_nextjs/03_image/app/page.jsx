import Image from "next/image";

export default function Page(){
    /*
    * 절대 경로 : /src -> 서버의 메인을 중심으로(기준이 바뀌기도 한다.)
    * 상대 경로 : ./src, src -> 현재위치를 기준으로
    *  ./ 는 현재 위치, ../ 현재 위치에서 한단계 위
    */
    return (
        <div>
            <img src="/incheon.jpg" width={1027} height={768} alt="incheon image"/>
            <hr/>
            <Image src="/incheon.jpg" width={1027} height={768} alt="incheon image"
            placeholder="blur" blurDataURL="/incheon_small.jpg"/>
        </div>
    );
}