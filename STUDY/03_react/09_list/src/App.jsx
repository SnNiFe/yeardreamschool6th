import Blog from "./component/Blog.jsx";

export default function App(){

    // ctrl + alt + L : 라인절렬
    const posts = [
        {id:1, title:'박찬욱 감독님 표 기생충 -어쩔수가없다 관람후기', category:'영화'},
        {id:2, title:'광명 철산역 숨은맛집 소들녘, 소고기 회식 추천 고기집', category:'맛집'},
        {id:3, title:'컴포즈커피 반값할인 50% 오키클럽행사', category:'카페'},
        {id:4, title:'엘릭서랩(Elixir Lab) 신제품 엑소 크림 4종 전격 리뷰! PDRN 라인까지', category:'미용'},
        {id:5, title:'동급 최강! 가성비 모델 랜드로버 디스커버리 스포츠 시승기', category:'자동차'},
        {id:6, title:'오이도 명물 등대빵 노을바다 뷰 즐기기 좋은 카페 베이커리 방문기', category:'카페'},
    ];
    
    return(<Blog posts={posts} />);
}