from excepciones_logs import EntidadBase, DatosInvalidosError, registrar_evento

"""
Aquí conecto este archivo con el anterior trayendo la clase abstracta EntidadBase, mi error personalizado DatosInvalidosError y la función registrar_evento para guardar 
lo que pase en el archivo de logs. Luego creo la clase Cliente heredando de EntidadBase. En el def __init__ primero uso super().__init__(id_cliente) para que la clase padre guarde y revise el ID. Después guardo el nombre, documento, correo, teléfono y el estado activo usando el guion bajo para que sean atributos privados (encapsulación). Al final del constructor llamo a self.validar() para revisar que todos los datos estén bien escritos antes de aceptar al cliente, y si pasa la prueba, dejo el registro guardado en el log.
"""

class Cliente(EntidadBase):
    def __init__(self, id_cliente, nombre, documento, correo, telefono):
        super().__init__(id_cliente)
        self._nombre = str(nombre).strip()
        self._documento = str(documento).strip()
        self._correo = str(correo).strip()
        self._telefono = str(telefono).strip()
        self._activo = True

        self.validar()
        registrar_evento(f"Cliente registrado exitosamente: {self._nombre} (ID: {self._id})")

    """
    Este método validar() es obligatorio porque lo exige la clase abstracta EntidadBase.  Aquí pongo varios filtros con condicionales if para revisar cada dato del cliente: que el nombre no venga vacío ni sea muy corto, que el documento y el teléfono tengan solo números usando .isdigit(), y que el correo tenga un arroba (@) y un punto. Si alguno de estos datos falla, uso raise DatosInvalidosError para detener la creación del cliente y avisar exactamente qué dato quedó mal escrito.
    """

    def validar(self):
        if not self._nombre or len(self._nombre) < 3:
            raise DatosInvalidosError("El nombre del cliente debe tener al menos 3 letras")

        if not self._documento.isdigit() or len(self._documento) < 5:
            raise DatosInvalidosError("El documento debe contener solo números y tener mínimo 5 digitos.")

        if "@" not in self._correo or "." not in self._correo:
            raise DatosInvalidosError(f"El correo '{self._correo}' no tiene un formato válido.")

        if not self._telefono.isdigit() or len(self._telefono) < 7:
            raise DatosInvalidosError("El teléfono debe contener solo números y tener al menos 7 dígitos.")
        return True

    """
    Como puse los atributos del cliente como privados con el guion bajo, aquí creo métodos públicos para poder leerlos o modificarlos de forma controlada desde afuera.
    Por ejemplo, en actualizar_correo primero reviso que el correo nuevo sea válido antes de cambiarlo. Al final programo obtener_resumen(), que es el segundo método obligatorio de EntidadBase, para devolver una ficha corta con los datos del cliente.
    """

    def obtener_nombre(self):
        return self._nombre

    def obtener_correo(self):
        return self._correo

    def esta_activo(self):
        return self._activo

    def actualizar_correo(self, nuevo_correo):
        nuevo_correo = str(nuevo_correo).strip()
        if "@" not in nuevo_correo or "." not in nuevo_correo:
            raise DatosInvalidosError("El nuevo correo electrónico no es válido.")
        self._correo = nuevo_correo
        registrar_evento(f"Correo actualizado para el cliente {self._nombre} (ID: {self._id})")

    def obtener_resumen(self):
        estado = "Activo" if self._activo else "Inactivo"
        return f"Cliente [{self._id}] - {self._nombre} | Doc: {self._documento} | Correo: {self._correo} ({estado})"
