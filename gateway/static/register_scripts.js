document.getElementById('registerForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        alert('Por favor, rellena todos los campos.');
        return;
    }

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            alert('¡Registro exitoso! Redirigiendo a la página de películas...');
            window.location.href = '/home_page';
        } else {
            const errorData = await response.json();
            alert(`Error al registrar: ${errorData.detail}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Hubo un problema con el servidor.');
    }
});