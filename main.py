from traduccion import TraductorDeDirecciones
from cargarDatos import cargar_configuracion_desde_archivo

# --- Ejecución del Programa ---
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
