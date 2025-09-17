import unittest
from faker import Faker

from src.logica.LogicaRecetario import LogicaRecetario
from src.modelo.declarative_base import session
from src.modelo.receta import Receta
from src.modelo.ingrediente import Ingrediente
from src.modelo.ingrediente_receta import IngredienteReceta

class TestListarIngredientesReceta(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.faker = Faker("es_ES")
        cls.logica = LogicaRecetario()

    def setUp(self):
        # Aislar: limpiar tablas en orden FK
        session.query(IngredienteReceta).delete()
        session.query(Ingrediente).delete()
        session.query(Receta).delete()
        session.commit()

    def tearDown(self):
        session.rollback()

    # ---------- Helpers ----------
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
        session.flush()  # asegura r.id
        return r

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

    def _asociar(self, receta_id, ingrediente_id, cantidad: str):
        link = IngredienteReceta(
            receta_id=receta_id,
            ingrediente_id=ingrediente_id,
            cantidad=str(cantidad),  # la columna es String
        )
        session.add(link)
        session.flush()
        return link

    def _indice_receta_por_nombre(self, nombre):

        recetas = session.query(Receta).all()
        for i, r in enumerate(recetas):
            if r.nombre == nombre:
                return i
        return None

    # ---------- Casos ----------

    def test_receta_sin_ingredientes_devuelve_lista_vacia(self):
        r = self._crear_receta()
        session.commit()
        idx = self._indice_receta_por_nombre(r.nombre)
        result = self.logica.dar_ingredientes_receta(idx)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_indice_inexistente_devuelve_lista_vacia(self):
        # sin recetas
        self.assertEqual(self.logica.dar_ingredientes_receta(0), [])
        # con una receta, pedir un índice fuera de rango
        r = self._crear_receta()
        session.commit()
        self.assertNotEqual(self._indice_receta_por_nombre(r.nombre), None)
        self.assertEqual(self.logica.dar_ingredientes_receta(9999), [])

    def test_listar_devuelve_nombre_unidad_y_cantidad(self):
        r = self._crear_receta()
        ing1 = self._crear_ingrediente(unidad="g")
        ing2 = self._crear_ingrediente(unidad="ml")
        self._asociar(r.id, ing1.id, "250")
        self._asociar(r.id, ing2.id, "100")
        session.commit()

        idx = self._indice_receta_por_nombre(r.nombre)
        data = self.logica.dar_ingredientes_receta(idx)

        self.assertEqual(len(data), 2)
        por_nombre = {d["ingrediente"]: d for d in data}

        self.assertIn(ing1.nombre, por_nombre)
        self.assertIn(ing2.nombre, por_nombre)

        self.assertEqual(por_nombre[ing1.nombre]["receta"], r.nombre)
        self.assertEqual(por_nombre[ing1.nombre]["unidad"], "g")
        self.assertEqual(por_nombre[ing1.nombre]["cantidad"], "250")

        self.assertEqual(por_nombre[ing2.nombre]["receta"], r.nombre)
        self.assertEqual(por_nombre[ing2.nombre]["unidad"], "ml")
        self.assertEqual(por_nombre[ing2.nombre]["cantidad"], "100")

        # tipos básicos
        for item in data:
            self.assertTrue(isinstance(item["receta"], str) and item["receta"])
            self.assertTrue(
                isinstance(item["ingrediente"], str) and item["ingrediente"]
            )
            self.assertTrue(isinstance(item["unidad"], str) and item["unidad"])
            self.assertTrue(isinstance(item["cantidad"], str))  # cantidad es STRING

    def test_no_incluye_ingredientes_de_otras_recetas(self):
        # Receta A con 1 ingrediente
        ra = self._crear_receta()
        ia = self._crear_ingrediente(unidad="unidad")
        self._asociar(ra.id, ia.id, "3")

        # Receta B con 2 ingredientes
        rb = self._crear_receta()
        ib1 = self._crear_ingrediente(unidad="g")
        ib2 = self._crear_ingrediente(unidad="ml")
        self._asociar(rb.id, ib1.id, "50")
        self._asociar(rb.id, ib2.id, "20")
        session.commit()

        idx_a = self._indice_receta_por_nombre(ra.nombre)
        idx_b = self._indice_receta_por_nombre(rb.nombre)

        data_b = self.logica.dar_ingredientes_receta(idx_b)
        nombres_b = {d["ingrediente"] for d in data_b}
        self.assertEqual(len(data_b), 2)
        self.assertIn(ib1.nombre, nombres_b)
        self.assertIn(ib2.nombre, nombres_b)
        self.assertNotIn(ia.nombre, nombres_b)

        data_a = self.logica.dar_ingredientes_receta(idx_a)
        self.assertEqual(len(data_a), 1)
        self.assertEqual(data_a[0]["ingrediente"], ia.nombre)
        self.assertEqual(data_a[0]["unidad"], "unidad")
        self.assertEqual(data_a[0]["cantidad"], "3")

    # ---------- Casos para agregar_ingrediente_receta --------------------

    def test_agregar_ingrediente_receta_exitoso(self):
        # Crear receta e ingrediente
        receta = self._crear_receta("Pasta", "00:30:00", 4, 300, "Cocinar pasta")
        ingrediente = self._crear_ingrediente("Tomate", "unidad", 500, "Mercado")
        session.commit()

        # Obtener los objetos como diccionarios para la lógica
        receta_dict = self.logica.dar_receta(0)
        ingrediente_dict = self.logica.dar_ingrediente(0)
        cantidad = "2"

        # Verificar que inicialmente no hay ingredientes en la receta
        ingredientes_iniciales = self.logica.dar_ingredientes_receta(0)
        self.assertEqual(len(ingredientes_iniciales), 0)

        # Agregar ingrediente a la receta
        resultado = self.logica.agregar_ingrediente_receta(
            receta_dict, ingrediente_dict, cantidad
        )
        self.assertTrue(resultado)  # Debe retornar True si fue exitoso

        # Verificar que se agregó correctamente
        ingredientes_finales = self.logica.dar_ingredientes_receta(0)
        self.assertEqual(len(ingredientes_finales), 1)

        ingrediente_agregado = ingredientes_finales[0]
        self.assertEqual(ingrediente_agregado["receta"], "Pasta")
        self.assertEqual(ingrediente_agregado["ingrediente"], "Tomate")
        self.assertEqual(ingrediente_agregado["unidad"], "unidad")
        self.assertEqual(ingrediente_agregado["cantidad"], "2")

    def test_agregar_ingrediente_receta_multiples_ingredientes(self):
        # Crear receta
        receta = self._crear_receta(
            "Ensalada", "00:15:00", 2, 150, "Mezclar ingredientes"
        )
        session.commit()
        receta_dict = self.logica.dar_receta(0)

        # Crear varios ingredientes
        ingredientes = []
        for i in range(3):
            ing = self._crear_ingrediente(
                f"Ingrediente_{i}", "g", 100 * (i + 1), f"Tienda_{i}"
            )
            ingredientes.append(self.logica.dar_ingrediente(i))

        session.commit()

        # Agregar todos los ingredientes a la receta
        cantidades = ["100", "200", "150"]
        for i, (ing, cantidad) in enumerate(zip(ingredientes, cantidades)):
            resultado = self.logica.agregar_ingrediente_receta(
                receta_dict, ing, cantidad
            )
            self.assertTrue(resultado)  # Debe retornar True si fue exitoso

        # Verificar que se agregaron todos
        ingredientes_finales = self.logica.dar_ingredientes_receta(0)
        self.assertEqual(len(ingredientes_finales), 3)

        # Verificar cada ingrediente
        for i, ingrediente in enumerate(ingredientes_finales):
            self.assertEqual(ingrediente["receta"], "Ensalada")
            self.assertEqual(ingrediente["ingrediente"], f"Ingrediente_{i}")
            self.assertEqual(ingrediente["unidad"], "g")
            self.assertEqual(ingrediente["cantidad"], cantidades[i])

    def test_agregar_ingrediente_receta_misma_receta_diferentes_ingredientes(self):
        # Crear receta
        receta = self._crear_receta("Sopa", "01:00:00", 6, 200, "Hervir ingredientes")
        session.commit()
        receta_dict = self.logica.dar_receta(0)

        # Crear ingredientes
        ing1 = self._crear_ingrediente("Cebolla", "unidad", 300, "Mercado")
        ing2 = self._crear_ingrediente("Zanahoria", "unidad", 400, "Mercado")
        session.commit()

        ing1_dict = self.logica.dar_ingrediente(0)
        ing2_dict = self.logica.dar_ingrediente(1)

        # Agregar ambos ingredientes
        resultado1 = self.logica.agregar_ingrediente_receta(receta_dict, ing1_dict, "1")
        resultado2 = self.logica.agregar_ingrediente_receta(receta_dict, ing2_dict, "2")
        self.assertTrue(resultado1)
        self.assertTrue(resultado2)

        # Verificar que ambos están en la receta
        ingredientes = self.logica.dar_ingredientes_receta(0)
        self.assertEqual(len(ingredientes), 2)

        nombres_ingredientes = {ing["ingrediente"] for ing in ingredientes}
        self.assertIn("Cebolla", nombres_ingredientes)
        self.assertIn("Zanahoria", nombres_ingredientes)

    def test_agregar_ingrediente_receta_cantidad_string(self):
        # Crear receta e ingrediente
        receta = self._crear_receta("Postre", "00:45:00", 4, 400, "Hornear")
        ingrediente = self._crear_ingrediente("Azúcar", "taza", 2000, "Supermercado")
        session.commit()

        receta_dict = self.logica.dar_receta(0)
        ingrediente_dict = self.logica.dar_ingrediente(0)

        # Probar diferentes formatos de cantidad como string (solo números válidos)
        cantidades = ["1", "1.5", "2.5", "0.25", "0.5", "1.0"]

        for cantidad in cantidades:
            # Limpiar ingredientes anteriores
            session.query(IngredienteReceta).delete()
            session.commit()

            # Agregar con la cantidad actual
            resultado = self.logica.agregar_ingrediente_receta(
                receta_dict, ingrediente_dict, cantidad
            )
            self.assertTrue(resultado)

            # Verificar que se guardó correctamente
            ingredientes = self.logica.dar_ingredientes_receta(0)
            self.assertEqual(len(ingredientes), 1)
            self.assertEqual(ingredientes[0]["cantidad"], cantidad)

    def test_agregar_ingrediente_receta_no_afecta_otras_recetas(self):
        # Crear dos recetas
        receta1 = self._crear_receta("Receta A", "00:20:00", 2, 100, "Preparar A")
        receta2 = self._crear_receta("Receta B", "00:30:00", 3, 200, "Preparar B")
        session.commit()

        receta1_dict = self.logica.dar_receta(0)
        receta2_dict = self.logica.dar_receta(1)

        # Crear ingrediente
        ingrediente = self._crear_ingrediente("Sal", "cucharada", 50, "Cocina")
        session.commit()
        ingrediente_dict = self.logica.dar_ingrediente(0)

        # Agregar ingrediente solo a la primera receta
        resultado = self.logica.agregar_ingrediente_receta(
            receta1_dict, ingrediente_dict, "1"
        )
        self.assertTrue(resultado)

        # Verificar que solo está en la primera receta
        ingredientes_receta1 = self.logica.dar_ingredientes_receta(0)
        ingredientes_receta2 = self.logica.dar_ingredientes_receta(1)

        self.assertEqual(len(ingredientes_receta1), 1)
        self.assertEqual(len(ingredientes_receta2), 0)
        self.assertEqual(ingredientes_receta1[0]["receta"], "Receta A")

    def test_agregar_ingrediente_receta_ingrediente_duplicado(self):
        # Crear receta e ingrediente
        receta = self._crear_receta("Pizza", "00:45:00", 4, 500, "Hornear pizza")
        ingrediente = self._crear_ingrediente("Queso", "gramo", 100, "Lácteos")
        session.commit()

        receta_dict = self.logica.dar_receta(0)
        ingrediente_dict = self.logica.dar_ingrediente(0)

        # Agregar el mismo ingrediente dos veces
        resultado1 = self.logica.agregar_ingrediente_receta(
            receta_dict, ingrediente_dict, "100"
        )
        resultado2 = self.logica.agregar_ingrediente_receta(
            receta_dict, ingrediente_dict, "200"
        )
        self.assertTrue(resultado1)
        self.assertTrue(resultado2)

        # Verificar que solo hay una instancia (se actualiza la cantidad)
        ingredientes = self.logica.dar_ingredientes_receta(0)
        self.assertEqual(len(ingredientes), 1)

        # Debe tener la cantidad actualizada (la última)
        ingrediente_queso = ingredientes[0]
        self.assertEqual(ingrediente_queso["ingrediente"], "Queso")
        self.assertEqual(ingrediente_queso["cantidad"], "200")

    def test_agregar_ingrediente_receta_estructura_datos_correcta(self):
        # Crear receta e ingrediente
        receta = self._crear_receta("Torta", "01:30:00", 8, 600, "Hornear torta")
        ingrediente = self._crear_ingrediente("Harina", "taza", 1500, "Panadería")
        session.commit()

        receta_dict = self.logica.dar_receta(0)
        ingrediente_dict = self.logica.dar_ingrediente(0)
        cantidad = "3"

        # Agregar ingrediente
        resultado = self.logica.agregar_ingrediente_receta(
            receta_dict, ingrediente_dict, cantidad
        )
        self.assertTrue(resultado)

        # Verificar estructura del diccionario devuelto
        ingredientes = self.logica.dar_ingredientes_receta(0)
        self.assertEqual(len(ingredientes), 1)

        ingrediente_agregado = ingredientes[0]
        claves_esperadas = {"receta", "ingrediente", "unidad", "cantidad"}
        self.assertEqual(set(ingrediente_agregado.keys()), claves_esperadas)

        # Verificar tipos de datos
        self.assertIsInstance(ingrediente_agregado["receta"], str)
        self.assertIsInstance(ingrediente_agregado["ingrediente"], str)
        self.assertIsInstance(ingrediente_agregado["unidad"], str)
        self.assertIsInstance(ingrediente_agregado["cantidad"], str)

        # Verificar valores específicos
        self.assertEqual(ingrediente_agregado["receta"], "Torta")
        self.assertEqual(ingrediente_agregado["ingrediente"], "Harina")
        self.assertEqual(ingrediente_agregado["unidad"], "taza")
        self.assertEqual(ingrediente_agregado["cantidad"], "3")



if __name__ == "__main__":
    unittest.main()
    