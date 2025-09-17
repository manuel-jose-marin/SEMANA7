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
            self.assertTrue(self.logica.crear_receta(nombre, tiempo, personas, calorias, preparacion))
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
        self.assertTrue(self.logica.crear_receta(self.faker.word(), "00:10:00", "1", "10", "Paso 1"))
        self.assertIsNotNone(self.logica.dar_receta(0))
        self.assertIsNone(self.logica.dar_receta(1))

if __name__ == "__main__":
    unittest.main()
