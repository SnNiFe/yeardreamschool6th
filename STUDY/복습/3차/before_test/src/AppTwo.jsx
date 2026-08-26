export default function AppTwo(){
    // a_1
    let nums = [1, 4, 7, 10, 13, 16];
    for(let i=0; i<nums.length; i++){
        if(nums[i]>10){
            //console.log(nums[i]);
        }
    }
    // a_2
    // a_3
    // a_4
    // a_5
    let levels = [1, 5, 8, 12, 15, 20];
    for(let i=0;i<levels.length;i++){
        if(levels[i]%2 === 0){
            //console.log(levels[i]);
        }
    }
    // b_1
    let words = ["apple", "banana", "kiwi", "strawberry", "pear"];
    for(let i=0;i<words.length;i++){
        if(words[i].length > 5){
            //console.log(words[i]);
        }
    }
    // b_2
    let sentence = "JavaScript Is Fun";
    for(let i=0;i<sentence.length;i++){
        if(/[A-Z]/.test(sentence[i])){
            //console.log(sentence[i]);
        }
    }
    // b_3
    let files = ["index.html", "style.css", "script.js", "app.js", "logo.png"];
    for(let i=0;i<files.length;i++){
        if(files[i].endsWith('.js')){
            //console.log(files[i]);
        }
    }
    // b_4
    // b_5
    let users = ["admin", "guest1", "guest2", "manager", "test"];
    for(let i=0;i<users.length;i++){
        if(users[i].includes('guest')){
            //console.log(users[i]);
        }
    }
    // b_6
    // b_7
    // c_1

    // c_5
    let posts = [{title: "Hello", hits: 5}, {title: "World", hits: 100}, {title: "JS", hits: 50}];
    for(let i=0;i<posts.length;i++){
        if(posts[i].hits >= 50){
            //console.log(posts[i].title);
        }
    }
    // d_1

    // d_5
    let data = ["apple", 10, "banana", 20, "cherry"];
    for(let i=0;i<data.length;i++){
        if(typeof data[i] === 'string'){
            //console.log(data[i]);
        }
    }

    //문제 A-1-1 예시 코드:
    let anums = [1, 4, 7, 10, 13, 16];

    // 1단계: 모든 숫자를 순서대로 출력

    for (let i = 0; i < anums.length; i++) {
        // console.log(anums[i]);
    }

    // 2단계: 조건문을 사용하여 10보다 큰 숫자만 출력
    // 새로 입력하는 것이 아니라 위 1단계 코드에서 조건문 영역만 수정/작성

    for (let i = 0; i < anums.length; i++) {
        if (anums[i] > 10) {
            // console.log(anums[i]);
        }
    }

    // console.log('--2 end--');
    return(<><h1>JS 복습 2단계 : 조건 필터링</h1><p>hello</p></>);
}