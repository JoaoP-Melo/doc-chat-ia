import './homePage.css'
import LogoutButton from "./LogoutButton";
import Chat from "./ChatMessages";
import NewConversation from "./NewConversation";
import { useEffect, useState } from "react";

function HomePage(){

    const [chats, setChats] = useState([]);

    async function loadChats() {

        const response = await fetch(
            "http://localhost:8000/conversation/read_conversation/",
            {
                method: "GET",
                credentials: "include"
            }
        );

        if (response.status === 404) {
            setChats([]);
            return;
        }

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        setChats(data.Chats);
    }


    useEffect(() => {
        Promise.resolve().then(loadChats);
    }, []);

    function handleConversationCreated(newConversation) {
        setChats((currentChats) => {
            const alreadyExists = currentChats.some(
                (chat) => chat.id === newConversation.id
            );

            return alreadyExists
                ? currentChats
                : [...currentChats, newConversation];
        });
    }

    const [selectedChat, setSelectedChat] = useState(null);
    const [messages, setMessages] = useState([]);

    async function handleChatClick(chatId) {
        try {
            const response = await fetch(
                `http://localhost:8000/conversation/user_chat/${chatId}/`,
                {
                    method: "GET",
                    credentials: "include"
                }
            );

            if (!response.ok) {
                console.error("Erro ao buscar mensagens");
                return;
            }

            const data = await response.json();

            console.log("Resposta:", data);

            setMessages(data.Messages);
            setSelectedChat(chatId);

        } catch (error) {
            console.error("Erro:", error);
        }
    }


    return (
        <div className="home">

            <aside className="left-column">

                <div className="sidebar-header">
                    <div className="logo">
                        Doc Chat IA
                    </div>

                    <LogoutButton />
                </div>

                <h2 className="conversation-title">
                    Conversas
                </h2>

                <div className="new-conversation">
                    <NewConversation
                        onConversationCreated={handleConversationCreated}
                    />
                </div>

                <div className="conversation-list">

                    {chats.map((chat) => (
                        <div
                            key={`chat-${chat.id}`}
                            className={`conversation ${
                                selectedChat === chat.id ? "conversation-active" : ""
                            }`}
                            onClick={() => handleChatClick(chat.id)}
                        >
                            {chat.title}
                        </div>
                    ))}

                </div>

            </aside>

            <main className="start">

                <div className="chat-container">

                    {selectedChat ? (

                        <Chat messages={messages} />

                    ) : (

                        <div className="empty-chat">

                            <div className="empty-chat-icon">
                                💬
                            </div>

                            <h1>
                                Comece uma conversa
                            </h1>

                            <p>
                                Crie uma nova conversa ou selecione uma conversa
                                existente para começar a fazer perguntas.
                            </p>

                            <div className="empty-chat-actions">

                                <NewConversation
                                    onConversationCreated={handleConversationCreated}
                                />

                            </div>

                        </div>

                    )}

                </div>

            </main>

        </div>
    )
}

export default HomePage
