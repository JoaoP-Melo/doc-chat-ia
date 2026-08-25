import apiFetch from "../../../services/api";

export async function getChats() {
    var options = {
            method: "GET",
        }
        
    const response = await apiFetch(
        "conversation/",
        options
    );

    if (!response.ok) {
        throw new Error("Erro ao carregar conversas");
    }

    const data = await response.json();

    return data.Chats;
}

export async function getChatMessages(chatId) {
    var options = {
            method: "GET",
    }

    const response = await apiFetch(
        `conversation/${chatId}/messages`,
        options
    );

    if (!response.ok) {
        throw new Error("Erro ao buscar mensagens");
    }

    const data = await response.json();

    return data.Messages;
}

export async function deleteConversation(chatId) {
    var options = {
            method: "DELETE",
    }

    const response = await apiFetch(
        `conversation/${chatId}`,
        options
    );

    if (!response.ok) {
        throw new Error("Erro ao excluir conversa");
    }
}