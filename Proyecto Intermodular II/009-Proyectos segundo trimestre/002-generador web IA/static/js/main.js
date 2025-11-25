document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("prompt-form");
    const promptInput = document.getElementById("prompt");
    const statusBox = document.getElementById("status");
    const iframe = document.getElementById("preview-frame");
    const generateBtn = document.getElementById("generate-btn");

    function setStatus(message, type = "info") {
        statusBox.textContent = message || "";
        statusBox.className = "status " + type;
    }

    function setLoading(isLoading) {
        if (isLoading) {
            generateBtn.disabled = true;
            generateBtn.textContent = "Generando...";
        } else {
            generateBtn.disabled = false;
            generateBtn.textContent = "Generar página";
        }
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const prompt = promptInput.value.trim();
        if (!prompt) {
            setStatus("Escribe un prompt primero.", "error");
            return;
        }

        setStatus("");
        setLoading(true);

        try {
            const response = await fetch(GENERATE_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ prompt })
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.error || "Error HTTP " + response.status);
            }

            const data = await response.json();
            const html = data.html || "<h1>No se ha recibido HTML</h1>";

            // Render inside iframe using srcdoc
            iframe.srcdoc = html;

            setStatus("Página generada correctamente.", "success");
        } catch (err) {
            console.error(err);
            setStatus("Error al generar la página: " + err.message, "error");
        } finally {
            setLoading(false);
        }
    });
});

