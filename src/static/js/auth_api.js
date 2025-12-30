document.querySelector('form').addEventListener('submit', function(event) {
    event.preventDefault(); // Evita que el formulario se envíe automáticamente

    const correo = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value.trim();

    if (!correo || !password) {
        alert('Por favor, completa todos los campos antes de iniciar sesión.');
        return;
    }

    fetch('{{ url_for("auth_api_bp.login") }}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ correo, password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message); // Logueo exitoso
        } else if (data.error) {
            alert(data.error); // Error en el logueo
        }
    })
    .catch(error => console.error('Error:', error));
});


<script>
// Función para mostrar/ocultar la barra de navegación
function toggleNav() {
    const nav = document.querySelector('.navegacion');
    nav.classList.toggle('hide');
}

function mostrarLogin() {
    document.getElementById('loginFondo').classList.add('active');
}

function cerrarLogin() {
    document.getElementById('loginFondo').classList.remove('active');
}
</script>
</body>
</html>
<script src="{{ url_for('static', filename='js/login.js') }}"></script>