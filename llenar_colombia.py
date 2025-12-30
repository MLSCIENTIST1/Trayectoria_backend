from src.models.colombia_data.colombia_data import Colombia
from src.models.database import db
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


def poblar_ciudades():
    ciudades = [
        "Leticia", "Puerto Nariño", "Medellín", "Bello", "Itagüí", "Envigado", "Rionegro", "Apartadó", "Arauca", "Saravena", 
        "Arauquita", "Barranquilla", "Soledad", "Malambo", "Puerto Colombia", "Cartagena", "Magangué", "Turbaco", "Tunja", 
        "Duitama", "Sogamoso", "Chiquinquirá", "Manizales", "Villamaría", "Chinchiná", "Florencia", "Yopal", "Popayán", 
        "Santander de Quilichao", "Valledupar", "Aguachica", "Quibdó", "Istmina", "Montería", "Cereté", "Lorica", "Bogotá", 
        "Soacha", "Zipaquirá", "Girardot", "Facatativá", "Chía", "Fusagasugá", "Inírida", "San José del Guaviare", "Neiva", 
        "Pitalito", "Garzón", "Riohacha", "Maicao", "Uribia", "Santa Marta", "Ciénaga", "Fundación", "Villavicencio", 
        "Acacías", "Granada", "Pasto", "Ipiales", "Tumaco", "Cúcuta", "Ocaña", "Pamplona", "Mocoa", "Puerto Asís", 
        "Armenia", "Montenegro", "Circasia", "Pereira", "Dosquebradas", "Santa Rosa de Cabal", "San Andrés", "Providencia", 
        "Bucaramanga", "Floridablanca", "Girón", "Piedecuesta", "Sincelejo", "Corozal", "Ibagué", "Espinal", "Melgar", 
        "Cali", "Palmira", "Buenaventura", "Tuluá", "Jamundí", "Mitú", "Puerto Carreño", "Abejorral", "Abriaquí", 
        "Alejandría", "Amagá", "Amalfi", "Andes", "Angelópolis", "Angostura", "Anorí", "Anzá", "Arboletes", "Argelia", 
        "Armenia", "Barbosa", "Belmira", "Betania", "Betulia", "Briceño", "Buriticá", "Cáceres", "Caicedo", "Caldas", 
        "Campamento", "Cañasgordas", "Caracolí", "Caramanta", "Carepa", "Carolina del Príncipe", "Caucasia", "Chigorodó", 
        "Cisneros", "Ciudad Bolívar", "Cocorná", "Concepción", "Concordia", "Copacabana", "Dabeiba", "Donmatías", 
        "Ebéjico", "El Bagre", "El Carmen de Viboral", "El Santuario", "Entrerríos", "Fredonia", "Frontino", "Giraldo", 
        "Girardota", "Gómez Plata", "Granada", "Guadalupe", "Guarne", "Guatapé", "Heliconia", "Hispania", "Itagüí", 
        "Ituango", "Jardín", "Jericó", "La Ceja", "La Estrella", "La Pintada", "La Unión", "Liborina", "Maceo", 
        "Marinilla", "Montebello", "Murindó", "Mutatá", "Nariño", "Nechí", "Olaya", "Peque", "Pueblorrico", "Puerto Berrío", 
        "Puerto Nare", "Puerto Triunfo", "Remedios", "Retiro", "Rionegro", "Sabanalarga", "Sabaneta", "Salgar", "San Andrés", 
        "San Carlos", "San Francisco", "San Jerónimo", "San José de la Montaña", "San Juan de Urabá", "San Luis", 
        "San Pedro de Urabá", "San Pedro de los Milagros", "San Rafael", "San Roque", "San Vicente", "Santa Bárbara", 
        "Santa Fe de Antioquia", "Santa Rosa de Osos", "Santo Domingo", "Segovia", "Sonsón", "Sopetrán", "Támesis", 
        "Tarazá", "Tarso", "Titiribí", "Toledo", "Turbo", "Uramita", "Urrao", "Valdivia", "Valparaíso", "Vegachí", 
        "Venecia", "Vigía del Fuerte", "Yalí", "Yarumal", "Yolombó", "Yondó", "Zaragoza", "Abriaquí", "Alejandría", "Amagá", "Amalfi", "Andes", "Angelópolis", "Angostura", "Anorí", "Anzá", 
        "Arboletes", "Argelia", "Armenia", "Barbosa", "Belmira", "Betania", "Betulia", "Briceño", "Buriticá", 
        "Cáceres", "Caicedo", "Caldas", "Campamento", "Cañasgordas", "Caracolí", "Caramanta", "Carepa", 
        "Carolina del Príncipe", "Caucasia", "Chigorodó", "Cisneros", "Ciudad Bolívar", "Cocorná", "Concepción", 
        "Concordia", "Copacabana", "Dabeiba", "Donmatías", "Ebéjico", "El Bagre", "El Carmen de Viboral", 
        "El Santuario", "Entrerríos", "Fredonia", "Frontino", "Giraldo", "Girardota", "Gómez Plata", "Granada", 
        "Guadalupe", "Guarne", "Guatapé", "Heliconia", "Hispania", "Itagüí", "Ituango", "Jardín", "Jericó", 
        "La Ceja", "La Estrella", "La Pintada", "La Unión", "Liborina", "Maceo", "Marinilla", "Montebello", 
        "Murindó", "Mutatá", "Nariño", "Nechí", "Olaya", "Peque", "Pueblorrico", "Puerto Berrío", "Puerto Nare", 
        "Puerto Triunfo", "Remedios", "Retiro", "Rionegro", "Sabanalarga", "Sabaneta", "Salgar", "San Andrés", 
        "San Carlos", "San Francisco", "San Jerónimo", "San José de la Montaña", "San Juan de Urabá", "San Luis", 
        "San Pedro de Urabá", "San Pedro de los Milagros", "San Rafael", "San Roque", "San Vicente", "Santa Bárbara", 
        "Santa Fe de Antioquia", "Santa Rosa de Osos", "Santo Domingo", "Segovia", "Sonsón", "Sopetrán", "Támesis", 
        "Tarazá", "Tarso", "Titiribí", "Toledo", "Turbo", "Uramita", "Urrao", "Valdivia", "Valparaíso", "Vegachí", 
        "Venecia", "Vigía del Fuerte", "Yalí", "Yarumal", "Yolombó", "Yondó", "Zaragoza", "Aguazul", "Albania", 
        "Alcalá", "Anapoima", "Anserma", "Apía", "Armero", "Ayapel", "Bahía Solano", "Balboa", "Baranoa", 
        "Becerril", "Belalcázar", "Belén", "Beltrán", "Betéitiva", "Boavita", "Bolívar", "Bosconia", "Bugalagrande", 
        "Cabuyaro", "Cajamarca", "Calamar", "Caloto", "Campoalegre", "Canalete", "Candelaria", "Caparrapí", 
        "Capitanejo", "Carmen de Apicalá", "Carmen de Carupa", "Cartago", "Caucasia", "Cajibío", "Caldas", 
        "Castilla la Nueva", "Cereté", "Chalán", "Chámeza", "Chaparral", "Chía", "Chimá", "Chinchiná", "Chiriguaná", 
        "Chocontá", "Chinchiná", "Chinú", "Chipaque", "Choachí", "Chopinzal", "Circasia", "Ciénaga", "Cisneros", 
        "Cota", "Coper", "Cómbita", "Coromoro", "Cumaral", "Cuítiva", "Dagua", "Dibulla", "Distracción", "El Banco", 
        "El Carmen de Bolívar", "El Cerrito", "El Colegio", "El Dorado", "El Líbano", "El Molino", "El Peñol", 
        "El Retorno", "El Zulia", "Enciso", "Entrerríos", "Espinal", "Gachalá", "Gachancipá", "Gachetá", "Gamarra", 
        "Gámeza", "Garzón", "Gigante", "Guaduas", "Guamo", "Guapi", "Guavatá", "Guayabal de Síquima", "Guática", 
        "Gutiérrez", "Hato", "Herrán", "Herveo", "Honda", "Icononzo", "Ipiales", "Isnos", "Jamundí", "Jenoy", 
        "Jerusalén", "La Belleza", "La Calera", "La Esperanza", "La Florida", "La Jagua de Ibirico", "La Mesa", 
        "La Paz", "La Tebaida", "La Unión", "Labateca", "Lago Agrio","La Dorada", "La Vega", "La Victoria", "Lebrija", "Líbano", "Linares", "Lorica", "Los Andes", "Los Palmitos", 
        "Madrid", "Magangué", "Mahates", "Malambo", "Manaure", "Manzanares", "Mariquita", "Marmato", "Marsella", 
        "Martinica", "Medina", "Mejía", "Mesitas", "Miraflores", "Mistrató", "Mocoa", "Momil", "Montelíbano", 
        "Montecristo", "Montenegro", "Morales", "Mosquera", "Murillo", "Natagaima", "Nemocón", "Neiva", "Nilo", 
        "Nocaima", "Norcasia", "Obando", "Ocamonte", "Oiba", "Oporapa", "Orito", "Ospina", "Otanche", "Pachavita", 
        "Paicol", "Pailitas", "Palermo", "Palestina", "Palmar", "Palmas del Socorro", "Palmira", "Pamplona", "Pamplonita", 
        "Pandi", "Paratebueno", "Pasca", "Patía", "Paz de Río", "Pedraza", "Pelaya", "Peñol", "Pensilvania", "Pereira", 
        "Piedecuesta", "Pinchote", "Piojó", "Pisba", "Pitalito", "Plato", "Policarpa", "Pradera", "Pueblo Rico", 
        "Puerto Berrío", "Puerto Boyacá", "Puerto Caicedo", "Puerto Carreño", "Puerto Colombia", "Puerto Concordia", 
        "Puerto Escondido", "Puerto Gaitán", "Puerto Guzmán", "Puerto Libertador", "Puerto Lleras", "Puerto Nariño", 
        "Puerto Rico", "Puerto Salgar", "Puerto Santander", "Puracé", "Purificación", "Quebradanegra", "Quibdó", 
        "Quinchía", "Quipile", "Ricaurte", "Río Viejo", "Riofrío", "Rionegro", "Risaralda", "Riviera", "Roberto Payán", 
        "Roldanillo", "Roncesvalles", "San Benito", "San Bernardo", "San Diego", "San Estanislao", "San Jacinto", 
        "San José", "San Juan Nepomuceno", "San Luis de Gaceno", "San Miguel", "San Onofre", "San Pablo", "San Pelayo", 
        "San Sebastián", "San Vicente", "Santa Ana", "Santa Bárbara", "Santa Catalina", "Santa Isabel", "Santa Lucía", 
        "Santa María", "Santa Rosa", "Santa Rosalía", "Santander", "Santo Domingo", "Santuario", "Sapuyes", "Saravena", 
        "Sardinata", "Sasaima", "Segovia", "Sesquilé", "Sibaté", "Silvia", "Sitionuevo", "Soacha", "Soplaviento", 
        "Sora", "Sotaquirá", "Suaza", "Suesca", "Supatá", "Suquita", "Suratá", "Susacón", "Sutamarchán", "Támara", 
        "Tame", "Taminango", "Tangatá", "Tauramena", "Tenza", "Tibacuy", "Tibaná", "Tibú", "Timaná", "Timbío", "Timoteo", 
        "Titiribí", "Toca", "Tocancipá", "Toledo", "Tolu", "Toluviejo", "Tomarrazón", "Trujillo", "Tubará", "Tumaco", 
        "Tuta", "Tutazá", "Ubala", "Ubalá", "Ulloa", "Umbita", "Une", "Útica", "Valdivia", "Valle de San Juan", 
        "Valledupar", "Vegachí", "Venadillo", "Venecia", "Vergara", "Vetas", "Villamaría", "Villanueva", "Villapinzón", 
        "Villeta", "Viterbo", "Yacuanquer", "Yaguará", "Yarumal", "Yolombó", "Yondo", "Yopal", "Zambrano", "Zapatoca", 
        "Zaragoza", "Zetaquira","Acevedo", "Achí", "Agrado", "Aipe", "Albania", "Aldana", "Alejandría", "Algarrobo", "Almaguer", 
        "Altamira", "Alto Baudó", "Altos del Rosario", "Ancuya", "Andalucía", "Anorí", "Anza", "Apartadó", 
        "Aracataca", "Aranzazu", "Arbeláez", "Arboleda", "Arboledas", "Arjona", "Armenia", "Astrea", "Ataco", 
        "Atrato", "Ayapel", "Bagadó", "Bahía Solano", "Barbacoas", "Barichara", "Barrancas", "Becerril", 
        "Belén de Bajirá", "Belén de Umbría", "Belén", "Berbeo", "Betéitiva", "Bolívar", "Bosconia", "Bochalema", 
        "Boyacá", "Briceño", "Buenavista", "Buenaventura", "Buenos Aires", "Buriticá", "Cabrera", "Cabuyaro", 
        "Cáchira", "Cajamarca", "Cajibío", "Calamar", "Calarcá", "Calima", "Campamento", "Campo de la Cruz", 
        "Campoalegre", "Cantagallo", "Caparrapí", "Caracolí", "Caramanta", "Carepa", "Carmen del Darién", 
        "Carmen de Chucurí", "Carmen de Viboral", "Carurú", "Casabianca", "Castilla la Nueva", "Caucasia", 
        "Cepitá", "Cereté", "Chachagüí", "Chaguaní", "Chámeza", "Chaparral", "Charalá", "Charta", "Chíquiza", 
        "Chigorodó", "Choachí", "Chocontá", "Chámeza", "Cicuco", "Colón", "Colosó", "Coper", "Corrales", 
        "Cota", "Cotorra", "Coveñas", "Cravo Norte", "Curití", "Curumaní", "Cumbal", "Cumbitara", "Cunday", 
        "Dabeiba", "Dagua", "Dibulla", "Distracción", "Dolores", "Donmatías", "Durania", "El Águila", 
        "El Banco", "El Cantón del San Pablo", "El Carmen de Bolívar", "El Carmen", "El Charco", 
        "El Cocuy", "El Colegio", "El Copey", "El Doncello", "El Dorado", "El Encanto", "El Espino", 
        "El Litoral del San Juan", "El Molino", "El Paso", "El Peñol", "El Piñón", "El Playón", "El Retiro", 
        "El Roble", "El Rosal", "El Rosario", "El Tablón de Gómez", "El Tarra", "El Zulia", "Encino", 
        "Enciso", "Entrerríos", "Envigado", "Flandes", "Florencia", "Florian", "Floridablanca", 
        "Fosca", "Francisco Pizarro", "Fredonia", "Fresno", "Frontino", "Fuente de Oro", "Fundación", 
        "Funza", "Funes", "Fusagasugá", "Gachalá", "Gachancipá", "Gachetá", "Galapa", "Galeras", 
        "Gama", "Gamarra", "Garagoa", "Garzón", "Genova", "Gigante", "Ginebra", "Giraldo", "Girardota", 
        "Gómez Plata", "Guaca", "Guacamayas", "Guachené", "Guachetá", "Guadalupe", "Guaduas", "Guaitarilla", 
        "Gualmatán", "Guamal", "Guamo", "Guapí", "Guayabal de Síquima", "Guayabetal", "Gutiérrez", 
        "Hato Corozal", "Heliconia", "Herrán", "Herveo", "Honda", "Iles", "Imués", "Inzá", 
        "Ipiales", "Isnos", "Istmina", "Ituango", "Jambaló", "Jardín", "Jericó", "Jerusalén", "Junín", 
        "La Apartada", "La Argentina", "La Belleza", "La Capilla", "La Cumbre", "La Gloria", 
        "La Jagua de Ibirico", "La Llanada", "La Macarena", "La Mesa", "La Palma", "La Paz", "La Plata", 
        "La Primavera", "La Salina", "La Sierra", "La Tebaida", "La Uvita", "La Vega", "La Victoria", "Labranzagrande", "Landázuri", "Lebrija", "Leiva", "Lenguazaque", "Lérida", "Liborina", "Linares", "López de Micay", 
        "Lorica", "Los Andes", "Los Córdobas", "Los Palmitos", "Luruaco", "Macanal", "Maceo", "Machetá", "Madrid", 
        "Magüí Payán", "Majagual", "Malambo", "Mallama", "Manatí", "Manaure Balcón del Cesar", "Manaure", "Manzanares", 
        "Mapiripán", "Mapiripana", "Margarita", "María la Baja", "Marinilla", "Maripí", "Mariquita", "Marmato", "Marsella", 
        "Marulanda", "Matanza", "Medina", "Medio Atrato", "Medio Baudó", "Medio San Juan", "Melgar", "Mercaderes", 
        "Mesetas", "Milán", "Miraflores", "Miranda", "Mistrató", "Mocarí", "Mogotes", "Molagavita", "Momil", 
        "Mompox", "Montelíbano", "Montecristo", "Montenegro", "Morales", "Morelia", "Morroa", "Murillo", "Murindó", 
        "Mutatá", "Mutiscua", "Nariño", "Nátaga", "Natagaima", "Nechí", "Nemocón", "Nilo", "Nimaima", "Nobsa", 
        "Nocaima", "Norcasia", "Norosí", "Novita", "Nueva Granada", "Nuevo Colón", "Nunchía", "Nuquí", "Obando", 
        "Ocamonte", "Ocaña", "Ochí", "Olaya Herrera", "Onzaga", "Oporapa", "Ovejas", "Pachavita", "Padilla", 
        "Paicol", "Pajarito", "Palestina", "Palmar de Varela", "Palmar", "Palmas del Socorro", "Pamplonita", 
        "Pandi", "Panqueba", "Páramo", "Paratebueno", "Pasca", "Paz de Ariporo", "Pedraza", "Pelaya", "Pensilvania", 
        "Peque", "Pesca", "Piamonte", "Pie de Cuesta", "Piedras", "Piendamó", "Pijao", "Pijiño del Carmen", 
        "Piojó", "Pisba", "Policarpa", "Ponedera", "Popayán", "Pore", "Potosí", "Pradera", "Providencia", 
        "Puerto Alegría", "Puerto Arica", "Puerto Asís", "Puerto Berrío", "Puerto Bogotá", "Puerto Boyacá", 
        "Puerto Caicedo", "Puerto Carreño", "Puerto Colombia", "Puerto Concordia", "Puerto Escondido", 
        "Puerto Gaitán", "Puerto Guzmán", "Puerto Leguízamo", "Puerto Libertador", "Puerto Lleras", 
        "Puerto López", "Puerto Nare", "Puerto Nariño", "Puerto Parra", "Puerto Rico", "Puerto Rondón", 
        "Puerto Salgar", "Puerto Santander", "Puerto Tejada", "Puerto Triunfo", "Puerto Wilches", 
        "Puracé", "Pueblorrico", "Puebloviejo", "Quebradanegra", "Quetame", "Quimbaya", "Quinchía", 
        "Quipama", "Ragonvalia", "Ramiriquí", "Recetor", "Regidor", "Remedios", "Remolino", "Ricaurte", 
        "Río de Oro", "Río Quito", "Risaralda", "Riosucio", "Risaralda", "Rivera", "Roberto Payán", 
        "Roldanillo", "Roncesvalles", "Rondón", "Rosas", "Rovira", "Sabana de Torres", "Sabana Larga", 
        "Sabanagrande", "Sabanalarga", "Sabaneta", "Saboyá", "Sacama", "Sáchica", "Sahagún", "Saladoblanco", 
        "Salamina", "Salazar", "Saldaña", "Salento", "Samacá", "Samaná", "Samaniego", "San Agustín", 
        "San Alberto", "San Andrés", "San Andrés de Cuerquia", "San Antero", "San Antonio del Tequendama", 
        "San Benito Abad", "San Benito", "San Bernardo del Viento", "San Bernardo", "San Calixto", 
        "San Carlos", "San Diego", "San Eduardo", "San Estanislao", "San Francisco", "San Gil", "San Jacinto", 
        "San Jacinto del Cauca", "San Jerónimo", "San José del Guaviare"
        
        ]
    
    try:
        for ciudad_nombre in ciudades:
            nueva_ciudad = Colombia(ciudad_nombre=ciudad_nombre)
            db.session.add(nueva_ciudad)
        
        db.session.commit()
        print("Ciudades agregadas exitosamente.")
    except Exception as e:
        db.session.rollback()
        print(f"Ocurrió un error al poblar las ciudades: {e}")

if __name__ == "__main__":
    # Asegúrate de que se inicialice la app de Flask antes de llamar este script
    from src import create_app
    app = create_app()
    with app.app_context():
        poblar_ciudades()