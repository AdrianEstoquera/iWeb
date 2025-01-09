// Asegurarse de que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('registerForm').addEventListener('submit', async (event) => {
        event.preventDefault();

        // Obtener los valores de los campos
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        // Validación básica de campos
        if (!username || !password) {
            alert('Por favor, rellena todos los campos.');
            return;
        }

        try {
            // Hacer la solicitud al servidor
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            // Manejo de la respuesta
            if (response.ok) {
                alert('¡Registro exitoso! Redirigiendo a la página de inicio...');
                window.location.href = '/';
            } else {
                const errorData = await response.json();
                alert(`Error al registrar: ${errorData.detail || 'Ocurrió un error inesperado.'}`);
            }
        } catch (error) {
            // Manejo de errores del servidor o de la red
            console.error('Error:', error);
            alert('Hubo un problema con el servidor.');
        }
    });
});
