import "../style/auth.css";
import { Link } from 'react-router-dom'
import { useState } from 'react'
import { useNavigate } from "react-router-dom";

function LoginPage() {
    const navigate = useNavigate();
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')

    const handleSubmit = async (event) => {
        event.preventDefault();

        const response = await fetch(
            "http://localhost:8000/auth/login/",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include",
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );

        if (response.status !== 200) {
            alert("Usuário ou senha incorretos.");
            return;
        }

        if (response.ok) {
            navigate("/home");
        }

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
                        onChange={(event) => {
                            setEmail(event.target.value);
                            setError("");
                        }}
                        placeholder="Digite o email"
                    />

                    {error && (
                        <p className="alert">
                            {error}
                        </p>
                    )}

                </div>

                <div className='field'>
                    <label htmlFor="password">Senha</label>

                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(event) => {
                            setPassword(event.target.value);
                            setError("");
                        }}
                        placeholder="Digite a senha"
                    />

                    {error&& (
                        <p className="alert">
                            {error}
                        </p>
                    )}

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