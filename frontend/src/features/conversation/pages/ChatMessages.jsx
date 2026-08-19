import ReactMarkdown from "react-markdown";

function Chat({ messages }) {
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

            </div>

            <form
                className="question-form"
                onSubmit={(event) => event.preventDefault()}
            >

                <input
                    type="text"
                    placeholder="Faça uma pergunta..."
                />

                <button type="submit">
                    Enviar
                </button>

            </form>

        </div>
    );
}

export default Chat;
