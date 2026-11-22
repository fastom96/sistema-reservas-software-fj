# ---------------------------------------------------------------------------
# Importaciones del proyecto
# ---------------------------------------------------------------------------
# EntidadBase define los atributos y operaciones comunes a todas las entidades.
# Los tipos de error permiten informar cada falla de forma clara y específica.
# registrar_evento escribe las acciones realizadas en el sistema de registros.
from excepciones_logs import (
    EntidadBase,
    DatosInvalidosError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    registrar_evento
)

# Las clases Cliente y Servicio contienen los datos y reglas de sus entidades.
from clientes import Cliente
from servicios import Servicio


# ---------------------------------------------------------------------------
# Clase Reserva
# ---------------------------------------------------------------------------
class Reserva(EntidadBase):
    """Representa una reserva y coordina su estado, costo y disponibilidad."""

    def __init__(self, id_reserva, cliente, servicio, duracion, descuento=0.0, aplicar_iva=False):
        # EntidadBase asigna el identificador común a todas las entidades.
        super().__init__(id_reserva)

        # Se conservan las referencias necesarias para validar y procesar la reserva.
        self._cliente = cliente
        self._servicio = servicio

        # Configuración económica solicitada por el usuario al crear la reserva.
        self._descuento = descuento
        self._aplicar_iva = bool(aplicar_iva)

        # Toda reserva nueva comienza pendiente hasta que sea confirmada.
        self._estado = "Pendiente"

        # El costo inicia en cero y se calcula al confirmar o procesar la reserva.
        self._costo_total = 0.0

        # Convertir la duración permite realizar operaciones numéricas más adelante.
        # Si el dato no puede convertirse, se conserva el error original con "from".
        try:
            self._duracion = float(duracion)
        except (ValueError, TypeError) as error_original:
            raise DatosInvalidosError(
                f"La duración '{duracion}' de la reserva debe ser un número válido."
            ) from error_original

        # Antes de registrar la creación se verifican todas las reglas de la reserva.
        self.validar()

        # El evento deja constancia de la reserva recién creada y de su estado inicial.
        registrar_evento(
            f"Reserva [{self._id}] creada en estado Pendiente para {self._cliente.obtener_nombre()}"
            f"en el servicio '{self._servicio.obtener_nombre_servicio()}'."
        )

    def validar(self):
        """Comprueba que los objetos y valores usados por la reserva sean válidos."""

        # isinstance evita que se acepten objetos que no pertenezcan a las clases esperadas.
        if not isinstance(self._cliente, Cliente):
            raise DatosInvalidosError("La reserva requiere un objeto Cliente válido.")

        # Un cliente inactivo no tiene permiso para crear o confirmar reservas.
        if not self._cliente.esta_activo():
            raise OperacionNoPermitidaError(
                f"El cliente {self._cliente.obtener_nombre()} está inactivo y no puede reservar."
            )

        if not isinstance(self._servicio, Servicio):
            raise DatosInvalidosError("La reserva requiere un objeto Servicio válido.")

        # El servicio debe estar libre para que la reserva pueda utilizarlo.
        if not self._servicio.esta_disponible():
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.obtener_nombre_servicio()}' no se encuentra disponible"
            )

        # La duración debe representar al menos una unidad positiva de tiempo.
        if self._duracion <= 0:
            raise DatosInvalidosError("La duración de la reserva debe ser mayor a cero.")

        return True

    def confirmar_reserva(self):
        """Confirma una reserva pendiente y bloquea temporalmente el servicio."""

        # Solo las reservas pendientes pueden pasar al estado Confirmada.
        if self._estado != "Pendiente":
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva [{self._id}] porque su estado actual es '{self._estado}'."
            )

        # Una segunda reserva no puede utilizar un servicio que ya fue ocupado.
        if not self._servicio.esta_disponible():
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.obtener_nombre_servicio()}' ya fue ocupado por otra reserva."
            )

        # Se calcula el costo estimado aplicando descuento e IVA según la configuración.
        self._costo_total = self._servicio.calcular_costo_final(
            self._duracion, self._descuento, self._aplicar_iva
        )

        # False indica que el servicio ya no está disponible para nuevas reservas.
        self._servicio.cambiar_disponibilidad(False)
        self._estado = "Confirmada"

        registrar_evento(
            f"Reserva [{self._id}] confirmada. Costo estimado: ${self._costo_total:.2f}"
        )

    def cancelar_reserva(self, motivo ="Cancelada por solicitud del cliente"):
        """Cancela la reserva y libera nuevamente el servicio si estaba confirmado."""

        # Las reservas ya procesadas o canceladas no pueden cancelarse otra vez.
        if self._estado in ("Procesada", "Cancelada"):
            raise OperacionNoPermitidaError(
                f"No se puede cancelaar la reserva [{self._id}] en estado '{self._estado}'."
            )

        # Solo una reserva confirmada tiene ocupado el servicio; vuelve a estar libre.
        if self._estado == "Confirmada":
            self._servicio.cambiar_disponibilidad(True)

        self._estado = "Cancelada"
        registrar_evento(f"Reserva [{self._id}] cancelada. Motivo: {motivo}")

    def procesar_reserva(self):
        """Liquida una reserva confirmada y finaliza su ciclo de vida."""

        # El procesamiento solo es válido si la reserva fue confirmada previamente.
        if self._estado != "Confirmada":
            raise ReservaInvalidaError(
                f"Solo se pueden procesar reservas confirmadas. Estado actual de [{self._estado}]'."
            )

        # try contiene el cálculo que puede generar una excepción de datos inválidos.
        try:
            self._costo_total = self._servicio.calcular_costo_final(
                self._duracion, self._descuento, self._aplicar_iva
            )

        # El error original se incluye como causa del error específico de reserva.
        except DatosInvalidosError as error_original:
            raise ReservaInvalidaError(
                f"Fallo al liquidar el costo de la reserva [{self._id}]."
            ) from error_original

        # Este bloque se ejecuta únicamente si el cálculo terminó sin errores.
        else:
            self._estado = "Procesada"

            # True libera el servicio para que pueda ser utilizado por otra reserva.
            self._servicio.cambiar_disponibilidad(True)

            registrar_evento(
                f"Reserva [{self._id}] procesada y liquidada por ${self._costo_total:.2f}."
            )
            return self._costo_total

        # finally se ejecuta tanto si el cálculo tiene éxito como si produce un error.
        finally:
            registrar_evento(
                f"Auditoria finalizada para la reserva [{self._id}] (Estado: {self._estado})."
            )

    def obtener_estado(self):
        """Devuelve el estado actual de la reserva."""
        return self._estado

    def obtener_costo_total(self):
        """Devuelve el costo calculado hasta el momento."""
        return self._costo_total

    def obtener_resumen(self):
        """Construye una descripción legible con los datos principales de la reserva."""
        return (
            f"Reserva [{self._id}] | Cliente: {self._cliente.obtener_nombre()} | "
            f"Servicio: {self._servicio.obtener_nombre_servicio()} | Duración: {self._duracion} | "
            f"Estado: {self._estado} | Total: ${self._costo_total:.2f}"
        )