import sys
def cargar_configuracion_desde_archivo(nombre_archivo):
    """Lee la configuración de memoria y el mapeo inicial de la tabla de páginas."""
    config = {}
    mapas_iniciales = {}
    try:
        with open(nombre_archivo, 'r') as f:
            modo_mapas = False
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith('#'):
                    continue
                
                if linea == 'MAPEOS:':
                    modo_mapas = True
                    continue
                
                clave, valor = linea.split(':', 1)
                clave = clave.strip()
                valor = valor.strip()

                if modo_mapas:
                    mapas_iniciales[int(clave)] = int(valor)
                else:
                    config[clave] = int(valor)

        if not all(k in config for k in ['TAMANO_MEMORIA_VIRTUAL', 'TAMANO_MEMORIA_FISICA', 'TAMANO_PAGINA']):
            raise KeyError("El archivo de configuración no contiene todas las claves de memoria necesarias.")
            
        return config, mapas_iniciales
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{nombre_archivo}'.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al procesar el archivo de configuración: {e}")
        sys.exit(1)