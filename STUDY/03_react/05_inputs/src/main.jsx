import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// import './index.css' // 좌측 정렬을 위해 css 적용 해제
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
