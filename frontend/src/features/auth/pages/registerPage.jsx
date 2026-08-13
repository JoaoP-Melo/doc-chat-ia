import './registerPage.css'
import { Link } from 'react-router-dom'
import { useState } from 'react'

const upperWord = [
  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 
  'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 
  'U', 'V', 'W', 'X', 'Y', 'Z'
];

const lowerWord = [
  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 
  'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 
  'u', 'v', 'w', 'x', 'y', 'z'
];

const numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

function correctPassword(pass) {
    const hasUpper = [...pass].some(char => upperWord.includes(char));
    const hasLower = [...pass].some(char => lowerWord.includes(char));
    const hasNumber = [...pass].some(char => numbers.includes(char));

    if (pass.length > 0 && !hasUpper) {
        return <p className="alert">A senha deve ter uma letra maiúscula.</p>;
    }

    if (pass.length > 0 && !hasLower) {
        return <p className="alert">A senha deve ter uma letra minúscula.</p>;
    }

    if (pass.length > 0 && !hasNumber) {
        return <p className="alert">A senha deve ter um número.</p>;
    }

    if (pass.length > 0 && pass.length < 8) {
        return <p className="alert">A senha deve ter pelo menos 8 caracteres.</p>;
    }

    return null;
}

function matchingPasswords(pass1, pass2) {
    if (pass1.length > 0 && pass2.length > 0 && pass1 !== pass2) {
        return <p className="alert">As duas senhas devem ser iguais</p>;
    }
}

function RegisterPage() {
    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [password1, setPassword1] = useState('')
    const [password2, setPassword2] = useState('')
    
    const handleSubmit = async (event) => {
        event.preventDefault();

        if (
            username.length === 0 ||
            email.length === 0 ||
            password1.length === 0 ||
            password2.length === 0
        ){return;}

        const response = await fetch(
            "http://localhost:8000/auth/user_registration/",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    username: username,
                    email: email,
                    password1: password1,
                    password2: password2
                })
            }
        );

        const data = await response.json();

        console.log(data);
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

                    {correctPassword(password1)}

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

                    {matchingPasswords(password1, password2)}
                </div>

                <button 
                    type="submit"
                    disabled={
                    username.length === 0 ||
                    email.length === 0 ||
                    password1.length === 0 ||
                    password2.length === 0
                    }
                >
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