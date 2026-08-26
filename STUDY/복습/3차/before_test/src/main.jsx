import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import AppTwo from "./AppTwo.jsx";
import AppThree from "./AppThree.jsx";
import DomOne from "./DomOne.jsx";
import Qbank from "./Qbank.jsx";


createRoot(document.getElementById('root')).render(
    <>
        <App />
        <AppTwo />
        <AppThree />
        <DomOne />
        <Qbank />
    </>
)
