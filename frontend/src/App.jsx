import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LoginPage from './features/auth/pages/loginPage.jsx'
import RegisterPage from './features/auth/pages/registerPage.jsx'

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<LoginPage/>}/>
                <Route path="/register" element={<RegisterPage/>}/>
            </Routes>
        </BrowserRouter>
    )
}

export default App