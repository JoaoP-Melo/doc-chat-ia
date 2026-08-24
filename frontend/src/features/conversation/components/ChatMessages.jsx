import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { useEffect, useRef } from "react";
import apiFetch from "../../../services/api";

function Chat({ messages, selectedChat, handleChatClick }) {

    const [question, setQuestion] = useState("");
    const [loading, setLoading] = useState(false); 
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth"
        });
    }, [messages]);

    function handleQuestionChange(e) {
        setQuestion(e.target.value);

        const textarea = messagesEndRef.current;

        textarea.style.height = "auto";
        textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }

    async function handleSubmit(e) {
        e.preventDefault();

        if (!question.trim() || loading || !selectedChat) return;

        setLoading(true);

        try {

            var options = {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: "include",
                    body: JSON.stringify({
                        conversation_id: Number(selectedChat),
                        question: question,
                    }),
            }

            await apiFetch(
                "conversation/user_question/",
                options
            );

            setQuestion("");
            
            await handleChatClick(selectedChat);

        } catch (error) {
            console.error("Erro ao enviar pergunta:", error);
        }finally {
        setLoading(false);
        }

    }

    return (
        <div className="chat">

            <div className="messages">

                {messages.map((message) => (

                    <div
                        key={message.id}
                        className={`message message-${message.role}`}
                    >
                        <div className="message-content">
                            <ReactMarkdown>
                                {message.content}
                            </ReactMarkdown>
                        </div>
                    </div>

                ))}

                <div ref={messagesEndRef} />
                
            </div>

            <form
                className="question-form"
                onSubmit={handleSubmit}
            >
                <textarea
                    placeholder="Faça uma pergunta..."
                    value={question}
                    onChange={handleQuestionChange}
                    rows={1}
                />

                <button type="submit" disabled={loading}>
                    {loading ? "Enviando..." : "Enviar"}
                </button>
            </form>

        </div>
    );
}

export default Chat;