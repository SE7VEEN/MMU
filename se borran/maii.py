#   Implementación de un traductor de direcciones de memoria virtual a física
#   Universidad Autónoma de Puebla
#   Facultad de Ciencias de la Computación
#   Materia: Sistemas Operativos II
#   date 25/09/2025
#   Integrantes:
#    -Jose Antonio Rodriguez Maldonado  202250718
#    -Jose Luis Santiago Ibañez         202253693
#    -Jorge Luis Vergara Mora           202256565
#   Objetivo:
#   Implementar un sistema de traducción de direcciones mediante paginación
#   simulando una Unidad de Gestión de Memoria (MMU).


from traduccion_LFU import TraductorDeDirecciones
from cargarDatos import cargar_configuracion_desde_archivo

if __name__ == "__main__":
    try:
        configuracion, mapas, direcciones_vi_hex = cargar_configuracion_desde_archivo('config1.txt')
        
        traductor = TraductorDeDirecciones(
            configuracion['TAMANO_MEMORIA_VIRTUAL'],
            configuracion['TAMANO_MEMORIA_FISICA'],
            configuracion['TAMANO_PAGINA'],
            mapas
        )
        
        print("\n--- Listo para traducir ---")
        # 4. NUEVO BUCLE: Iterar sobre las direcciones cargadas.
        for i, dv_str in enumerate(direcciones_vi_hex):
            print(f"\n==============================================")
            # Asegúrate de que tu método traducir() acepta la string hexadecimal (dv_str)
            print(f" ACCESO {i+1} de {len(direcciones_vi_hex)}: Procesando DV: {dv_str}")
            print(f"==============================================")
            
            # 5. Llamar a traducir. El método traducir() debe hacer la conversión int(dv_str, 16).
            traductor.traducir(dv_str)


    except (ValueError, KeyError) as e:
        print(f"\nError durante la ejecución: {e}")
    except KeyboardInterrupt:
        print("\n\nSimulación interrumpida.")
