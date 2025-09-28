class StegoTextoApp {
    constructor() {
        this.form = document.getElementById('userForm');
        this.loading = document.getElementById('loading');
        this.result = document.getElementById('result');
        this.error = document.getElementById('error');
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadImage());
        document.getElementById('newEncodeBtn').addEventListener('click', () => this.resetForm());
        
        // Auto-generate filename based on name and surname
        document.getElementById('name').addEventListener('input', () => this.generateFilename());
        document.getElementById('surname').addEventListener('input', () => this.generateFilename());
    }

    generateFilename() {
        const name = document.getElementById('name').value.trim();
        const surname = document.getElementById('surname').value.trim();
        
        if (name && surname) {
            const filename = `${name.toLowerCase()}_${surname.toLowerCase()}_datos`;
            document.getElementById('filename').value = filename;
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.form);
        const userData = Object.fromEntries(formData);
        
        // Validación básica
        if (!this.validateData(userData)) {
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch('/encode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const result = await response.json();

            if (result.success) {
                this.showResult(result);
            } else {
                this.showError(result.error || 'Error desconocido');
            }
        } catch (error) {
            this.showError('Error de conexión: ' + error.message);
        }
    }

    validateData(data) {
        // Validar email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.email)) {
            this.showError('Por favor ingresa un email válido');
            return false;
        }

        // Validar teléfono (solo números y opcionalmente +, espacios, guiones)
        const phoneRegex = /^[\+]?[0-9\s\-\(\)]+$/;
        if (!phoneRegex.test(data.phone)) {
            this.showError('Por favor ingresa un número de teléfono válido');
            return false;
        }

        return true;
    }

    showLoading() {
        this.form.classList.add('hidden');
        this.loading.classList.remove('hidden');
        this.result.classList.add('hidden');
        this.error.classList.add('hidden');
    }

    showResult(result) {
        this.loading.classList.add('hidden');
        this.result.classList.remove('hidden');
        
        // Mostrar la imagen generada
        const img = document.getElementById('encodedImage');
        img.src = result.image_url + '?t=' + new Date().getTime(); // Cache bust
        
        // Mostrar información
        document.getElementById('imageName').textContent = result.filename;
        document.getElementById('imageSize').textContent = result.image_size;
        document.getElementById('dataLength').textContent = result.data_length;
        
        // Guardar datos para la descarga
        this.currentResult = result;
    }

    showError(message) {
        this.loading.classList.add('hidden');
        this.error.classList.remove('hidden');
        document.getElementById('errorMessage').textContent = message;
    }

    downloadImage() {
        if (this.currentResult) {
            const link = document.createElement('a');
            link.href = this.currentResult.image_url;
            link.download = this.currentResult.filename;
            link.click();
        }
    }

    resetForm() {
        this.result.classList.add('hidden');
        this.form.classList.remove('hidden');
        this.form.reset();
        this.generateFilename(); // Regenerar filename basado en campos vacíos
    }
}

// Función global para ocultar errores
function hideError() {
    document.getElementById('error').classList.add('hidden');
    document.getElementById('userForm').classList.remove('hidden');
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new StegoTextoApp();
});