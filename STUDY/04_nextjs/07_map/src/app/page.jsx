'use client'
import {useEffect, useRef} from "react";

export default function MainPage(){

    let container = useRef(null);

    useEffect(() => {
        // 맵 옵션 설정
        const mapOption = {
            center: new kakao.maps.LatLng(37.535289, 126.897724), // 지도의 중심좌표
            level: 3 // 지도의 확대 레벨
        };
        // 맵 그리기
        let map = new kakao.maps.Map(container.current, mapOption);

        // 맵 중앙에 마커 표시
        let marker = new kakao.maps.Marker({
            position:map.getCenter()
        });
        marker.setMap(map);

        // 이벤트 추가
        kakao.maps.event.addListener(map,'click',function(evt){
            //console.log(evt);
            let pos =  evt.latLng;
            marker.setPosition(pos);
            console.log(`위도 : ${pos.getLat()}/ 경도 : ${pos.getLng()}`);
        });

    }, []);

    return (
        <>
            <div id={"map"} style={{width:"100%", height:"350px"}} ref={container}></div>
        </>
    );
}