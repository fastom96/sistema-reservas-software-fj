import logging
from abc import ABC, abstractmethod

"""
La idea aquí es configurar el sistema de registro (logs) apenas arranca el programa.
Con logging.basicConfig le digo a Python que cree un archivo llamado 'sistema_software_fj.log' y que guarde ahí todo lo que pase, poniendo primero la fecha y hora, luego el nivel (si fue información normal o un error) y después el mensaje. Uso encoding='utf-8' para que no tenga problemas con tildes ni con la letra ñ. Abajo creo dos funciones cortas (registrar_evento y registrar_error) para llamarlas fácil desde cualquier parte del proyecto sin repetir código.
"""

logging.basicConfig(
    filename="sistema_software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def registrar_evento(mensaje):
    logging.info(mensaje)

def registrar_error(mensaje):
    logging.error(mensaje)

"""
Aquí creo mis propias excepciones personalizadas heredando de la clase Exception que ya trae Python. Hago una excepción general llamada ErrorSistemaFJ y de ahí saco cuatro errores más específicos según lo que pueda fallar en la empresa: si meten datos mal escritos, si un servicio no está disponible, si una reserva tiene fallos o si intentan hacer una operación que no está permitida. Uso 'pass' porque no necesitan código extra por dentro, solo el nombre para poder atrapar cada tipo de error por separado más adelante.
"""

class ErrorSistemaFJ(Exception):
    pass

class DatosInvalidosError(ErrorSistemaFJ):
    pass

class ServicioNoDisponibleError(ErrorSistemaFJ):
    pass

class ReservaInvalidaError(ErrorSistemaFJ):
    pass

class OperacionNoPermitidaError(ErrorSistemaFJ):
    pass

"""
Aquí creo la clase abstracta EntidadBase usando ABC, que funcionará como el molde principal para todas las entidades generales del sistema (clientes, servicios y reservas). En el def __init__ recibo el id_entidad, verifico que no venga vacío (si viene vacío lanzo mi error personalizado DatosInvalidosError) y lo guardo privado con self._id. Luego pongo dos métodos abstractos (@abstractmethod): validar y obtener_resumen. Esto obliga a que cualquier clase que herede de EntidadBase tenga que programar obligatoriamente esos dos métodos a su manera.
"""

class EntidadBase(ABC):
    def __init__(self, id_entidad):
        if not id_entidad or str(id_entidad).strip() == "":
            raise DatosInvalidosError("El identificador (ID) de la entidad no puede estar vacío.")
        self._id = str(id_entidad).strip()

    def obtener_id(self):
        return self._id

    @abstractmethod
    def validar(self):
        pass

    @abstractmethod
    def obtener_resumen(self):
        pass