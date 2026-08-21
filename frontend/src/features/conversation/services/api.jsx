const API_URL = "http://localhost:8000/";

export async function apiFetch(endpoint, options = {}) {
    let response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        credentials: "include",
    });

    
    if (response.status == 401) {
        const refreshResponse = await fetch(
            `${API_URL}auth/refresh_token/`,
            {
                method: "POST",
                credentials: "include",
            }
        );

        if (refreshResponse.status == 401) {
            window.location.href = "/login";
            return null;
        }

        response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            credentials: "include",
        });
    }

    return response;
}

export default apiFetch;