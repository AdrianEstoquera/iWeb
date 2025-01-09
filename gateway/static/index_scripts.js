document.addEventListener('DOMContentLoaded', () => {
    // Botón de login
    document.getElementById('loginBtn').addEventListener('click', async (event) => {
        event.preventDefault(); // Prevenir el comportamiento por defecto del botón submit

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        if (!username || !password) {
            alert('Por favor, rellena todos los campos.');
            return;
        }

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (response.ok) {
                const data = await response.json();
                // Guardar el token JWT en el almacenamiento local
                localStorage.setItem('jwt', data.access_token);
                alert('¡Inicio de sesión exitoso!');
                // Redirigir a la página de películas
                window.location.href = '/home_page';
            } else {
                alert('Error al iniciar sesión. Por favor, verifica tus datos.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Hubo un problema con el servidor.');
        }
    });

    // Botón registrar
    document.getElementById('registerBtn').addEventListener('click', () => {
        window.location.href = '/register_user';
    });
});
