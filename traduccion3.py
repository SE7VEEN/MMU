import math
import sys

def imprimir_binario(n, bits):
    """Imprime un número en formato binario con espacios."""
    mascara = (1 << bits) - 1
    bin_str = format(n & mascara, f'0{bits}b')
    return ' '.join(bin_str[i:i+4] for i in range(0, len(bin_str), 4))

def cargar_configuracion_desde_archivo(nombre_archivo):
    """
    Lee la configuración de memoria y el mapeo inicial de la tabla de páginas.
    """
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

class TraductorDeDirecciones:
    def __init__(self, tamano_memoria_virtual, tamano_memoria_fisica, tamano_pagina, mapas_iniciales):
        self.tamano_pagina = tamano_pagina
        self.num_paginas = tamano_memoria_virtual // tamano_pagina
        self.num_marcos = tamano_memoria_fisica // tamano_pagina
        self.bits_desplazamiento = int(math.log2(tamano_pagina))
        self.bits_pagina_virtual = int(math.log2(self.num_paginas))
        self.mascara_desplazamiento = (1 << self.bits_desplazamiento) - 1
        self.tabla_de_paginas = {}

        self._inicializar_tabla_paginas(mapas_iniciales)

        print("--- Parámetros del Traductor (cargados desde archivo) ---")
        print(f"Tamaño Memoria Virtual: {tamano_memoria_virtual}")
        print(f"Tamaño Memoria Física: {tamano_memoria_fisica}")
        print(f"Tamaño de Página: {tamano_pagina}")
        print("-" * 20)
        print(f"Bits para desplazamiento: {self.bits_desplazamiento}")
        print(f"Bits para página virtual: {self.bits_pagina_virtual}")
        print(f"Máscara de desplazamiento: {imprimir_binario(self.mascara_desplazamiento, 16)} (0x{self.mascara_desplazamiento:X})")
        print("\n✅ Tabla de páginas inicializada desde el archivo.")
        print("----------------------------------------------------------")

    def _inicializar_tabla_paginas(self, mapas_iniciales):
        marcos_usados = set(mapas_iniciales.values())
        if len(marcos_usados) != len(mapas_iniciales.values()):
            print("⚠️ Advertencia: El archivo de configuración asigna el mismo marco a múltiples páginas.")

        for i in range(self.num_paginas):
            if i in mapas_iniciales:
                self.tabla_de_paginas[i] = {"marco": mapas_iniciales[i], "presente": 1}
            else:
                self.tabla_de_paginas[i] = {"marco": 0, "presente": 0}

    def traducir(self, direccion_virtual):
        print(f"\n--- Traduciendo Dirección Virtual: 0x{direccion_virtual:X} ---")
        print(f"DV en binario ({self.bits_pagina_virtual + self.bits_desplazamiento} bits): {imprimir_binario(direccion_virtual, self.bits_pagina_virtual + self.bits_desplazamiento)}")
        
        numero_pagina = direccion_virtual >> self.bits_desplazamiento
        desplazamiento = direccion_virtual & self.mascara_desplazamiento

        print("\n1. Extracción de Componentes:")
        print(f"   Número de Página = {direccion_virtual} >> {self.bits_desplazamiento}  = {numero_pagina}")
        print(f"   Desplazamiento   = {direccion_virtual} & {self.mascara_desplazamiento} = {desplazamiento} "
              f"(bin: {imprimir_binario(desplazamiento, self.bits_desplazamiento)}, hex: 0x{desplazamiento:X})")
        
        print("\n2. Consulta a la Tabla de Páginas:")
        if numero_pagina not in self.tabla_de_paginas:
            print(f"   ❌ Error: La página {numero_pagina} es inválida para este espacio de direcciones.")
            return

        entrada_tabla = self.tabla_de_paginas[numero_pagina]
        print(f"   -> Entrada para página {numero_pagina}: {entrada_tabla}")

        if entrada_tabla["presente"] == 0:
            print(f"   ❌ FALLO DE PÁGINA: La página {numero_pagina} no está cargada en memoria.")
            return

        print(f"   -> ✅ La página está presente en memoria.")
        numero_marco = entrada_tabla["marco"]
        direccion_fisica = (numero_marco << self.bits_desplazamiento) | desplazamiento

        print("\n3. Cálculo de la Dirección Física:")
        print(f"   Fórmula: (marco << bits_desplazamiento) | desplazamiento")
        print(f"   Cálculo: ({numero_marco} << {self.bits_desplazamiento}) | {desplazamiento} = {direccion_fisica}")

        print("\n--- Resultado ---")
        print(f"Dirección Física: binario = {imprimir_binario(direccion_fisica, self.bits_pagina_virtual + self.bits_desplazamiento)}")
        print(f"                   hexadecimal = 0x{direccion_fisica:X}")
        print("-----------------")

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
            
            # ✅ Convertir la entrada a entero desde hexadecimal
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
