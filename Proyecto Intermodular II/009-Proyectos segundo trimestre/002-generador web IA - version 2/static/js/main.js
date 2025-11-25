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
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ prompt })
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.error || "Error HTTP " + response.status);
            }

            const data = await response.json();
            const html = data.html || "<h1>No se ha recibido HTML</h1>";

            iframe.srcdoc = html;

            setStatus("Página generada correctamente.", "success");
        } catch (err) {
            console.error(err);
            setStatus("Error al generar la página: " + err.message, "error");
        } finally {
            setLoading(false);
        }
    });


    // ---------------------------
    // DESCARGAR COMO WEBP
    // ---------------------------
    document.getElementById("download-img").addEventListener("click", async () => {
        const iframeDoc = iframe.contentDocument;
        if (!iframeDoc || !iframeDoc.body) {
            alert("No hay contenido generado.");
            return;
        }

        const canvas = await html2canvas(iframeDoc.body, {
            scale: 2,
            useCORS: true
        });

        const dataURL = canvas.toDataURL("image/webp", 1.0);

        const response = await fetch("/export_webp", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({image: dataURL})
        });

        const blob = await response.blob();
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "landing.webp";
        a.click();
    });


    // ---------------------------
    // DESCARGAR ZIP (HTML + CSS)
    // ---------------------------
    document.getElementById("download-zip").addEventListener("click", async () => {
        let title = prompt("Nombre de la página:");

        const response = await fetch("/download_project", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({title: title || "landing"})
        });

        const blob = await response.blob();
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "proyecto.zip";
        a.click();
    });
});
