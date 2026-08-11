import './registerPage.css'
import { Link } from 'react-router-dom'
import { useState } from 'react'

function RegisterPage() {
    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [password1, setPassword1] = useState('')
    const [password2, setPassword2] = useState('')
    
    function handleSubmit(event) {
        event.preventDefault()
    }

        return (
        <div className='main'>
            <h1>Registrar Usuario</h1>
            <form className='form'onSubmit={handleSubmit}>
                <div className='field'>
                    <label htmlFor="username">Nome de usuario</label>

                    <input
                        id="username"
                        type="text"
                        value={username}
                        onChange={(event) => setUsername(event.target.value)}
                        placeholder="Digite o nome"
                    />
                </div>

                <div className='field'>
                    <label htmlFor="email">Email</label>

                    <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        placeholder="Digite o email"
                    />
                </div>

                <div className='field'>
                    <label htmlFor="password1">Senha</label>

                    <input
                        id="password1"
                        type="password"
                        value={password1}
                        onChange={(event) => setPassword1(event.target.value)}
                        placeholder="Digite a senha"
                    />
                </div>

                <div className='field'>
                    <label htmlFor="password2">Confirme a senha</label>

                    <input
                        id="password2"
                        type="password"
                        value={password2}
                        onChange={(event) => setPassword2(event.target.value)}
                        placeholder="Confirme a senha"
                    />
                </div>

                <button type="submit">
                    Confirmar
                </button>

                <Link to="/login" className="button">
                    Voltar
                </Link>
            </form>
        </div>
    )
}

export default RegisterPage