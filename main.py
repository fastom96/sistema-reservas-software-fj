from excepciones_logs import (
    ErrorSistemaFJ,
    DatosInvalidosError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    registrar_evento,
    registrar_error
)

from clientes import Cliente
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reservas import Reserva

"""
Aquí conecto este archivo principal con los cuatro módulos que ya creé: las excepciones y los logs, la clase Cliente, los tres servicios especializados y la clase Reserva. Luego creo la función ejecutar_simulaciones() donde preparo tres listas vacías en memoria (clientes, servicios y reservas) para guardar los datos sin usar bases de datos. En las primeras simulaciones (1 a 3) pongo a prueba el registro de clientes: primero registro dos clientes con datos buenos usando try / except / else, y después intento crear dos clientes con datos malos (documento con letras y nombre muy corto) para comprobar que mis excepciones personalizadas los bloquean y los guardan en el log sin que el programa se cierre.
"""

def ejecutar_simulaciones():
    registrar_evento("=== INICIO DE SIMULACIONES DEL SISTEMA SOFTWARE FJ ===")
    print("\n============================================================")
    print("  SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ (SIMULACIONES)  ")
    print("============================================================\n")

    clientes = []
    servicios = []
    reservas = []

    #Simulación 1 (Válida): Registro correcto de clientes
    print("--- Simulación 1: Registro válido de clientes ---")
    try:
        c1 = Cliente("CLI-01", "Laura Rivera", "1045678912", "laura.rivera@correo.com", "3215879685")
        c2 = Cliente("CLI-02", "John Ossa", "1014315584", "john.osssa@empresa.com", "3106253185")
    except ErrorSistemaFJ as error:
        registrar_error(f"Simulación 1 falló inesperadamente: {error}")
    else:
        clientes.extend([c1, c2])
        print("OK ->", c1.obtener_resumen())
        print("OK ->", c2.obtener_resumen())
        
    #Simulación 2 (Inválida): Cliente con documento con letras y correo inválido
    print("\n-- Simulación 2: Intento de registrar cliente con datos inválidos ---")
    try:
        c_malo1 = Cliente("CLI-03", "Pedro Ruiz", "ABC12345", "pedro_ruiz.com", "3001112233")
        clientes.append(c_malo1)
    except DatosInvalidosError as error:
        registrar_error(f"Simulación 2 (Error esperado): {error}")
        print(f"ERROR CONTOLADO -> {error}")

    #Simulación 3 (Inválida): Cliente con nombre muy corto
    print("\n--- Simulación 3: Intento de registrar cliente con nombre corto ---")
    try:
        c_malo2 = Cliente("CLI-04", "AL", "1020304050", "al@correo.com", "3112345678")
        clientes.append(c_malo2)
    except DatosInvalidosError as error:
        registrar_error(f"Simulación 3 (Error esperado): {error}")
        print(f"ERROR CONTROLADO -> {error}")

    """
    En este segundo bloque de simulaciones (4 a 6) pongo a prueba el catálogo de servicios de Software FJ. Primero creo los tres servicios especializados (Sala, Equipo y Asesoría) y los recorro con un ciclo for para mostrar el polimorfismo con describir_servicio(). Luego intento crear un servicio poniendo texto en la tarifa para comprobar el encadenamiento de excepciones (mostrando error.__cause__) y otro servicio con capacidad negativa.
    """

    #Simulación 4 (Válida): Creación de los 3 tipos de servicios (Polimorfismo)
    print("\n--- Simulación 4: Creación válida de los 3 servicios especializados ---")
    try:
        s1 = ReservaSala("SRV-01", "Sala Ejecutiva Norte", 50000, 12)
        s2 = AlquilerEquipo("SRV-02", "Kit Proyectar + Portátil", 80000, "Audiovisual", 30000)
        s3 = AsesoriaEspecializada("SRV-03", "Consultoría Ciberseguridad", 120000, "Seguridad", urgente=True)
    except ErrorSistemaFJ as error:
        registrar_error(f"Simulación 4 falló inesperadamente: {error}")
    else:
        servicios.extend([s1, s2, s3])
        for srv in servicios:
            print("OK ->", srv.describir_servicio())

    #Simulación 5 (Inválida): Servicio con tarifa no numérica (Encadenamiento de excepciones)
    print("\n--- Simulación 5: Servicio con tariafa inválida (Encadenamiento) ---")
    try:
        s_malo1 = ReservaSala("SRV-04", "Sala Sur", "cincuenta_mil", 6)
        servicios.append(s_malo1)
    except DatosInvalidosError as error:
        registrar_error(f"Simulación 5 (Error encadenado): {error} | Causa original: {type(error.__cause__).__name__}")
        print(f"ERROR CONTROLADO -> {error} (Causa técnica: {type(error.__cause__).__name__})")

    # Simulación 6 (Inválida): Sala con capacidad menor al minímo permitido
    print("\n--- Simulación 6: Sala con capacidad insuficiente ---")
    try:
        s_malo2 = ReservaSala("SRV-05", "Cabina Individual", 20000, 1)
        servicios.append(s_malo2)
    except DatosInvalidosError as error:
        registrar_error(f"Simulación 6 (Error esperado): {error}")
        print(f"ERROR CONTROLADO -> {error}")

    """
    En las últimas simulaciones (7 a 12) pruebo todo el ciclo de vida de las reservas. Primero creo y confirmo una reserva válida usando sobrecarga (con descuento e IVA), luego intento reservar esa misma sala ocupada para disparar ServicioNoDisponibleError, y después proceso y liquido esa reserva para liberar la sala. También pruebo cancelar una reserva, intentar volverla a cancelar (OperacionNoPermitidaError) e intentar procesar una reserva sin confirmar (ReservaInvalidaError) usando try / except / finally.
    """

    # Simulación 7 (Válida): Creación y confirmación de reserva con descuento e IVA (Sobrecarga)
    print("\n--- Simulación 7: Creación y confirmación exitosa de reserva ---")
    try:
        r1 = Reserva("RES-01", clientes[0], servicios[0], 3, descuento=10.0, aplicar_iva=True)
        r1.confirmar_reserva()
        reservas.append(r1)
        print("OK ->", r1.obtener_resumen())
    except ErrorSistemaFJ as error:
        registrar_error(f"Simulación 7 falló: {error}")

    # Simulación 8 (Inválida): Intentar reservar una sala que ya está ocupada
    print("\n--- Simulación 8: Intento de reserva sobre servicio no disponible ---")
    try:
        r_fallida = Reserva("RES-02", clientes[1], servicios[0], 2)
        reservas.append(r_fallida)
    except ServicioNoDisponibleError as error:
        registrar_error(f"Simulación 8 (Error esperado): {error}")
        print(f"ERROR CONTROLADO -> {error}")

    # Simulación 9 (Válida): Procesar y liquidar reserva confirmada (liber el servicio)
    print("\n--- Simulación 9: Procesamiento y liquidación de reserva ---")
    try:
        total_pagado = r1.procesar_reserva()
        print(f"OK -> Reserva procesada. Total cobrado: ${total_pagado:.2f} | Estado: {r1.obtener_estado()}")
    except ErrorSistemaFJ as error:
        registrar_error(f"Simulación 9 falló: {error}")

    # Simulación 10 (Válida): Crear, confirmar y cancelar una reserva de alquiler de equipo
    print("\n--- Simulación 10: Creación, confirmación y cancelación de reserva ---")
    try:
        r2 = Reserva("RES-03", clientes[1], servicios[1], 2)
        r2.confirmar_reserva()
        r2.cancelar_reserva("Cambio de fecha solicitado por el cliente")
        reservas.append(r2)
        print("OK ->", r2.obtener_resumen())
    except ErrorSistemaFJ as error:
        registrar_error(f"Simulación 10 falló: {error}")

    # Simulación 11 (Inválida): Intentar cancelar una rserva que ya estaba cancelada
    print("\n--- Simulación 11: Intento de cancelar reserva ya cancelada ---")
    try:
        r2.cancelar_reserva("Segundo intento de cancelación")
    except OperacionNoPermitidaError as error:
        registrar_error(f"Simulación 11 (Error esperado): {error}")
        print(f"ERROR CONTROLADO -> {error}")

    # Simulación 12 (Inválida): Procesar reserva sin confirmar usando try / except / finally
    print("\n--- Simulación 12: Intento de procesar reserva no confirmada ---")
    r3 = Reserva("RES-04", clientes[0], servicios[2], 2, descuento=15.0)
    reservas.append(r3)
    try:
        r3.procesar_reserva()
    except ReservaInvalidaError as error:
        registrar_error(f"Simulación 12 (Error esperado): {error}")
        print(f"ERROR CONTROLADO -> {error}")
    finally:
        print(f"FINALIZADO -> Verificación de cierre en Simulación 12 (Estado de RES-04: {r3.obtener_estado()})")

    print("\n============================================================")
    print(f"  RESUMEN FINAL EN MEMORIA: {len(clientes)} Clientes | {len(servicios)} Servicios | {len(reservas)} Reservas")
    print("============================================================\n")
    registrar_evento("=== FIN DE SIMULACIONES - APLICACIÓN ESTABLE SIN INTERRUPCIONES ===")

if __name__ == "__main__":
    ejecutar_simulaciones()