# test_ingredientes.py
import unittest
from faker import Faker

# Lógica y modelos reales
from src.logica.LogicaRecetario import LogicaRecetario
from src.modelo.declarative_base import session
from src.modelo.ingrediente import Ingrediente
from src.modelo.ingrediente_receta import IngredienteReceta
from src.modelo.receta import Receta


class TestIngredientes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.faker = Faker("es_ES")

    def setUp(self):
        # Limpieza de tablas para aislar cada test
        session.query(IngredienteReceta).delete()
        session.query(Ingrediente).delete()
        session.query(Receta).delete()
        session.commit()

        self.logica = LogicaRecetario()

    def tearDown(self):
        session.rollback()

    # ---------- Helpers ----------
    def _crear_ingrediente(
        self, nombre=None, unidad="g", valor=100, sitio="Mercado Central"
    ):
        if not nombre:
            nombre = self.faker.unique.word().capitalize()
        ing = Ingrediente(
            nombre=nombre.strip(),
            unidad_medida=unidad.strip(),
            valor_unidad=int(valor),
            sitio_compra=sitio.strip(),
        )
        session.add(ing)
        session.flush()
        return ing

    def _indice_ingrediente_por_nombre(self, nombre):
        ingredientes = session.query(Ingrediente).all()
        for i, ing in enumerate(ingredientes):
            if ing.nombre == nombre:
                return i
        return None

    def _crear_receta(
        self,
        nombre=None,
        tiempo="00:20:00",
        personas=2,
        calorias=None,
        preparacion=None,
    ):
        if not nombre:
            nombre = self.faker.unique.word().capitalize()
        if not preparacion:
            preparacion = self.faker.sentence()
        r = Receta(
            nombre=nombre.strip(),
            tiempo_preparacion=tiempo,
            numero_personas=int(personas),
            calorias_porcion=int(calorias) if calorias is not None else None,
            preparacion=preparacion.strip(),
        )
        session.add(r)
        session.flush()
        return r

    def _indice_receta_por_nombre(self, nombre):
        recetas = session.query(Receta).all()
        for i, r in enumerate(recetas):
            if r.nombre == nombre:
                return i
        return None

    # ---------- Casos para dar_ingrediente --------------------

    def test_dar_ingrediente_devuelve_el_ingrediente_correcto_por_indice(self):
        # Crear varios ingredientes
        datos = []
        for _ in range(3):
            nombre = self.faker.unique.word().capitalize()
            unidad = self.faker.random_element(elements=("g", "ml", "unidad", "libra"))
            valor = self.faker.random_int(min=100, max=10000)
            sitio = self.faker.company()

            ing = self._crear_ingrediente(nombre, unidad, valor, sitio)
            datos.append((nombre, unidad, valor, sitio))

        session.commit()

        # Verificar por índice 0, 1 y 2 según orden de inserción
        for idx, (nombre, unidad, valor, sitio) in enumerate(datos):
            ingrediente = self.logica.dar_ingrediente(idx)
            self.assertIsInstance(ingrediente, dict)
            self.assertEqual(ingrediente["nombre"], nombre)
            self.assertEqual(ingrediente["unidad"], unidad)
            self.assertEqual(ingrediente["valor"], valor)
            self.assertEqual(ingrediente["sitioCompra"], sitio)

    def test_dar_ingrediente_indice_fuera_de_rango_devuelve_none(self):
        # Sin ingredientes: cualquier índice es inválido
        self.assertIsNone(self.logica.dar_ingrediente(0))

        # Con un ingrediente: 0 válido, 1 inválido -> None
        self._crear_ingrediente("Tomate", "unidad", 500, "Mercado")
        session.commit()
        self.assertIsNotNone(self.logica.dar_ingrediente(0))
        self.assertIsNone(self.logica.dar_ingrediente(1))
        self.assertIsNone(self.logica.dar_ingrediente(-1))

    def test_dar_ingrediente_indice_negativo_devuelve_none(self):
        # Crear un ingrediente
        self._crear_ingrediente("Cebolla", "libra", 2000, "Plaza")
        session.commit()

        # Índices negativos deben devolver None
        self.assertIsNone(self.logica.dar_ingrediente(-1))
        self.assertIsNone(self.logica.dar_ingrediente(-5))

    def test_dar_ingrediente_devuelve_copia_no_referencia(self):
        # Crear un ingrediente
        self._crear_ingrediente("Ajo", "unidad", 100, "Tienda")
        session.commit()

        # Obtener el ingrediente dos veces
        ing1 = self.logica.dar_ingrediente(0)
        ing2 = self.logica.dar_ingrediente(0)

        # Deben ser objetos diferentes (copia, no referencia)
        self.assertIsNot(ing1, ing2)
        # Pero con el mismo contenido
        self.assertEqual(ing1, ing2)

    def test_dar_ingrediente_maneja_ingredientes_con_datos_especiales(self):
        # Ingrediente con nombre muy largo
        nombre_largo = "Ingrediente con nombre muy largo y descriptivo"
        self._crear_ingrediente(nombre_largo, "kg", 5000, "Supermercado")

        # Ingrediente con valor 0
        self._crear_ingrediente("Gratis", "unidad", 0, "Regalo")

        # Ingrediente con sitio de compra con caracteres especiales
        sitio_especial = "Mercado 'El Buen Precio' & Cía."
        self._crear_ingrediente("Especial", "g", 1000, sitio_especial)

        session.commit()

        # Verificar que todos se pueden obtener correctamente
        self.assertEqual(self.logica.dar_ingrediente(0)["nombre"], nombre_largo)
        self.assertEqual(self.logica.dar_ingrediente(1)["valor"], 0)
        self.assertEqual(self.logica.dar_ingrediente(2)["sitioCompra"], sitio_especial)

    def test_dar_ingrediente_estructura_del_diccionario(self):
        # Crear un ingrediente con datos conocidos
        nombre = "Papa"
        unidad = "libra"
        valor = 3000
        sitio = "Plaza de Mercado"

        self._crear_ingrediente(nombre, unidad, valor, sitio)
        session.commit()

        ingrediente = self.logica.dar_ingrediente(0)

        # Verificar que tiene todas las claves esperadas
        claves_esperadas = {"nombre", "unidad", "valor", "sitioCompra"}
        self.assertEqual(set(ingrediente.keys()), claves_esperadas)

        # Verificar tipos de datos
        self.assertIsInstance(ingrediente["nombre"], str)
        self.assertIsInstance(ingrediente["unidad"], str)
        self.assertIsInstance(ingrediente["valor"], int)
        self.assertIsInstance(ingrediente["sitioCompra"], str)

        # Verificar que no hay claves extra
        self.assertEqual(len(ingrediente), 4)

    def test_dar_ingrediente_con_muchos_ingredientes(self):
        # Crear muchos ingredientes para probar rendimiento
        cantidad = 50
        datos_esperados = []

        for i in range(cantidad):
            nombre = f"Ingrediente_{i:03d}"
            unidad = self.faker.random_element(
                elements=("g", "ml", "unidad", "libra", "kg")
            )
            valor = self.faker.random_int(min=100, max=50000)
            sitio = f"Tienda_{i}"

            self._crear_ingrediente(nombre, unidad, valor, sitio)
            datos_esperados.append((nombre, unidad, valor, sitio))

        session.commit()

        # Verificar que se pueden obtener todos los ingredientes
        for i in range(cantidad):
            ingrediente = self.logica.dar_ingrediente(i)
            self.assertIsNotNone(ingrediente)
            self.assertEqual(ingrediente["nombre"], datos_esperados[i][0])
            self.assertEqual(ingrediente["unidad"], datos_esperados[i][1])
            self.assertEqual(ingrediente["valor"], datos_esperados[i][2])
            self.assertEqual(ingrediente["sitioCompra"], datos_esperados[i][3])

    # ---------- Casos para dar_ingredientes (plural) --------------------

    def test_dar_ingredientes_sin_ingredientes_devuelve_lista_vacia(self):
        # Sin ingredientes en la base de datos
        ingredientes = self.logica.dar_ingredientes()
        self.assertIsInstance(ingredientes, list)
        self.assertEqual(len(ingredientes), 0)

    def test_dar_ingredientes_con_un_ingrediente_devuelve_lista_con_un_elemento(self):
        # Crear un ingrediente
        nombre = "Tomate"
        unidad = "libra"
        valor = 3000
        sitio = "Mercado Central"
        self._crear_ingrediente(nombre, unidad, valor, sitio)
        session.commit()

        ingredientes = self.logica.dar_ingredientes()
        
        self.assertIsInstance(ingredientes, list)
        self.assertEqual(len(ingredientes), 1)
        
        ingrediente = ingredientes[0]
        self.assertEqual(ingrediente["nombre"], nombre)
        self.assertEqual(ingrediente["unidad"], unidad)
        self.assertEqual(ingrediente["valor"], valor)
        self.assertEqual(ingrediente["sitioCompra"], sitio)

    def test_dar_ingredientes_con_multiples_ingredientes_devuelve_todos(self):
        # Crear varios ingredientes con datos diferentes
        datos_ingredientes = [
            ("Papa", "libra", 2000, "Plaza de Mercado"),
            ("Cebolla", "unidad", 500, "Tienda Local"),
            ("Ajo", "cabeza", 800, "Supermercado"),
            ("Zanahoria", "libra", 1500, "Fruver")
        ]

        for nombre, unidad, valor, sitio in datos_ingredientes:
            self._crear_ingrediente(nombre, unidad, valor, sitio)
        session.commit()

        ingredientes = self.logica.dar_ingredientes()
        
        self.assertIsInstance(ingredientes, list)
        self.assertEqual(len(ingredientes), len(datos_ingredientes))

        # Verificar que todos los ingredientes están presentes
        nombres_obtenidos = [ing["nombre"] for ing in ingredientes]
        nombres_esperados = [datos[0] for datos in datos_ingredientes]
        
        # Los nombres deben estar todos presentes (sin importar el orden)
        self.assertEqual(set(nombres_obtenidos), set(nombres_esperados))

    def test_dar_ingredientes_estructura_correcta_de_diccionarios(self):
        # Crear ingredientes con diferentes características
        self._crear_ingrediente("Ingrediente1", "g", 100, "Sitio1")
        self._crear_ingrediente("Ingrediente2", "ml", 200, "Sitio2")
        self._crear_ingrediente("Ingrediente3", "unidad", 300, "Sitio3")
        session.commit()

        ingredientes = self.logica.dar_ingredientes()
        
        # Verificar que cada ingrediente tiene la estructura correcta
        claves_esperadas = {"nombre", "unidad", "valor", "sitioCompra"}
        
        for ingrediente in ingredientes:
            self.assertIsInstance(ingrediente, dict)
            self.assertEqual(set(ingrediente.keys()), claves_esperadas)
            
            # Verificar tipos de datos
            self.assertIsInstance(ingrediente["nombre"], str)
            self.assertIsInstance(ingrediente["unidad"], str)
            self.assertIsInstance(ingrediente["valor"], int)
            self.assertIsInstance(ingrediente["sitioCompra"], str)

    def test_dar_ingredientes_devuelve_copia_no_referencia(self):
        # Crear un ingrediente
        self._crear_ingrediente("Test", "unidad", 100, "Tienda")
        session.commit()

        # Obtener la lista dos veces
        ingredientes1 = self.logica.dar_ingredientes()
        ingredientes2 = self.logica.dar_ingredientes()

        # Las listas deben ser diferentes objetos
        self.assertIsNot(ingredientes1, ingredientes2)
        
        # Los diccionarios dentro también deben ser diferentes objetos
        self.assertIsNot(ingredientes1[0], ingredientes2[0])
        
        # Pero con el mismo contenido
        self.assertEqual(ingredientes1, ingredientes2)

    def test_dar_ingredientes_orden_consistente(self):
        # Crear ingredientes en orden específico
        nombres = ["Zebra", "Alpha", "Charlie", "Beta"]
        for nombre in nombres:
            self._crear_ingrediente(nombre, "unidad", 100, "Tienda")
        session.commit()

        # Obtener ingredientes múltiples veces
        ingredientes1 = self.logica.dar_ingredientes()
        ingredientes2 = self.logica.dar_ingredientes()
        ingredientes3 = self.logica.dar_ingredientes()

        # El orden debe ser consistente entre llamadas
        nombres1 = [ing["nombre"] for ing in ingredientes1]
        nombres2 = [ing["nombre"] for ing in ingredientes2]
        nombres3 = [ing["nombre"] for ing in ingredientes3]

        self.assertEqual(nombres1, nombres2)
        self.assertEqual(nombres2, nombres3)

    def test_dar_ingredientes_con_datos_especiales(self):
        # Ingredientes con casos especiales
        datos_especiales = [
            ("Nombre con espacios  ", "unidad con espacios", 0, "Sitio con 'comillas'"),
            ("", "g", 999999, ""),  # Casos límite
            ("Ñoño", "kg", 5000, "Tienda & Cía"),  # Caracteres especiales
            ("Ingrediente muy largo con muchos caracteres", "litro", 1, "Supermercado")
        ]

        for nombre, unidad, valor, sitio in datos_especiales:
            self._crear_ingrediente(nombre, unidad, valor, sitio)
        session.commit()

        ingredientes = self.logica.dar_ingredientes()
        
        self.assertEqual(len(ingredientes), len(datos_especiales))
        
        # Verificar que todos los datos especiales se manejan correctamente
        for ingrediente in ingredientes:
            self.assertIsInstance(ingrediente["nombre"], str)
            self.assertIsInstance(ingrediente["unidad"], str)
            self.assertIsInstance(ingrediente["valor"], int)
            self.assertIsInstance(ingrediente["sitioCompra"], str)

    def test_dar_ingredientes_rendimiento_con_muchos_ingredientes(self):
        # Crear una cantidad considerable de ingredientes
        cantidad = 100
        
        for i in range(cantidad):
            nombre = f"Ingrediente_{i:04d}"
            unidad = self.faker.random_element(elements=("g", "ml", "unidad", "libra", "kg"))
            valor = self.faker.random_int(min=1, max=100000)
            sitio = f"Sitio_{i}"
            self._crear_ingrediente(nombre, unidad, valor, sitio)
        
        session.commit()

        # Medir que la operación se complete sin errores
        ingredientes = self.logica.dar_ingredientes()
        
        self.assertEqual(len(ingredientes), cantidad)
        
        # Verificar que todos los ingredientes tienen la estructura correcta
        for ingrediente in ingredientes:
            self.assertIn("nombre", ingrediente)
            self.assertIn("unidad", ingrediente)
            self.assertIn("valor", ingrediente)
            self.assertIn("sitioCompra", ingrediente)

    def test_dar_ingredientes_despues_de_eliminar_algunos(self):
        # Crear varios ingredientes
        nombres = ["Ingrediente1", "Ingrediente2", "Ingrediente3", "Ingrediente4"]
        for nombre in nombres:
            self._crear_ingrediente(nombre, "unidad", 100, "Tienda")
        session.commit()

        # Verificar que inicialmente tenemos todos
        ingredientes_inicial = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes_inicial), 4)

        # Eliminar algunos ingredientes directamente de la base de datos
        ingredientes_bd = session.query(Ingrediente).all()
        session.delete(ingredientes_bd[1])  # Eliminar el segundo
        session.delete(ingredientes_bd[3])  # Eliminar el cuarto
        session.commit()

        # Verificar que dar_ingredientes refleja los cambios
        ingredientes_final = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes_final), 2)
        
        nombres_restantes = [ing["nombre"] for ing in ingredientes_final]
        self.assertIn("Ingrediente1", nombres_restantes)
        self.assertIn("Ingrediente3", nombres_restantes)
        self.assertNotIn("Ingrediente2", nombres_restantes)
        self.assertNotIn("Ingrediente4", nombres_restantes)
    
    
   # ---------- Casos para eliminar_ingrediente --------------------

    def test_eliminar_ingrediente_exitoso(self):
        # Crear varios ingredientes
        ing1 = self._crear_ingrediente("Tomate", "unidad", 500, "Mercado")
        ing2 = self._crear_ingrediente("Cebolla", "unidad", 300, "Mercado")
        ing3 = self._crear_ingrediente("Ajo", "unidad", 100, "Mercado")
        session.commit()

        # Verificar que inicialmente hay 3 ingredientes
        ingredientes_iniciales = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes_iniciales), 3)

        # Eliminar el ingrediente del índice 1 (Cebolla)
        resultado = self.logica.eliminar_ingrediente(1)
        self.assertTrue(resultado)  # Debe retornar True si fue exitoso

        # Verificar que ahora hay 2 ingredientes
        ingredientes_finales = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes_finales), 2)

        # Verificar que se eliminó el correcto (Cebolla)
        nombres_ingredientes = {ing["nombre"] for ing in ingredientes_finales}
        self.assertIn("Tomate", nombres_ingredientes)
        self.assertNotIn("Cebolla", nombres_ingredientes)
        self.assertIn("Ajo", nombres_ingredientes)

    def test_eliminar_ingrediente_primero_de_la_lista(self):
        # Crear ingredientes
        ing1 = self._crear_ingrediente("Primero", "g", 100, "Tienda1")
        ing2 = self._crear_ingrediente("Segundo", "g", 200, "Tienda2")
        ing3 = self._crear_ingrediente("Tercero", "g", 300, "Tienda3")
        session.commit()

        # Eliminar el primer ingrediente (índice 0)
        resultado = self.logica.eliminar_ingrediente(0)
        self.assertTrue(resultado)

        # Verificar que se eliminó el correcto
        ingredientes = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes), 2)

        nombres_ingredientes = {ing["nombre"] for ing in ingredientes}
        self.assertNotIn("Primero", nombres_ingredientes)
        self.assertIn("Segundo", nombres_ingredientes)
        self.assertIn("Tercero", nombres_ingredientes)

    def test_eliminar_ingrediente_ultimo_de_la_lista(self):
        # Crear ingredientes
        ing1 = self._crear_ingrediente("Primero", "g", 100, "Tienda1")
        ing2 = self._crear_ingrediente("Segundo", "g", 200, "Tienda2")
        ing3 = self._crear_ingrediente("Tercero", "g", 300, "Tienda3")
        session.commit()

        # Eliminar el último ingrediente (índice 2)
        resultado = self.logica.eliminar_ingrediente(2)
        self.assertTrue(resultado)

        # Verificar que se eliminó el correcto
        ingredientes = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes), 2)

        nombres_ingredientes = {ing["nombre"] for ing in ingredientes}
        self.assertIn("Primero", nombres_ingredientes)
        self.assertIn("Segundo", nombres_ingredientes)
        self.assertNotIn("Tercero", nombres_ingredientes)

    def test_eliminar_ingrediente_indice_fuera_de_rango(self):
        # Crear un ingrediente
        self._crear_ingrediente("Solo", "unidad", 100, "Tienda")
        session.commit()

        # Intentar eliminar con índice fuera de rango
        # Debe retornar False para índices inválidos
        resultado1 = self.logica.eliminar_ingrediente(5)  # Índice inexistente
        resultado2 = self.logica.eliminar_ingrediente(-1)  # Índice negativo
        self.assertFalse(resultado1)
        self.assertFalse(resultado2)

        # Verificar que el ingrediente sigue ahí
        ingredientes = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes), 1)
        self.assertEqual(ingredientes[0]["nombre"], "Solo")

    def test_eliminar_ingrediente_lista_vacia(self):
        # Sin ingredientes, intentar eliminar
        resultado = self.logica.eliminar_ingrediente(0)
        self.assertFalse(resultado)  # Debe retornar False

        # No debe lanzar excepción
        ingredientes = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes), 0)

    def test_eliminar_ingrediente_actualiza_indices(self):
        # Crear varios ingredientes
        ingredientes_nombres = []
        for i in range(5):
            nombre = f"Ingrediente_{i}"
            self._crear_ingrediente(nombre, "g", 100 * i, f"Tienda_{i}")
            ingredientes_nombres.append(nombre)
        session.commit()

        # Eliminar el ingrediente del medio (índice 2)
        resultado = self.logica.eliminar_ingrediente(2)
        self.assertTrue(resultado)

        # Verificar que los índices se actualizaron correctamente
        ingredientes = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes), 4)

        # Los ingredientes restantes deben ser: 0, 1, 3, 4 (originales)
        nombres_restantes = {ing["nombre"] for ing in ingredientes}
        self.assertIn("Ingrediente_0", nombres_restantes)
        self.assertIn("Ingrediente_1", nombres_restantes)
        self.assertNotIn("Ingrediente_2", nombres_restantes)  # Eliminado
        self.assertIn("Ingrediente_3", nombres_restantes)
        self.assertIn("Ingrediente_4", nombres_restantes)

    def test_eliminar_ingrediente_multiples_eliminaciones(self):
        # Crear ingredientes
        for i in range(6):
            self._crear_ingrediente(f"Ing_{i}", "g", 100 * i, f"Tienda_{i}")
        session.commit()

        # Eliminar varios ingredientes en orden
        resultado1 = self.logica.eliminar_ingrediente(1)  # Elimina Ing_1
        resultado2 = self.logica.eliminar_ingrediente(
            2
        )  # Ahora elimina Ing_3 (porque los índices se actualizaron)
        resultado3 = self.logica.eliminar_ingrediente(0)  # Ahora elimina Ing_0
        self.assertTrue(resultado1)
        self.assertTrue(resultado2)
        self.assertTrue(resultado3)

        # Verificar ingredientes restantes
        ingredientes = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes), 3)

        nombres_restantes = {ing["nombre"] for ing in ingredientes}
        self.assertNotIn("Ing_0", nombres_restantes)  # Eliminado
        self.assertNotIn("Ing_1", nombres_restantes)  # Eliminado
        self.assertIn("Ing_2", nombres_restantes)  # Restante
        self.assertNotIn("Ing_3", nombres_restantes)  # Eliminado
        self.assertIn("Ing_4", nombres_restantes)  # Restante
        self.assertIn("Ing_5", nombres_restantes)  # Restante

    def test_eliminar_ingrediente_unico_ingrediente(self):
        # Crear un solo ingrediente
        self._crear_ingrediente("Unico", "unidad", 500, "Tienda")
        session.commit()

        # Eliminar el único ingrediente
        resultado = self.logica.eliminar_ingrediente(0)
        self.assertTrue(resultado)

        # Verificar que la lista queda vacía
        ingredientes = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes), 0)

    def test_eliminar_ingrediente_no_afecta_recetas(self):
        # Crear receta e ingrediente
        receta = self._crear_receta("Sopa", "01:00:00", 4, 200, "Hervir")
        ingrediente = self._crear_ingrediente("Sal", "cucharada", 50, "Cocina")
        session.commit()

        # Agregar ingrediente a la receta
        receta_dict = self.logica.dar_receta(0)
        ingrediente_dict = self.logica.dar_ingrediente(0)
        resultado_agregar = self.logica.agregar_ingrediente_receta(
            receta_dict, ingrediente_dict, "1"
        )
        self.assertTrue(resultado_agregar)

        # Verificar que el ingrediente está en la receta
        ingredientes_receta = self.logica.dar_ingredientes_receta(0)
        self.assertEqual(len(ingredientes_receta), 1)

        # Eliminar el ingrediente de la lista general
        resultado_eliminar = self.logica.eliminar_ingrediente(0)
        self.assertTrue(resultado_eliminar)

        # Verificar que se eliminó de la lista general
        ingredientes_generales = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes_generales), 0)

        # Verificar que la receta sigue existiendo
        recetas = self.logica.dar_recetas()
        self.assertEqual(len(recetas), 1)

        # Verificar que el ingrediente se eliminó también de la receta (cascade delete)
        ingredientes_receta_finales = self.logica.dar_ingredientes_receta(0)
        self.assertEqual(len(ingredientes_receta_finales), 0)

    def test_eliminar_ingrediente_con_datos_especiales(self):
        # Crear ingredientes con datos especiales
        self._crear_ingrediente(
            "Ingrediente con nombre muy largo", "kg", 0, "Tienda 'Especial' & Cía."
        )
        self._crear_ingrediente("Normal", "g", 1000, "Tienda Normal")
        self._crear_ingrediente("Último", "ml", 500, "Tienda Final")
        session.commit()

        # Eliminar el del medio (índice 1)
        resultado = self.logica.eliminar_ingrediente(1)
        self.assertTrue(resultado)

        # Verificar que se eliminó el correcto
        ingredientes = self.logica.dar_ingredientes()
        self.assertEqual(len(ingredientes), 2)

        nombres_restantes = {ing["nombre"] for ing in ingredientes}
        self.assertIn("Ingrediente con nombre muy largo", nombres_restantes)
        self.assertNotIn("Normal", nombres_restantes)  # Eliminado
        self.assertIn("Último", nombres_restantes)
        

if __name__ == "__main__":
    unittest.main()
