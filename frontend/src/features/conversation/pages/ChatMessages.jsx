function Chat({ messages }) {
    return (
        <div className="chat">

            <div className="chat-messages">

                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`message ${message.role}`}
                    >
                        {message.content}
                    </div>
                ))}

            </div>

            <div className="chat-input">
                <input
                    type="text"
                    placeholder="Faça uma pergunta..."
                />

                <button>
                    Enviar
                </button>
            </div>

        </div>
    );
}

export default Chat;