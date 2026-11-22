from abc import abstractmethod
from excepciones_logs import EntidadBase, DatosInvalidosError, registrar_evento

#SERVICIOS
#define la estructura comun y las reglas base para todos los servicios. No se puede instanciar directamente; sirve como plantilla para las subclases.


class Servicio(EntidadBase):
    def __init__(self, id_servicio, nombre_servicio, tarifa_base, disponible=True):
        # Valida y asigna los atributos comunes a todos los servicios
        super().__init__(id_servicio)
        self._nombre_servicio = str(nombre_servicio).strip()
        self._disponible = bool(disponible)
        
        #convierte la tarifa_base a float y manejo posibles errores de conversión

        try:
            self._tarifa_base = float(tarifa_base)
        except (ValueError, TypeError) as error_original:
            raise DatosInvalidosError(
                f"La tarifa base '{tarifa_base}' debe ser un valor numérico válido."
            ) from error_original
    
    # metodos de consulta y control de disponibilidad
    def obtener_nombre_servicio(self):
        return self._nombre_servicio

    def esta_disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        self._disponible = bool(estado)

    @abstractmethod
    def calcular_costo(self, cantidad):
        pass

    @abstractmethod
    def describir_servicio(self):
        pass

    #metodos abstractos (cada servicio define su propia implementacion)

    def calcular_costo_final(self, cantidad, porcentaje_descuento=0.0, aplicar_iva=False):
        subtotal = self.calcular_costo(cantidad)

        if porcentaje_descuento < 0 or porcentaje_descuento > 50:
            raise DatosInvalidosError("El descuento debe estar entre 0% y 50%")

        valor_descuento = subtotal * (porcentaje_descuento / 100)
        total = subtotal - valor_descuento

        if aplicar_iva:
            total = total * 1.19

        return round(total, 2)

    def obtener_resumen(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"Servicio [{self._id}] - {self._nombre_servicio} | Tarifa base: ${self._tarifa_base:.2f} ({estado})"

#RESERVA DE SALA
#calcula el costo por horas de sala y agrega un recargo si la sala es para más de 10 personas. 

class ReservaSala(Servicio):
    def __init__(self, id_servicio, nombre_servicio, tarifa_hora, capacidad_personas, disponible=True):
        super().__init__(id_servicio, nombre_servicio, tarifa_hora, disponible)
        try:
            self._capacidad_personas = int(capacidad_personas)
        except (ValueError, TypeError) as error_original:
            raise DatosInvalidosError("La capacidad de personas debe ser un número entero.") from error_original

        self.validar()
        registrar_evento(f"Servicio de Sala creado: {self._nombre_servicio} (ID: {self._id})")

    def validar(self):
        if not self._nombre_servicio:
            raise DatosInvalidosError("El nombre de la sala no puede estar vacío.")
        if self._tarifa_base <= 0:
            raise DatosInvalidosError("La tarifa por hora de la sala debe ser mayor a cero.")
        if self._capacidad_personas < 2:
            raise DatosInvalidosError("La sala debe tener capacidad mínima para 2 personas.")
        return True

    def calcular_costo(self, horas):
        if horas <= 0:
            raise DatosInvalidosError("Las horas de reserva de la sala deben ser mayores a cero.")
        costo = self._tarifa_base * horas
        if self._capacidad_personas > 10:
            costo += 15000
        return costo

    def describir_servicio(self):
        return f"Sala '{self._nombre_servicio} (Capacidad: {self._capacidad_personas} personas) - ${self._tarifa_base:.2f}/hora"

#ALQUILER DE EQUIPO
#Calcula el costo por dias de alquiler sumando el deposito de seguridad.

class AlquilerEquipo(Servicio):
    def __init__(self, id_servicio, nombre_servicio, tarifa_dia, tipo_equipo, deposito_seguridad,  disponible=True):
        super().__init__(id_servicio, nombre_servicio, tarifa_dia, disponible)
        self._tipo_equipo = str(tipo_equipo).strip()
        try:
            self._deposito_seguridad = float(deposito_seguridad)
        except (ValueError, TypeError) as error_original:
            raise DatosInvalidosError("El depósito de seguridad debe ser un valor numérico") from error_original

        self.validar()
        registrar_evento(f"Servicio de Alquiler de Equipo creado: {self._nombre_servicio} (ID: {self._id})")

    def validar(self):
        if not self._nombre_servicio or not self._tipo_equipo:
            raise DatosInvalidosError("El nombre y el tipo de equipo son obligatorios.")
        if self._tarifa_base <= 0:
            raise DatosInvalidosError("La tarifa diaria del equipo debe ser mayor a cero.")
        if self._deposito_seguridad < 0:
            raise DatosInvalidosError("El deposito de seguridad no puede ser negativo.")
        return True

    def calcular_costo(self, dias):
        if dias < 1:
            raise DatosInvalidosError("El alquiler de equipos debe ser por mínimo dia.")
        return (self._tarifa_base * dias) + self._deposito_seguridad

    def describir_servicio(self):
        return f"Equipo '{self._nombre_servicio}' [Tipo: {self._tipo_equipo}] - ${self._tarifa_base:.2f}/día + Depósito ${self._deposito_seguridad:.2f}"

#ASESORIA ESPECIALIZADA
#Calcula el costo por horas de asesoría sumando un recargo si es urgente.

class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio, nombre_servicio, tarifa_base, area_tecnica, urgente=False, disponible=True):
        super().__init__(id_servicio, nombre_servicio, tarifa_base, disponible)
        self._area_tecnica = str(area_tecnica).strip()
        self._urgente = bool(urgente)

        self.validar()
        registrar_evento(f"Servicio de Asesoría creado: {self._nombre_servicio} (ID: {self._id})")

    def validar(self):
        if not self._nombre_servicio or not self._area_tecnica:
            raise DatosInvalidosError("El nombre y el área técnica de la asesoría son obligatorios")
        if self._tarifa_base <= 0:
            raise DatosInvalidosError("La tarifa por hora de la asesoría debe ser mayor a cero.")
        return True

    def calcular_costo(self, horas):
        if horas < 1:
            raise DatosInvalidosError("La asesoría especializada mínimo 1 hora.")
        costo = self._tarifa_base * horas
        if self._urgente:
            costo = costo * 1.20
        return costo

    def describir_servicio(self):
        prioridad = "Urgente (+20%)" if self._urgente else "Estándar"
        return f"Asesoría '{self._nombre_servicio}' [Área: {self._area_tecnica} 