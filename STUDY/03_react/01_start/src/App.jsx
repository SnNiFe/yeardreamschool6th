import './App.css'

function App() {

  let html = <h3>Hello, React.js</h3>;
  // return 은 render() 를 품고 있다.
  // return 안에서는 태그 하나로 끝나야 한다.
  return (<>{html}</>);
}

// App.jsx 에서는 기본으로 App 함수를 내보낸다.
export default App
