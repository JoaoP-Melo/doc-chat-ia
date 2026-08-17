import { useNavigate } from "react-router-dom";

function LogoutButton() {
    const navigate = useNavigate();

    async function handleLogout() {
        try {
            const response = await fetch("http://localhost:8000/auth/user_logout/", {
                method: "DELETE",
                credentials: "include"
            });

            if (response.ok) {
                navigate("/login/");
            }
        } catch (error) {
            console.error("Erro ao fazer logout:", error);
        }
    }

    return (
        <button onClick={handleLogout}>
            Sair
        </button>
    );
}

export default LogoutButton;