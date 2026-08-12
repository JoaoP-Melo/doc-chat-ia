import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LoginPage from './features/auth/pages/loginPage.jsx'
import RegisterPage from './features/auth/pages/registerPage.jsx'
import HomePage from './features/conversation/pages/homePage.jsx'

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<LoginPage/>}/>
                <Route path="/register" element={<RegisterPage/>}/>
                <Route path="/home" element={<HomePage/>}/>
            </Routes>
        </BrowserRouter>
    )
}

export default App