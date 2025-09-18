import unittest
from faker import Faker

from src.logica.LogicaRecetario import LogicaRecetario
from src.modelo.declarative_base import session
from src.modelo.receta import Receta


class TestRecetas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faker = Faker("es_ES")

    def setUp(self):
        session.query(Receta).delete()
        session.commit()

        self.logica = LogicaRecetario()

    def tearDown(self):
        session.rollback()

    # -------------------- crear_receta --------------------

    def test_crear_receta_exitoso(self):
        nombre = self.faker.unique.word().capitalize()
        tiempo = "01:30:00"
        personas = "5"
        calorias = "320"
        preparacion = self.faker.sentence(nb_words=8)

        total_antes = len(self.logica.dar_recetas())
        ok = self.logica.crear_receta(nombre, tiempo, personas, calorias, preparacion)

        self.assertTrue(ok)
        recetas = self.logica.dar_recetas()
        self.assertEqual(len(recetas), total_antes + 1)

        nueva = recetas[-1]
        self.assertEqual(nueva["nombre"], nombre)
        self.assertEqual(nueva["tiempo"], tiempo)
        self.assertEqual(nueva["personas"], int(personas))
        self.assertEqual(nueva["calorias"], int(calorias))
        self.assertEqual(nueva["preparacion"], preparacion)

    def test_crear_receta_valida_campos_minimos(self):
        self.assertFalse(self.logica.crear_receta("", "00:10:00", "1", "0", "Paso 1"))
        self.assertFalse(
            self.logica.crear_receta(self.faker.word(), "", "1", "10", "Paso 1")
        )
        self.assertFalse(
            self.logica.crear_receta(self.faker.word(), "00:20:00", "0", "10", "Paso 1")
        )
        self.assertFalse(
            self.logica.crear_receta(
                self.faker.word(), "00:20:00", "-2", "10", "Paso 1"
            )
        )
        self.assertFalse(
            self.logica.crear_receta(self.faker.word(), "00:20:00", "1", "-1", "Paso 1")
        )
        self.assertFalse(
            self.logica.crear_receta(self.faker.word(), "00:20:00", "1", "10", "")
        )

        self.assertEqual(len(self.logica.dar_recetas()), 0)

    def test_crear_receta_trimea_campos(self):
        base_nombre = self.faker.unique.word().capitalize()
        base_prep = self.faker.sentence()
        ok = self.logica.crear_receta(
            f"  {base_nombre}  ", "00:30:00", "2", "100", f"  {base_prep}  "
        )
        self.assertTrue(ok)
        receta = self.logica.dar_recetas()[-1]
        self.assertEqual(receta["nombre"], base_nombre)
        self.assertEqual(receta["preparacion"], base_prep)

    def test_crear_receta_rechaza_duplicado_mismo_caso(self):
        nombre = self.faker.unique.word().capitalize()
        self.assertTrue(
            self.logica.crear_receta(nombre, "00:20:00", "2", "50", "Paso 1")
        )
        self.assertFalse(
            self.logica.crear_receta(nombre, "00:25:00", "3", "60", "Paso 2")
        )
        recetas = self.logica.dar_recetas()
        self.assertEqual(sum(1 for r in recetas if r["nombre"] == nombre), 1)

    # -------------------- dar_receta --------------------

    def test_dar_receta_devuelve_la_receta_correcta_por_indice(self):
        datos = []
        for _ in range(3):
            nombre = self.faker.unique.word().capitalize()
            tiempo = "00:{:02d}:00".format(self.faker.random_int(min=5, max=59))
            personas = str(self.faker.random_int(min=1, max=8))
            calorias = str(self.faker.random_int(min=0, max=700))
            preparacion = self.faker.sentence()
            self.assertTrue(
                self.logica.crear_receta(
                    nombre, tiempo, personas, calorias, preparacion
                )
            )
            datos.append((nombre, tiempo, int(personas), int(calorias), preparacion))

        for idx, (nombre, tiempo, personas, calorias, preparacion) in enumerate(datos):
            receta = self.logica.dar_receta(idx)
            self.assertIsInstance(receta, dict)
            self.assertEqual(receta["nombre"], nombre)
            self.assertEqual(receta["tiempo"], tiempo)
            self.assertEqual(receta["personas"], personas)
            self.assertEqual(receta["calorias"], calorias)
            self.assertEqual(receta["preparacion"], preparacion)

    def test_dar_receta_indice_fuera_de_rango_devuelve_none(self):
        self.assertIsNone(self.logica.dar_receta(0))
        self.assertTrue(
            self.logica.crear_receta(self.faker.word(), "00:10:00", "1", "10", "Paso 1")
        )
        self.assertIsNotNone(self.logica.dar_receta(0))
        self.assertIsNone(self.logica.dar_receta(1))

    # -------------------- dar_preparacion --------------------

    def test_dar_preparacion_receta_existente_devuelve_datos_correctos(self):
        # Crear una receta con ingredientes
        nombre_receta = "Sopa de Pollo"
        tiempo = "01:30:00"
        personas_originales = 4
        calorias = 250
        preparacion = "Hervir pollo con verduras por 1 hora"

        self.assertTrue(
            self.logica.crear_receta(
                nombre_receta, tiempo, personas_originales, calorias, preparacion
            )
        )

        # Crear ingredientes
        ingrediente1 = self.logica.crear_ingrediente(
            "Pollo", "libra", 8000, "Carnicería"
        )
        ingrediente2 = self.logica.crear_ingrediente(
            "Cebolla", "unidad", 500, "Mercado"
        )

        # Agregar ingredientes a la receta
        receta_dict = self.logica.dar_receta(0)
        ingrediente1_dict = self.logica.dar_ingrediente(0)
        ingrediente2_dict = self.logica.dar_ingrediente(1)

        self.assertTrue(
            self.logica.agregar_ingrediente_receta(receta_dict, ingrediente1_dict, "2")
        )
        self.assertTrue(
            self.logica.agregar_ingrediente_receta(receta_dict, ingrediente2_dict, "1")
        )

        # Solicitar preparación para 6 personas
        cantidad_personas = 6
        preparacion_data = self.logica.dar_preparacion(0, cantidad_personas)

        # Verificar estructura del diccionario
        self.assertIsInstance(preparacion_data, dict)
        self.assertIn("receta", preparacion_data)
        self.assertIn("personas", preparacion_data)
        self.assertIn("calorias", preparacion_data)
        self.assertIn("costo", preparacion_data)
        self.assertIn("tiempo_preparacion", preparacion_data)
        self.assertIn("datos_ingredientes", preparacion_data)

        # Verificar datos básicos
        self.assertEqual(preparacion_data["receta"], nombre_receta)
        self.assertEqual(preparacion_data["personas"], cantidad_personas)

        # Verificar que las calorías se escalan correctamente
        factor_escalamiento = cantidad_personas / personas_originales
        calorias_esperadas = int(calorias * factor_escalamiento)
        self.assertEqual(preparacion_data["calorias"], calorias_esperadas)

        # Verificar ingredientes escalados
        self.assertIsInstance(preparacion_data["datos_ingredientes"], list)
        self.assertEqual(len(preparacion_data["datos_ingredientes"]), 2)

        # Verificar primer ingrediente (Pollo)
        pollo_data = preparacion_data["datos_ingredientes"][0]
        self.assertEqual(pollo_data["nombre"], "Pollo")
        self.assertEqual(pollo_data["unidad"], "libra")
        self.assertEqual(pollo_data["cantidad"], "3.0")  # 2 * (6/4) = 3.0
        self.assertEqual(pollo_data["valor"], 24000)  # 8000 * 3.0

        # Verificar segundo ingrediente (Cebolla)
        cebolla_data = preparacion_data["datos_ingredientes"][1]
        self.assertEqual(cebolla_data["nombre"], "Cebolla")
        self.assertEqual(cebolla_data["unidad"], "unidad")
        self.assertEqual(cebolla_data["cantidad"], "1.5")  # 1 * (6/4) = 1.5
        self.assertEqual(cebolla_data["valor"], 750)  # 500 * 1.5

    def test_dar_preparacion_receta_sin_ingredientes(self):
        # Crear una receta sin ingredientes
        nombre_receta = "Receta Simple"
        tiempo = "00:30:00"
        personas_originales = 2
        calorias = 100
        preparacion = "Solo seguir instrucciones"

        self.assertTrue(
            self.logica.crear_receta(
                nombre_receta, tiempo, personas_originales, calorias, preparacion
            )
        )

        # Solicitar preparación para 4 personas
        cantidad_personas = 4
        preparacion_data = self.logica.dar_preparacion(0, cantidad_personas)

        # Verificar estructura básica
        self.assertIsInstance(preparacion_data, dict)
        self.assertEqual(preparacion_data["receta"], nombre_receta)
        self.assertEqual(preparacion_data["personas"], cantidad_personas)

        # Verificar que las calorías se escalan
        factor_escalamiento = cantidad_personas / personas_originales
        calorias_esperadas = int(calorias * factor_escalamiento)
        self.assertEqual(preparacion_data["calorias"], calorias_esperadas)

        # Verificar que no hay ingredientes
        self.assertIsInstance(preparacion_data["datos_ingredientes"], list)
        self.assertEqual(len(preparacion_data["datos_ingredientes"]), 0)

        # Verificar que el costo es 0
        self.assertEqual(preparacion_data["costo"], 0)

    def test_dar_preparacion_indice_receta_fuera_de_rango(self):
        # Sin recetas, cualquier índice debe devolver None o estructura vacía
        preparacion_data = self.logica.dar_preparacion(0, 4)
        self.assertIsNone(preparacion_data)

        # Crear una receta
        self.assertTrue(self.logica.crear_receta("Test", "00:10:00", "2", "50", "Test"))

        # Índice válido debe funcionar
        preparacion_data = self.logica.dar_preparacion(0, 4)
        self.assertIsNotNone(preparacion_data)

        # Índice fuera de rango debe devolver None
        preparacion_data = self.logica.dar_preparacion(5, 4)
        self.assertIsNone(preparacion_data)

        preparacion_data = self.logica.dar_preparacion(-1, 4)
        self.assertIsNone(preparacion_data)

    def test_dar_preparacion_cantidad_personas_negativa_o_cero(self):
        # Crear una receta
        self.assertTrue(self.logica.crear_receta("Test", "00:10:00", "2", "50", "Test"))

        # Cantidad de personas negativa
        preparacion_data = self.logica.dar_preparacion(0, -2)
        self.assertIsNone(preparacion_data)

        # Cantidad de personas cero
        preparacion_data = self.logica.dar_preparacion(0, 0)
        self.assertIsNone(preparacion_data)

    def test_dar_preparacion_escalamiento_correcto_ingredientes(self):
        # Crear receta con ingredientes específicos
        self.assertTrue(
            self.logica.crear_receta("Pasta", "00:20:00", "3", "300", "Cocinar pasta")
        )

        # Crear ingredientes con valores específicos
        self.logica.crear_ingrediente("Pasta", "libra", 3000, "Supermercado")
        self.logica.crear_ingrediente("Tomate", "libra", 2000, "Mercado")

        # Agregar ingredientes a la receta
        receta_dict = self.logica.dar_receta(0)
        pasta_dict = self.logica.dar_ingrediente(0)
        tomate_dict = self.logica.dar_ingrediente(1)

        self.logica.agregar_ingrediente_receta(receta_dict, pasta_dict, "1.5")
        self.logica.agregar_ingrediente_receta(receta_dict, tomate_dict, "2")

        # Solicitar preparación para 9 personas (factor de escalamiento: 9/3 = 3)
        preparacion_data = self.logica.dar_preparacion(0, 9)

        # Verificar escalamiento de ingredientes
        ingredientes = preparacion_data["datos_ingredientes"]

        # Pasta: 1.5 * 3 = 4.5
        pasta_data = next(ing for ing in ingredientes if ing["nombre"] == "Pasta")
        self.assertEqual(pasta_data["cantidad"], "4.5")
        self.assertEqual(pasta_data["valor"], 13500)  # 3000 * 4.5

        # Tomate: 2 * 3 = 6
        tomate_data = next(ing for ing in ingredientes if ing["nombre"] == "Tomate")
        self.assertEqual(tomate_data["cantidad"], "6.0")
        self.assertEqual(tomate_data["valor"], 12000)  # 2000 * 6

    def test_dar_preparacion_calculo_costo_total(self):
        # Crear receta con ingredientes
        self.assertTrue(
            self.logica.crear_receta(
                "Ensalada", "00:15:00", "2", "150", "Mezclar ingredientes"
            )
        )

        # Crear ingredientes con valores específicos
        self.logica.crear_ingrediente("Lechuga", "libra", 1000, "Verdulería")
        self.logica.crear_ingrediente("Tomate", "libra", 2000, "Verdulería")
        self.logica.crear_ingrediente("Aceite", "ml", 500, "Supermercado")

        # Agregar ingredientes a la receta
        receta_dict = self.logica.dar_receta(0)
        lechuga_dict = self.logica.dar_ingrediente(0)
        tomate_dict = self.logica.dar_ingrediente(1)
        aceite_dict = self.logica.dar_ingrediente(2)

        self.logica.agregar_ingrediente_receta(receta_dict, lechuga_dict, "1")
        self.logica.agregar_ingrediente_receta(receta_dict, tomate_dict, "0.5")
        self.logica.agregar_ingrediente_receta(receta_dict, aceite_dict, "50")

        # Solicitar preparación para 6 personas (factor: 6/2 = 3)
        preparacion_data = self.logica.dar_preparacion(0, 6)

        # Calcular costo esperado
        # Lechuga: 1 * 3 * 1000 = 3000
        # Tomate: 0.5 * 3 * 2000 = 3000
        # Aceite: 50 * 3 * 500 = 75000
        # Total: 3000 + 3000 + 75000 = 81000
        costo_esperado = 81000
        self.assertEqual(preparacion_data["costo"], costo_esperado)

    def test_dar_preparacion_tiempo_preparacion_escalado(self):
        # Crear receta con tiempo específico
        tiempo_original = "01:30:00"  # 1 hora 30 minutos
        self.assertTrue(
            self.logica.crear_receta(
                "Estofado", tiempo_original, "4", "400", "Cocinar lentamente"
            )
        )

        # Solicitar preparación para 8 personas (factor: 8/4 = 2)
        preparacion_data = self.logica.dar_preparacion(0, 8)

        # El tiempo de preparación debería escalarse
        # 1:30:00 * 2 = 3:00:00
        tiempo_esperado = "03:00:00"
        self.assertEqual(preparacion_data["tiempo_preparacion"], tiempo_esperado)

    def test_dar_preparacion_con_ingredientes_decimales(self):
        # Crear receta
        self.assertTrue(
            self.logica.crear_receta("Sopa", "00:45:00", "5", "200", "Hervir")
        )

        # Crear ingrediente
        self.logica.crear_ingrediente("Sal", "cucharada", 100, "Cocina")

        # Agregar ingrediente con cantidad decimal
        receta_dict = self.logica.dar_receta(0)
        sal_dict = self.logica.dar_ingrediente(0)
        self.logica.agregar_ingrediente_receta(receta_dict, sal_dict, "1.5")

        # Solicitar preparación para 7 personas (factor: 7/5 = 1.4)
        preparacion_data = self.logica.dar_preparacion(0, 7)

        # Verificar escalamiento decimal
        sal_data = preparacion_data["datos_ingredientes"][0]
        cantidad_esperada = 1.5 * (7 / 5)  # 2.1
        self.assertEqual(sal_data["cantidad"], "2.1")
        self.assertEqual(sal_data["valor"], 210)  # 100 * 2.1

    def test_dar_preparacion_estructura_completa_datos(self):
        # Crear receta completa
        self.assertTrue(
            self.logica.crear_receta("Pizza", "00:30:00", "3", "500", "Hornear")
        )

        # Crear múltiples ingredientes
        ingredientes_data = [
            ("Harina", "libra", 2000, "Supermercado"),
            ("Queso", "libra", 8000, "Lácteos"),
            ("Tomate", "libra", 3000, "Verdulería"),
            ("Aceitunas", "libra", 5000, "Delicatessen"),
        ]

        for nombre, unidad, valor, sitio in ingredientes_data:
            self.logica.crear_ingrediente(nombre, unidad, valor, sitio)

        # Agregar todos los ingredientes a la receta
        receta_dict = self.logica.dar_receta(0)
        for i, (nombre, _, _, _) in enumerate(ingredientes_data):
            ingrediente_dict = self.logica.dar_ingrediente(i)
            self.logica.agregar_ingrediente_receta(
                receta_dict, ingrediente_dict, str(i + 1)
            )

        # Solicitar preparación para 6 personas
        preparacion_data = self.logica.dar_preparacion(0, 6)

        # Verificar estructura completa
        claves_esperadas = {
            "receta",
            "personas",
            "calorias",
            "costo",
            "tiempo_preparacion",
            "datos_ingredientes",
        }
        self.assertEqual(set(preparacion_data.keys()), claves_esperadas)

        # Verificar tipos de datos
        self.assertIsInstance(preparacion_data["receta"], str)
        self.assertIsInstance(preparacion_data["personas"], int)
        self.assertIsInstance(preparacion_data["calorias"], int)
        self.assertIsInstance(preparacion_data["costo"], int)
        self.assertIsInstance(preparacion_data["tiempo_preparacion"], str)
        self.assertIsInstance(preparacion_data["datos_ingredientes"], list)

        # Verificar que hay 4 ingredientes
        self.assertEqual(len(preparacion_data["datos_ingredientes"]), 4)

        # Verificar estructura de cada ingrediente
        for ingrediente in preparacion_data["datos_ingredientes"]:
            claves_ingrediente = {"nombre", "unidad", "cantidad", "valor"}
            self.assertEqual(set(ingrediente.keys()), claves_ingrediente)
            self.assertIsInstance(ingrediente["nombre"], str)
            self.assertIsInstance(ingrediente["unidad"], str)
            self.assertIsInstance(ingrediente["cantidad"], str)
            self.assertIsInstance(ingrediente["valor"], int)


if __name__ == "__main__":
    unittest.main()
