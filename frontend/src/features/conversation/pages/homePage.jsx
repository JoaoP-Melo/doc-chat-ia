import './homePage.css'

function HomePage(){

    const conversations = 
    [
        {
            id: 1,
            titulo: "Como funciona o React?"
        },
        {
            id: 2,
            titulo: "Meu projeto de IA"
        },
        {
            id: 3,
            titulo: "Estudando FastAPI"
        },
        {
            id: 4,
            titulo: "Dúvidas sobre PostgreSQL"
        }
    ];

    return (
        <section>
            <div className='top'>
                <div className='left-column'>
                    
                    <div className='header'>
                        Doc Chat IA
                        Sair
                    </div>
                    <h2>Conversas</h2>

                    <div className="conversation-list">

                        {conversations.map((conversa) => (
                            <div
                                className="conversation"
                                key={conversa.id}
                            >
                                {conversa.titulo}
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