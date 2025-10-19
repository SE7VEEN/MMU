import sys
import math

# Nota: Asumo que la clase TraductorDeDirecciones y la función imprimir_binario
# están definidas en este mismo script o han sido importadas.
# Para este ejemplo, solo modifico la función de carga.

def cargar_configuracion_desde_archivo(nombre_archivo):
    """
    Lee la configuración de memoria, el mapeo inicial de la tabla de páginas 
    (como HEX), y la secuencia de direcciones virtuales (como HEX).
    """
    config = {}
    tabla_empaquetada = {} 
    direcciones_virtuales = []
    
    modo_mapas = False
    modo_direcciones = False

    try:
        with open(nombre_archivo, 'r') as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith('#'): 
                    continue
                
                # --- Detección de Secciones ---
                if linea == 'MAPEOS_EMPAQUETADOS:': 
                    modo_mapas = True
                    modo_direcciones = False
                    continue
                
                if linea == 'DIRECCIONES_VI:': 
                    modo_mapas = False
                    modo_direcciones = True
                    continue
                
                # --- Procesamiento de Secciones ---
                
                if modo_direcciones:
                    # Las direcciones virtuales son una lista de strings hexadecimales
                    # que se añaden directamente.
                    # Asume que cada línea en esta sección es una DV.
                    direcciones_virtuales.append(linea)
                    continue

                try:
                    clave, valor = linea.split(':', 1)
                    clave = clave.strip()
                    valor = valor.strip()
                except ValueError:
                    print(f"❌ Error de formato en línea: '{linea}'. Esperando 'clave:valor'.")
                    continue

                if modo_mapas:
                    # Las entradas empaquetadas se leen como STRING HEXADECIMAL
                    # y la clave (página) se asume ENTERO.
                    try:
                        pagina_int = int(clave)
                        # El valor se mantiene como string hexadecimal para la clase Traductor
                        tabla_empaquetada[pagina_int] = valor 
                    except ValueError:
                         print(f"❌ Error: La clave de página '{clave}' no es un número entero válido.")
                    
                else:
                    # Configuraciones de memoria (TAMANO_*)
                    try:
                        # Se asume que los valores de configuración son DECIMALES
                        config[clave] = int(valor) 
                    except ValueError:
                        print(f"❌ Error: El valor de configuración '{valor}' para '{clave}' no es un número entero.")


        if not all(k in config for k in ['TAMANO_MEMORIA_VIRTUAL', 'TAMANO_MEMORIA_FISICA', 'TAMANO_PAGINA']):
            raise KeyError("El archivo de configuración no contiene todas las claves de memoria necesarias.")
            
        return config, tabla_empaquetada, direcciones_virtuales
    
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{nombre_archivo}'.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al procesar el archivo de configuración: {e}")
        sys.exit(1)