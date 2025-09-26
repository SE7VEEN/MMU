import math
def imprimir_binario(n, bits):
    """Imprime un número en formato binario con espacios."""
    mascara = (1 << bits) - 1
    bin_str = format(n & mascara, f'0{bits}b')
    return ' '.join(bin_str[i:i+4] for i in range(0, len(bin_str), 4))

class TraductorDeDirecciones:
    def __init__(self, tamano_memoria_virtual, tamano_memoria_fisica, tamano_pagina, mapas_iniciales):
        self.tamano_pagina = tamano_pagina
        self.num_paginas = tamano_memoria_virtual // tamano_pagina
        self.num_marcos = tamano_memoria_fisica // tamano_pagina
        self.bits_desplazamiento = int(math.log2(tamano_pagina))
        self.bits_pagina_virtual = int(math.log2(self.num_paginas))
        self.bits_marco = int(math.log2(self.num_marcos))
        self.bits_direccion_fisica = int(math.log2(tamano_memoria_fisica))
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
        print(f"Bits para marco: {self.bits_marco}")
        print(f"Bits para dirección física: {self.bits_direccion_fisica}")
        print(f"Máscara de desplazamiento: {imprimir_binario(self.mascara_desplazamiento, 16)} (0x{self.mascara_desplazamiento:X})")
        print("\n✅ Tabla de páginas inicializada desde el archivo.\n")
        self.imprimir_tabla_paginas()
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

    def imprimir_tabla_paginas(self):
        """Imprime la tabla de páginas en forma de tabla legible."""
        print("📘 Tabla de Páginas:")
        print("--------------------------------------------------")
        print(f"{'Página':<10}{'Marco':<10}{'Presente':<10}")
        print("--------------------------------------------------")
        for pagina, datos in self.tabla_de_paginas.items():
            presente = "1" if datos['presente'] == 1 else "0"
            print(f"{pagina:<10}{datos['marco']:<10}{presente:<10}")
        print("--------------------------------------------------")

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
        print(f"   Bits del marco: {self.bits_marco}, Bits de dirección física: {self.bits_direccion_fisica}")

        print("\n--- Resultado ---")
        print(f"Dirección Física: binario = {imprimir_binario(direccion_fisica, self.bits_direccion_fisica)}")
        print(f"                   hexadecimal = 0x{direccion_fisica:X}")
        print("-----------------")