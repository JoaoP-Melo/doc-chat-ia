import { useNavigate } from "react-router-dom";
import { apiFetch } from "../services/api";

function LogoutButton() {
    const navigate = useNavigate();

    async function handleLogout() {
        try {
            var options = {
                method: "DELETE",
                credentials: "include"
            }
            const response = await apiFetch("auth/user_logout/", options);

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