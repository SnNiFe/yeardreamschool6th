// React 의 컴포넌트는 함수형과 클래스형이 있다.
function App(){

  let name = 'Naaak';
  let gender = '남자';
  let age = 30;

  // 본래 js 에서는 태그는 문자열에 담는다.
  // jsx 는 태그 자체를 담을 수 있따.
  // let js = '<h3>Hello World</h3>';
  // let jsx = <h3>Hello World</h3>;
  return (
      <>
        <div className="App">
          <h3>안녕하세요 리엑트에 잘 오셨습니다.</h3>
        </div>
        <div>
          {name}/{gender}/{age} {/*자바스크립트 관련은 {} 로 영역을 잡하준다.*/}
          <br/> {/*태그는 닫히지 않으면 에러가 난다.*/}
        </div>
        <div>
          {/*return 안에서는 if 문 사용이 불가능하다. 3항 연산자로 대체 가능*/}
          {/* eslint-disable-next-line no-constant-condition */}
          {1+1 === 2 ? (<p>맞아요</p>):(<p>틀려요</p>)}
          {/*굳이 if 를 사용하겠다면 익명함수 내에서 활용 하면 된다.*/
              (()=>{
                  if (age === 10) {
                      return <div>열살</div>
                  }
                  if (age === 20) {
                      return <div>스무살</div>
                  }
                  if (age === 30) {
                      return <div>서른살</div>
                  }
              })()
              /*start()*/
          }
        </div>
      </>
  );
}

export default App;