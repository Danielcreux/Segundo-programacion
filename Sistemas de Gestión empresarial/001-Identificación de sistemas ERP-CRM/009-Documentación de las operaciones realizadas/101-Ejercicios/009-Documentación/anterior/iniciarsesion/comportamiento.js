document.querySelector("button").onclick = function() {
    let usuario = document.querySelector("#usuario").value;
    let contrasena = document.querySelector("#contrasena").value; 
    
    const loginData = {
        "usuario": usuario,
        "contrasena": contrasena,
    };

    console.log('Enviando datos de login:', loginData);

    fetch('../../posterior/iniciarsesion.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData)
    })
    .then(response => {
        console.log('Status HTTP:', response.status);
        console.log('Headers:', response.headers);
        
        // Primero obtener el texto de la respuesta
        return response.text().then(text => {
            console.log('Respuesta cruda del servidor:', text);
            
            // Intentar parsear como JSON
            try {
                const data = JSON.parse(text);
                return data;
            } catch (e) {
                console.error('No es JSON válido:', text);
                throw new Error('El servidor no devolvió JSON válido: ' + text.substring(0, 100));
            }
        });
    })
    .then(data => {
        console.log('Datos parseados:', data);
        if (data.success) {
            window.location = "../";
        } else { 
            document.querySelector("#estado").textContent = "Error: " + data.message;
        }
    })
    .catch(error => {
        console.error('Error completo:', error);
        document.querySelector("#estado").textContent = "Error de conexión: " + error.message;
    });
};