import '../style/conversation.css'
import LogoutButton from "../../auth/services/LogoutButton";
import Chat from "../components/ChatMessages";
import NewConversation from "../components/NewConversation";
import { getChatMessages, getChats, deleteConversation } from "../services/conversationService";
import { useEffect, useState } from "react";

function HomePage(){

    const [chats, setChats] = useState([]);

    async function loadChats() {
        try {
            const chats = await getChats();
            setChats(chats);
        } catch (error) {
            console.error(error);
        }
    }

    useEffect(() => {
        loadChats();
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
            const messages = await getChatMessages(chatId);

            setMessages(messages);
            setSelectedChat(chatId);

        } catch (error) {
            console.error("Erro:", error);
        }
    }

    async function handleDeleteChat(chatId) {
        try {
            await deleteConversation(chatId);

            setChats((prevChats) =>
                prevChats.filter((chat) => chat.id !== chatId)
            );

            if (selectedChat === chatId) {
                setSelectedChat(null);
                setMessages([]);
            }

        } catch (error) {
            console.error("Erro ao excluir chat:", error);
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
                            <span>{chat.title}</span>

                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteChat(chat.id);
                                }}
                            >
                                x
                            </button>
                        </div>
                        
                    ))}

                </div>

            </aside>

            <main className="start">

                <div className="chat-container">

                    {selectedChat ? (

                        <Chat
                            messages={messages}
                            selectedChat={selectedChat}
                            handleChatClick={handleChatClick}
                        />
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
