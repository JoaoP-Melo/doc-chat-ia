import { useRef, useState } from "react";
import apiFetch from "../../../services/api";

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

            var optionsDocuments = {
                    method: "POST",
                    credentials: "include",
                    body: formData
                }
            const documentResponse = await apiFetch(
                "document/upload_file/",
                optionsDocuments
            );

            if (!documentResponse.ok) {
                throw new Error("Erro ao criar documento.");
            }

            const documentData = await documentResponse.json();
      
            const documentId = documentData.id;

            var optionsConversation =  {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        document_id: Number(documentId)
                    })
                }

            const conversationResponse = await apiFetch(
                "conversation/create_conversation/",
                optionsConversation
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
