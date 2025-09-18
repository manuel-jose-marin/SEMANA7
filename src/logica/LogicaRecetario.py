from src.modelo import engine, Base
from src.logica.FachadaRecetario import FachadaRecetario
from src.modelo import session, Receta, Ingrediente, IngredienteReceta


class LogicaRecetario(FachadaRecetario):

    def __init__(self):
        super().__init__()
        Base.metadata.create_all(engine)

    def dar_recetas(self):
        """Retorna la lista de recetas registradas en el sistema
        Retorna:
            (list): La lista con los objetos de recetas
        """
        recetas = session.query(Receta).all()
        recetas_dict = []
        for receta in recetas:
            receta_dict = {
                "nombre": receta.nombre,
                "tiempo": receta.tiempo_preparacion,
                "personas": receta.numero_personas,
                "calorias": receta.calorias_porcion,
                "preparacion": receta.preparacion,
            }
            recetas_dict.append(receta_dict)
        return recetas_dict

    def dar_receta(self, id_receta):
        """Retorna una receta a partir de su identificador
        Parámetros:
            id_receta (int): El identificador de la receta a retornar
        Retorna:
            (dict): La receta identificada con el id_receta recibido como parámetro
        """
        # Obtener todas las recetas y devolver la del índice especificado
        recetas = self.dar_recetas()
        if 0 <= id_receta < len(recetas):
            return recetas[id_receta]
        return None

    def validar_crear_editar_receta(
        self, id_receta, receta, tiempo, personas, calorias, preparacion
    ):
        """Valida que una receta se pueda crear o editar
        Parámetros:
            id_receta (int): El identificador de la receta (para edición)
            receta (string): El nombre de la receta
            tiempo (string): El tiempo de preparación de la receta
            personas (string): La cantidad de personas de la receta
            calorias (string): Calorías por porción
            preparacion (string): Proceso de preparación de la receta
        Retorna:
            (string): El mensaje de error generado al presentarse errores en la
            validación o una cadena de caracteres vacía si no hay errores.
        """
        # Validar que el nombre no esté vacío
        if not receta or receta.strip() == "":
            return "El nombre de la receta es obligatorio"

        # Validar que no exista otra receta con el mismo nombre (solo para creación)
        if id_receta == -1:  # Creación nueva
            busqueda = (
                session.query(Receta).filter(Receta.nombre == receta.strip()).first()
            )
            if busqueda:
                return "Ya existe una receta con ese nombre"

        # Validar tiempo de preparación
        if not tiempo or tiempo.strip() == "":
            return "El tiempo de preparación es obligatorio"

        # Validar número de personas
        try:
            personas_int = int(personas)
            if personas_int <= 0:
                return "El número de personas debe ser mayor a 0"
        except (ValueError, TypeError):
            return "El número de personas debe ser un número válido"

        # Validar calorías
        if calorias and calorias.strip():
            try:
                calorias_int = int(calorias)
                if calorias_int < 0:
                    return "Las calorías no pueden ser negativas"
            except (ValueError, TypeError):
                return "Las calorías deben ser un número válido"

        # Validar preparación
        if not preparacion or preparacion.strip() == "":
            return "Las instrucciones de preparación son obligatorias"

        return ""

    def crear_receta(self, receta, tiempo, personas, calorias, preparacion):
        """Crea una nueva receta
        Parámetros:
            receta (string): El nombre de la receta
            tiempo (string): El tiempo de preparación de la receta
            personas (string): La cantidad de personas de la receta
            calorias (string): Calorías por porción
            preparacion (string): Proceso de preparación de la receta
        """
        validacion = self.validar_crear_editar_receta(
            -1, receta, tiempo, personas, calorias, preparacion
        )
        if validacion == "":
            # Convertir parámetros a tipos apropiados
            personas_int = int(personas)
            calorias_int = int(calorias) if calorias and calorias.strip() else None

            nueva_receta = Receta(
                nombre=receta.strip(),
                tiempo_preparacion=tiempo.strip(),
                numero_personas=personas_int,
                calorias_porcion=calorias_int,
                preparacion=preparacion.strip(),
            )
            session.add(nueva_receta)
            session.commit()
            return True
        return False

    def dar_ingrediente(self, id_ingrediente):
        """Retorna un ingrediente a partir de su identificador
        Parámetros:
            id_ingrediente (int): El identificador del ingrediente a retornar
        Retorna:
            (dict): El ingrediente identificado con el id_ingrediente recibido como parámetro
        """
        # Obtener todos los ingredientes y devolver el del índice especificado
        ingredientes = self.dar_ingredientes()
        if 0 <= id_ingrediente < len(ingredientes):
            return ingredientes[id_ingrediente]
        return None

    def dar_ingredientes(self):
        """Retorna la lista de ingredientes
        Retorna:
            (list): La lista con los dict o los objetos de los ingredientes
        """
        ingredientes = session.query(Ingrediente).all()
        ingredientes_dict = []
        for ingrediente in ingredientes:
            ingrediente_dict = {
                "nombre": ingrediente.nombre,
                "unidad": ingrediente.unidad_medida,
                "valor": ingrediente.valor_unidad,
                "sitioCompra": ingrediente.sitio_compra,
            }
            ingredientes_dict.append(ingrediente_dict)
        return ingredientes_dict

    def dar_ingredientes_receta(self, id_receta):
        """Retorna el listado de ingredientes de una receta dado su índice
        Parámetros:
            id_receta (int): El índice de la receta en la lista
        Retorna:
            (list) : listado de ingredientes de la receta
        """
        # Obtener todas las recetas para encontrar la receta por índice
        recetas = session.query(Receta).all()
        if 0 <= id_receta < len(recetas):
            receta_obj = recetas[id_receta]

            # Obtener los ingredientes de esta receta
            ingredientes_receta = (
                session.query(IngredienteReceta)
                .filter(IngredienteReceta.receta_id == receta_obj.id)
                .all()
            )

            resultado = []
            for ingrediente_receta in ingredientes_receta:
                # Obtener los datos del ingrediente relacionado
                ingrediente = (
                    session.query(Ingrediente)
                    .filter(Ingrediente.id == ingrediente_receta.ingrediente_id)
                    .first()
                )
                if ingrediente:
                    ingrediente_dict = {
                        "receta": receta_obj.nombre,
                        "ingrediente": ingrediente.nombre,
                        "unidad": ingrediente.unidad_medida,
                        "cantidad": ingrediente_receta.cantidad,
                    }
                    resultado.append(ingrediente_dict)

            return resultado

        return []

    def validar_crear_editar_ingReceta(self, receta, ingrediente, cantidad):
        """Valida si se puede crear o editar un ingrediente de una receta
        Parámetros:
            receta: diccionario con datos de la receta
            ingrediente: diccionario con datos del ingrediente
            cantidad: cantidad del ingrediente para la receta
        Retorna:
            (string): El mensaje de error generado al presentarse errores en la
            validación o una cadena de caracteres vacía si no hay errores.
        """
        # Validar que la receta existe
        if not receta or "nombre" not in receta:
            return "La receta es obligatoria"

        # Validar que el ingrediente existe
        if not ingrediente or "nombre" not in ingrediente:
            return "El ingrediente es obligatorio"

        # Validar la cantidad
        if not cantidad or str(cantidad).strip() == "":
            return "La cantidad es obligatoria"

        try:
            cantidad_float = float(cantidad)
            if cantidad_float <= 0:
                return "La cantidad debe ser mayor a 0"
        except (ValueError, TypeError):
            return "La cantidad debe ser un número válido"

        return ""

    def agregar_ingrediente_receta(self, receta, ingrediente, cantidad):
        """Agregar el ingrediente a la receta con la cantidad
        Parámetros:
            receta: diccionario con datos de la receta
            ingrediente: diccionario con datos del ingrediente que se va a agregar
            cantidad: cantidad del ingrediente para la receta
        """
        validacion = self.validar_crear_editar_ingReceta(receta, ingrediente, cantidad)
        if validacion == "":
            # Buscar la receta en la base de datos por nombre
            receta_obj = (
                session.query(Receta).filter(Receta.nombre == receta["nombre"]).first()
            )
            if not receta_obj:
                return False

            # Buscar el ingrediente en la base de datos por nombre
            ingrediente_obj = (
                session.query(Ingrediente)
                .filter(Ingrediente.nombre == ingrediente["nombre"])
                .first()
            )
            if not ingrediente_obj:
                return False

            # Verificar si ya existe esta combinación de receta e ingrediente
            existente = (
                session.query(IngredienteReceta)
                .filter(
                    IngredienteReceta.receta_id == receta_obj.id,
                    IngredienteReceta.ingrediente_id == ingrediente_obj.id,
                )
                .first()
            )

            if existente:
                # Si ya existe, actualizar la cantidad
                existente.cantidad = str(cantidad)
            else:
                # Si no existe, crear nuevo registro
                nuevo_ingrediente_receta = IngredienteReceta(
                    receta_id=receta_obj.id,
                    ingrediente_id=ingrediente_obj.id,
                    cantidad=str(cantidad),
                )
                session.add(nuevo_ingrediente_receta)

            session.commit()
            return True
        return False

    def eliminar_ingrediente(self, id_ingrediente):
        """Elimina un ingrediente de la lista de ingredientes
        Parámetros:
            id_ingrediente (int): El índice del ingrediente que se desea eliminar
        """
        # Obtener todos los ingredientes para encontrar el ingrediente por índice
        ingredientes = session.query(Ingrediente).all()
        if 0 <= id_ingrediente < len(ingredientes):
            ingrediente_obj = ingredientes[id_ingrediente]

            # Primero eliminar todas las relaciones ingrediente-receta
            ingredientes_receta = (
                session.query(IngredienteReceta)
                .filter(IngredienteReceta.ingrediente_id == ingrediente_obj.id)
                .all()
            )
            for ingrediente_receta in ingredientes_receta:
                session.delete(ingrediente_receta)

            # Luego eliminar el ingrediente
            session.delete(ingrediente_obj)
            session.commit()
            return True
        return False

    def dar_preparacion(self, id_receta, cantidad_personas):
        """Retorna los datos de preparación de una receta para cantidad de personas que entra como parámetro
        Parámetros:
            id_receta: identificador de la receta que se va a preparar
            cantidad_personas: cantidad personas para las que se va a preparar la receta
        Retorna:
            (dict): diccionario con los datos de preparación de la receta: nombre, cantidad personas, calorias, costo, tiempo de preparación,
                    (list) ingredientes de la receta
        """
        # Validar parámetros de entrada
        if cantidad_personas <= 0:
            return None

        # Obtener todas las recetas para encontrar la receta por índice
        recetas = session.query(Receta).all()
        if 0 <= id_receta < len(recetas):
            receta_obj = recetas[id_receta]

            # Calcular factor de escalamiento
            factor_escalamiento = cantidad_personas / receta_obj.numero_personas

            # Calcular calorías escaladas
            calorias_escaladas = (
                int(receta_obj.calorias_porcion * factor_escalamiento)
                if receta_obj.calorias_porcion
                else 0
            )

            # Calcular tiempo escalado
            tiempo_escalado = self._escalar_tiempo(
                receta_obj.tiempo_preparacion, factor_escalamiento
            )

            # Obtener ingredientes de la receta
            ingredientes_receta = (
                session.query(IngredienteReceta)
                .filter(IngredienteReceta.receta_id == receta_obj.id)
                .all()
            )

            # Procesar ingredientes y calcular costo total
            datos_ingredientes = []
            costo_total = 0

            for ingrediente_receta in ingredientes_receta:
                # Obtener los datos del ingrediente relacionado
                ingrediente = (
                    session.query(Ingrediente)
                    .filter(Ingrediente.id == ingrediente_receta.ingrediente_id)
                    .first()
                )

                if ingrediente:
                    # Calcular cantidad escalada
                    cantidad_original = float(ingrediente_receta.cantidad)
                    cantidad_escalada = cantidad_original * factor_escalamiento

                    # Calcular valor total del ingrediente
                    valor_total = int(ingrediente.valor_unidad * cantidad_escalada)
                    costo_total += valor_total

                    # Agregar ingrediente a la lista
                    ingrediente_data = {
                        "nombre": ingrediente.nombre,
                        "unidad": ingrediente.unidad_medida,
                        "cantidad": str(cantidad_escalada),
                        "valor": valor_total,
                    }
                    datos_ingredientes.append(ingrediente_data)

            # Construir respuesta
            preparacion_data = {
                "receta": receta_obj.nombre,
                "personas": cantidad_personas,
                "calorias": calorias_escaladas,
                "costo": costo_total,
                "tiempo_preparacion": tiempo_escalado,
                "datos_ingredientes": datos_ingredientes,
            }

            return preparacion_data

        return None

    def _escalar_tiempo(self, tiempo_original, factor):
        """Escala el tiempo de preparación según el factor dado
        Parámetros:
            tiempo_original (str): Tiempo en formato HH:MM:SS
            factor (float): Factor de escalamiento
        Retorna:
            (str): Tiempo escalado en formato HH:MM:SS
        """
        try:
            # Parsear tiempo original
            partes = tiempo_original.split(":")
            if len(partes) == 3:
                horas = int(partes[0])
                minutos = int(partes[1])
                segundos = int(partes[2])
            elif len(partes) == 2:
                horas = 0
                minutos = int(partes[0])
                segundos = int(partes[1])
            else:
                # Formato inválido, retornar tiempo original
                return tiempo_original

            # Convertir a segundos totales
            segundos_totales = horas * 3600 + minutos * 60 + segundos

            # Aplicar factor de escalamiento
            segundos_escalados = int(segundos_totales * factor)

            # Convertir de vuelta a HH:MM:SS
            horas_escaladas = segundos_escalados // 3600
            minutos_escalados = (segundos_escalados % 3600) // 60
            segundos_escalados = segundos_escalados % 60

            return f"{horas_escaladas:02d}:{minutos_escalados:02d}:{segundos_escalados:02d}"

        except (ValueError, IndexError):
            # Si hay error en el parsing, retornar tiempo original
            return tiempo_original
