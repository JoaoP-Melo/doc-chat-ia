import './homePage.css'
import LogoutButton from "./LogoutButton";
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
                            <div key={chat.id} className="conversation">
                                {chat.title}
                            </div>
                        ))}

                    </div>

                </div>

                <div className='start'>
                        <div className="chat-container">
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
                </div>
            </div>
        </section>
    )
}

export default HomePage