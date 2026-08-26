export default function AppThree() {

    // c_1
    let nums = [1, 4, 7, 10, 13, 16];
    let result = [];
    for(let i = 0; i < nums.length; i++) {
        result.push(nums[i]);
    }
    // console.log(result);

    //문제 C-1-1 예시 코드:
    let cnums = [1, 4, 7, 10, 13, 16];

    // 1단계: 결과를 담을 빈 배열 선언
    let cresult = [];

    // 2단계: for문과 조건문(if)을 사용하여 데이터 필터링 및 변수에 누적
    for (let i = 0; i < cnums.length; i++) {
        if (cnums[i] > 10) {
            cresult.push(cnums[i]);
        }
    }

    // 3단계: 최종 누적 결과 출력
    // console.log(cresult); // [13, 16]
    // console.log('--3 end--');
    return (<><h1>JS 복습 3단계 : 결과 누적 & 반환</h1><p>skip?</p></>);
}