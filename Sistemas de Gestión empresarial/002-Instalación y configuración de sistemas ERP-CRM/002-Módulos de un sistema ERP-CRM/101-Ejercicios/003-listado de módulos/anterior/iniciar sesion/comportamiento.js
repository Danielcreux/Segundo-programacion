// comportamiento.js
document.querySelector("button").onclick = function() {
    let usuario = document.querySelector("#usuario").value;
    let contrasena = document.querySelector("#contrasena").value; 
    
    // Crear objeto JSON con credenciales
    const loginData = {
        "usuario": usuario,
        "contrasena": contrasena
    };

    console.log('Enviando datos de login:', loginData);

    // Realizar petición fetch al servidor
    fetch('../../posterior/iniciarsesion.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            window.location = "../escritorio";
        } else { 
            document.querySelector("#estado").textContent = "Error de inicio de sesion";
        }
    })
    .catch(error => {
        console.error(error);
    });
};
