// === Listas estáticas por país ===
const ciudadesMexico = ["Ciudad de México", "Monterrey", "Guadalajara", "Cancún", "Puebla"];
const ciudadesArgentina = ["Buenos Aires", "Córdoba", "Rosario", "Mendoza", "La Plata"];
const ciudadesEspana = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza"];
const ciudadesBrasil = ["Próximamente"];

// === Función para aceptar los términos y mostrar el formulario ===
function aceptarTerminos() {
    document.getElementById('loginFondo').style.display = 'none';
    document.getElementById('registroUsuario').style.display = 'block';
    console.log("Términos aceptados. Mostrando el formulario de registro."); // Log
}

// === Función para verificar el país seleccionado y configurar la ciudad ===
function verificarPais() {
    console.log("Iniciando la verificación de país seleccionado."); // Log

    const paisSeleccionado = document.getElementById("pais").value;
    const ciudadInput = document.getElementById("ciudad");
    const datalist = document.getElementById("ciudades-sugeridas");

    ciudadInput.value = ""; 
    datalist.innerHTML = "";

    if (paisSeleccionado) {
        ciudadInput.disabled = false;
        ciudadInput.placeholder = "Escribe tu ciudad";

        console.log(`País seleccionado: ${paisSeleccionado}`); // Log
        if (paisSeleccionado === "México") {
            cargarCiudadesEstaticas(ciudadesMexico);
        } else if (paisSeleccionado === "Argentina") {
            cargarCiudadesEstaticas(ciudadesArgentina);
        } else if (paisSeleccionado === "España") {
            cargarCiudadesEstaticas(ciudadesEspana);
        } else if (paisSeleccionado === "Brasil") {
            cargarCiudadesEstaticas(ciudadesBrasil);
        }
    } else {
        ciudadInput.disabled = true;
        ciudadInput.placeholder = "Seleccione un país primero";
        console.log("No se seleccionó un país válido."); // Log
    }
}

// === Función para cargar ciudades estáticas en el datalist ===
function cargarCiudadesEstaticas(ciudades) {
    const datalist = document.getElementById("ciudades-sugeridas");
    datalist.innerHTML = ""; // Limpiar el datalist
    console.log("Cargando ciudades estáticas:", ciudades); // Log

    ciudades.forEach(ciudad => {
        const option = document.createElement("option");
        option.value = ciudad;
        datalist.appendChild(option);
        console.log(`Ciudad estática agregada: ${ciudad}`); // Log
    });
}

// === Función para filtrar ciudades según el término ingresado ===
async function filtrarCiudades(valor) {
    console.log("Iniciando la función filtrarCiudades con el valor:", valor); // Log inicial

    const datalist = document.getElementById("ciudades-sugeridas");
    datalist.innerHTML = ""; // Limpiar opciones previas en el datalist

    if (valor.length < 2) {
        console.log("El término es demasiado corto para realizar la búsqueda."); // Log para términos cortos
        return;
    }

    try {
        console.log(`Realizando solicitud al endpoint: /api/get_name_cities?q=${encodeURIComponent(valor)}`); // Log de la solicitud
        const response = await fetch(`/api/get_name_cities?q=${encodeURIComponent(valor)}`);
        console.log("Respuesta obtenida del servidor:", response); // Log para la respuesta del servidor

        if (response.ok) {
            const ciudades = await response.json(); // Parsear JSON con resultados
            console.log("Ciudades recibidas:", ciudades); // Log para los datos recibidos

            ciudades.forEach(ciudad => {
                const option = document.createElement("option");
                option.value = ciudad.ciudad_nombre; // Mostrar el nombre de la ciudad en el datalist
                option.setAttribute("data-id", ciudad.id); // Almacenar el ID como un atributo
                datalist.appendChild(option);
                console.log(`Opción agregada al datalist: ${ciudad.ciudad_nombre} (ID: ${ciudad.id})`); // Log para cada opción
            });
        } else {
            console.error("Error al obtener ciudades. Estado HTTP:", response.status, response.statusText); // Log de error HTTP
        }
    } catch (error) {
        console.error("Error al realizar la solicitud:", error); // Log de error en el fetch
    }
}

