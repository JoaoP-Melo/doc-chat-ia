import './loginPage.css'
import { Link } from 'react-router-dom'
import { useState } from 'react'

function LoginPage() {
    const [email, setUsername] = useState('')
    const [password, setPassword] = useState('')
    
    function handleSubmit(event) {
        event.preventDefault()
    }

        return (
        <div className='main'>
            <h1>Entrar</h1>
            <form className='form'onSubmit={handleSubmit}>
                <div className='field'>
                    <label htmlFor="username">Email</label>

                    <input
                        id="username"
                        type="text"
                        value={email}
                        onChange={(event) => setUsername(event.target.value)}
                        placeholder="Digite o email"
                    />
                </div>

                <div className='field'>
                    <label htmlFor="password">Senha</label>

                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        placeholder="Digite a senha"
                    />
                </div>

                <button type="submit">
                    Acessar
                </button>

                <div className='link-register'>
                    <p>
                        <Link to="/register">Criar conta</Link>
                    </p>
                </div>

            </form>
        </div>
    )
}

export default LoginPage