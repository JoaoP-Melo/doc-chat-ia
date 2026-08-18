import './homePage.css'
import LogoutButton from "./LogoutButton";
import Chat from "./ChatMessages";
import { useEffect, useState } from "react";

function HomePage(){

    const [chats, setChats] = useState([]);

    useEffect(() => {
        async function loadChats() {
            const response = await fetch(
                "http://localhost:8000/conversation/read_conversation/",
                {
                    method: "GET",
                    credentials: "include"
                }
            );

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            setChats(data.Chats);
        }

        loadChats();
    }, []);

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
        <section>
            <div className='top'>
                <div className='left-column'>
                    
                    <div className='header'>
                        Doc Chat I
                        <LogoutButton />
                    </div>
                    <h2>Conversas</h2>

                    <div className="conversation-list">

                        {chats.map((chat) => (
                            <div key={chat.id} 
                                className="conversation"
                                onClick={() => handleChatClick(chat.id)}>
                                {chat.title}
                            </div>
                        ))}

                    </div>

                </div>

                <div className='start'>
                        <div className="chat-container">
                                    {selectedChat ? (
                                        <Chat messages={messages} />
                                    ) : (
                            <div>
                                <h1>Sobre o que você quer conversar?</h1>

                                <form className="question-form">
                                    <input
                                        type="text"
                                        placeholder="Faça uma pergunta..."
                                    />

                                    <button type="submit">
                                        Enviar
                                    </button>
                                </form>
                            </div>
                        )}
                        </div>
                </div>
            </div>
        </section>
    )
}

export default HomePage