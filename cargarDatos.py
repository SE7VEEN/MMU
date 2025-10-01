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


import sys

def cargar_configuracion_desde_archivo(nombre_archivo):
    """
    Lee la configuración de memoria y el mapeo inicial de la tabla de páginas 
    (usando el valor empaquetado de la entrada).
    """
    config = {}
    # Ahora almacenamos el valor empaquetado: {número_página: Entrada_Tabla_de_páginas}
    tabla_empaquetada = {} 
    
    try:
        with open(nombre_archivo, 'r') as f:
            modo_mapas = False 
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith('#'): 
                    continue
                
                if linea == 'MAPEOS_EMPAQUETADOS:': # Cambié el marcador para claridad
                    modo_mapas = True
                    continue
                
                # Intentar dividir en clave:valor
                try:
                    clave, valor = linea.split(':', 1)
                    clave = clave.strip()
                    valor = valor.strip()
                except ValueError:
                    print(f"❌ Error de formato en línea: '{linea}'. Esperando 'clave:valor'.")
                    continue

                if modo_mapas:
                    # En modo mapeos, la CLAVE es el NÚMERO DE PÁGINA, 
                    # y el VALOR es la ENTRADA EMPAQUETADA (decimal)
                    tabla_empaquetada[int(clave)] = int(valor) 
                else:
                    # En modo config, la CLAVE es el NOMBRE del parámetro y el VALOR es su tamaño
                    config[clave] = int(valor)

        if not all(k in config for k in ['TAMANO_MEMORIA_VIRTUAL', 'TAMANO_MEMORIA_FISICA', 'TAMANO_PAGINA']):
            raise KeyError("El archivo de configuración no contiene todas las claves de memoria necesarias.")
            
        return config, tabla_empaquetada
    
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{nombre_archivo}'.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al procesar el archivo de configuración: {e}")
        sys.exit(1)