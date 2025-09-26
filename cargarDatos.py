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
    """Lee la configuración de memoria y el mapeo inicial de la tabla de páginas."""
    config = {} #Parametros globales(tamanos de memoria y pagina)
    mapeo_paginas = {} #{0: 3, 1: 2, 2: 5, etc...}
    try:
        with open(nombre_archivo, 'r') as f:
            modo_mapas = False #Para distinguir la seccion de configuracion de la de mapeos  
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith('#'): #Ignoramos los comentarios y lineas vacias
                    continue
                
                if linea == 'MAPEOS:':
                    modo_mapas = True
                    continue
                
                pagina, marco = linea.split(':', 1) #Dividimos la linea en pagina y marco
                pagina = pagina.strip() #Evitamos saltos de linea innecesarios
                marco = marco.strip()

                if modo_mapas:
                    mapeo_paginas[int(pagina)] = int(marco) #Añadimos la pagina con su marco al diccionario
                else:
                    config[pagina] = int(marco)

        if not all(k in config for k in ['TAMANO_MEMORIA_VIRTUAL', 'TAMANO_MEMORIA_FISICA', 'TAMANO_PAGINA']): #Verificamos que config contenga las claves necesarias 
            raise KeyError("El archivo de configuración no contiene todas las claves de memoria necesarias.")
            
        return config, mapeo_paginas
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{nombre_archivo}'.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al procesar el archivo de configuración: {e}")
        sys.exit(1)