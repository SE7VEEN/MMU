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


from traduccion1 import TraductorDeDirecciones
from cargarDatos import cargar_configuracion_desde_archivo

if __name__ == "__main__":
    try:
        configuracion, mapas = cargar_configuracion_desde_archivo('config.txt')
        
        traductor = TraductorDeDirecciones(
            configuracion['TAMANO_MEMORIA_VIRTUAL'],
            configuracion['TAMANO_MEMORIA_FISICA'],
            configuracion['TAMANO_PAGINA'],
            mapas
        )
        
        print("\n--- Listo para traducir ---")
        while True:
            dv_str = input("Ingrese una dirección virtual en HEXADECIMAL (ej. 0x1A2F) o 'q' para salir: ")
            if dv_str.lower() == 'q':
                break
            
            try:
                direccion_virtual = int(dv_str, 16)
            except ValueError:
                print("❌ Entrada inválida. Use formato hexadecimal (ej: 0x1A2F o 1A2F).")
                continue

            traductor.traducir(direccion_virtual)

    except (ValueError, KeyError) as e:
        print(f"\nError durante la ejecución: {e}")
    except KeyboardInterrupt:
        print("\n\nSimulación interrumpida.")
