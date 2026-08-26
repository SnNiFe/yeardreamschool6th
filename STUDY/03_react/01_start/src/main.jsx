import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
// id="root" 인 요소를 가져와 뭘 그린다?
createRoot(document.getElementById('root')).render(
  <StrictMode> {/*엄격 모드 : 문법 검사를 정석적으로 함*/}
    <App />      {/*<App/> 은 App 함수(클래스) 컴포넌트를 가져온것*/}
  </StrictMode>,
)
