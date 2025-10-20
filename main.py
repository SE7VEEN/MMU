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
from colorama import Fore, Style, init

init(autoreset=True)  # Para que los colores se reinicien automáticamente

if __name__ == "__main__":
    try:
        configuracion, mapas, direcciones_vi_hex = cargar_configuracion_desde_archivo('config1.txt')
        
        traductor = TraductorDeDirecciones(
            configuracion['TAMANO_MEMORIA_VIRTUAL'],
            configuracion['TAMANO_MEMORIA_FISICA'],
            configuracion['TAMANO_PAGINA'],
            mapas
        )
        
        print(f"\n{Fore.CYAN + Style.BRIGHT}--- Listo para traducir ---{Style.RESET_ALL}")
        
        # Iterar sobre las direcciones cargadas
        for i, dv_str in enumerate(direcciones_vi_hex):
            print(Fore.LIGHTBLUE_EX  + "\n==============================================")
            print(
                f"{Fore.GREEN + Style.BRIGHT}ACCESO {i+1}{Style.RESET_ALL} "
                f"{Fore.CYAN}de{Style.RESET_ALL} "
                f"{Fore.MAGENTA + Style.BRIGHT}{len(direcciones_vi_hex)}{Style.RESET_ALL}: "
                f"{Fore.WHITE}Procesando DV: {Fore.LIGHTBLUE_EX}{dv_str}{Style.RESET_ALL}"
            )
            print(Fore.LIGHTBLUE_EX  + "==============================================")
            
            traductor.traducir(dv_str)

    except (ValueError, KeyError) as e:
        print(f"\n{Fore.RED}Error durante la ejecución:{Style.RESET_ALL} {e}")
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}Simulación interrumpida.{Style.RESET_ALL}")