// === Función para enviar el formulario de registro al backend ===
async function enviarRegistro(event) {
    event.preventDefault(); // Prevenir el comportamiento por defecto del formulario
    console.log("Iniciando el envío del formulario de registro."); // Log inicial

    // Obtener los valores del formulario
    const nombre = document.getElementById("nombre").value.trim();
    const apellidos = document.getElementById("apellidos").value.trim();
    const correo = document.getElementById("correo").value.trim();
    const profesion = document.getElementById("profesion").value.trim();
    const cedula = document.getElementById("cedula").value.trim();
    const celular = document.getElementById("celular").value.trim();
    const ciudad = document.getElementById("ciudad").value.trim();
    const contrasenia = document.getElementById("contrasenia").value.trim();
    const confirmarContrasenia = document.getElementById("confirmarContrasenia").value.trim();
    const ciudadId = Array.from(document.querySelectorAll("#ciudades-sugeridas option"))
        .find(option => option.value === ciudad)?.getAttribute("data-id");

    console.log("Datos capturados del formulario:", {
        nombre, apellidos, correo, profesion, cedula, celular, ciudad, ciudadId, contrasenia, confirmarContrasenia
    });

    // Validar campos requeridos
    if (!nombre || !apellidos || !correo || !profesion || !cedula || !celular || !ciudad || !ciudadId || !contrasenia || !confirmarContrasenia) {
        console.warn("Algunos campos están vacíos o faltan. No se enviará el formulario.");
        alert("Por favor completa todos los campos requeridos.");
        return;
    }

    // Crear el objeto con los datos del formulario
    const datosRegistro = {
        nombre, apellidos, correo, profesion, cedula, celular, ciudad, ciudad_id: ciudadId, contrasenia, confirmar_contrasenia: confirmarContrasenia
    };
    console.log("Datos preparados para envío:", datosRegistro);

    try {
        console.log("Enviando datos al endpoint: /api/post_register_api");
        const response = await fetch("/api/post_register_api", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(datosRegistro),
        });

        console.log("Respuesta obtenida del servidor:", response);
        if (response.ok) {
            const resultado = await response.json();
            console.log("Registro exitoso:", resultado);
            alert(resultado.message);
            document.getElementById("registroUsuario").reset();
        } else {
            const error = await response.json();
            console.warn("Error al registrar:", error);
            alert(`Error al registrar: ${error.error}`);
        }
    } catch (error) {
        console.error("Error al enviar los datos al servidor:", error);
        alert("Hubo un problema al intentar registrar. Por favor, intenta nuevamente.");
    }
}
// === Listas estáticas para el autocompletado de correos ===
const dominiosCorreo = ["@gmail.com", "@hotmail.com", "@outlook.com", "@yahoo.com", "@icloud.com"];

// === Función para mostrar mensaje dinámico en confirmación de contraseña ===
function mostrarMensaje() {
    const mensaje = document.getElementById("mensaje-confirmacion");
    mensaje.style.display = "block";
    console.log("Mostrando mensaje de advertencia sobre la confirmación de contraseña."); // Log
}

// === Función para autocompletar correos ===
function autocompletarCorreo(valor) {
    const datalist = document.getElementById("dominios-correo");
    datalist.innerHTML = ""; // Limpiar opciones previas en el datalist
    console.log("Iniciando la función autocompletarCorreo con el valor:", valor); // Log inicial

    if (!valor.includes("@")) {
        dominiosCorreo.forEach(dominio => {
            const option = document.createElement("option");
            option.value = valor + dominio;
            datalist.appendChild(option);
            console.log(`Opción de correo sugerida: ${valor + dominio}`); // Log
        });
    }
}