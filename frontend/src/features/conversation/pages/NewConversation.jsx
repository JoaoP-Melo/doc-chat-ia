import { useRef, useState } from "react";

function NewConversation({ onConversationCreated }) {

    const fileInputRef = useRef(null);
    const [loading, setLoading] = useState(false);

    function handleClick() {
        fileInputRef.current.click();
    }

    async function handleFileChange(event) {

        const file = event.target.files[0];

        if (!file) {
            return;
        }

        if (file.type !== "application/pdf") {
            alert("Selecione um arquivo PDF.");
            event.target.value = "";
            return;
        }

        try {
            setLoading(true);

            const formData = new FormData();

            formData.append("file", file);

            const documentResponse = await fetch(
                "http://localhost:8000/document/upload_file/",
                {
                    method: "POST",
                    credentials: "include",
                    body: formData
                }
            );

            if (!documentResponse.ok) {
                throw new Error("Erro ao criar documento.");
            }

            const documentData =
                await documentResponse.json();

            console.log("Documento criado:", documentData);

            const documentId = documentData.id;


            const conversationResponse = await fetch(
                "http://localhost:8000/conversation/create_conversation/",
                {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        document_id: Number(documentId)
                    })
                }
            );

            if (!conversationResponse.ok) {
                throw new Error("Erro ao criar conversa.");
            }

            const conversationData =
                await conversationResponse.json();


            if (onConversationCreated) {
                onConversationCreated(conversationData);
            }

        } catch (error) {

            console.error(
                "Erro ao criar nova conversa:",
                error
            );

        } finally {

            setLoading(false);

            event.target.value = "";
        }
    }

    return (
        <>
            <button
                onClick={handleClick}
                disabled={loading}
            >
                {loading ? "..." : "+"}
            </button>

            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                style={{ display: "none" }}
            />
        </>
    );
}

export default NewConversation;
