import math

# Su propósito es asegurar que la representación binaria tenga la longitud de bits correcta.
def imprimir_binario(n, bits):
    """Imprime un número en formato binario con espacios."""
    # Usamos una máscara para limitar a 'bits' el número, aunque en Python no es estrictamente necesario 
    # para 'format', es buena práctica para simular enteros de tamaño fijo.
    mascara = (1 << bits) - 1
    # '0{bits}b' asegura que la cadena binaria tenga la longitud 'bits', rellenando con ceros a la izquierda.
    bin_str = format(n & mascara, f'0{bits}b')
    # Añade un espacio cada 4 bits para legibilidad.
    return ' '.join(bin_str[i:i+4] for i in range(0, len(bin_str), 4))


class TraductorDeDirecciones:
    """
    Simula la Unidad de Gestión de Memoria (MMU) para la traducción de
    direcciones virtuales a físicas mediante un esquema de paginación.
    Implementa el concepto de 'empaquetado' (packed) de la entrada de la
    tabla de páginas.
    """

    # --- Definición de Bits de la Entrada Empaquetada (8 bits en total) ---
    # Según la imagen: Marco (3 bits) + Bits de Control (5 bits).
    # Se asume el formato: [ Marco (3b) | P/A (1b) | M (1b) | R (1b) | Cache (2b) ]
    BITS_CONTROL_TOTAL = 5 
    BITS_MARCO = 3 
    
    # Máscara para extraer el Número de Marco (los 3 bits más significativos)
    # Se asume que el marco está en los bits 7, 6, 5. La entrada es de 8 bits (0-7).
    # Máscara: 111 00000 (binario) -> 224 (decimal)
    MASK_MARCO = 0b00000111   # 0x07
    MASK_PRESENTE = 0b00010000  # si el bit P/A sigue siendo bit 4 (0x10)
    SHIFT_PRESENTE = 4

    def __init__(self, tamano_memoria_virtual, tamano_memoria_fisica, tamano_pagina, tabla_empaquetada):
        
        # Validaciones originales (omitiéndolas por brevedad, pero se mantendrían)
        self.tamano_pagina = tamano_pagina
        self.num_paginas = tamano_memoria_virtual // tamano_pagina
        self.num_marcos = tamano_memoria_fisica // tamano_pagina
        
        self.bits_desplazamiento = int(math.log2(tamano_pagina))
        self.bits_pagina_virtual = int(math.log2(self.num_paginas))
        self.bits_marco = int(math.log2(self.num_marcos))
        self.bits_direccion_fisica = int(math.log2(tamano_memoria_fisica))
        
        self.mascara_desplazamiento = (1 << self.bits_desplazamiento) - 1
        
        # Almacenamos la tabla de páginas: {número_página: valor_empaquetado}
        self.tabla_de_paginas = {}
        self._inicializar_tabla_paginas(tabla_empaquetada)

        print("\n--- Parámetros del Traductor (actualizado con la imagen) ---")
        print(f"Tamaño Memoria Virtual: {tamano_memoria_virtual} bytes")
        print(f"Tamaño Memoria Física: {tamano_memoria_fisica} bytes")
        print(f"Tamaño de Página: {tamano_pagina} bytes")
        print("-" * 20)
        print(f"Bits para página virtual: {self.bits_pagina_virtual}")
        print(f"Bits para marco: {self.bits_marco}")
        print(f"Bits para desplazamiento: {self.bits_desplazamiento}")
        print(f"Tamaño Entrada de Página (Packed): {self.BITS_MARCO + self.BITS_CONTROL_TOTAL} bits")
        print(f"Máscara de Marco (bits {7}, {6}, {5}): 0x{self.MASK_MARCO:X}")
        print(f"Máscara de P/A (bit {self.SHIFT_PRESENTE}): 0x{self.MASK_PRESENTE:X}")
        print("\n✅ Tabla de páginas inicializada desde el archivo con valores empaquetados.\n")

        self.imprimir_tabla_paginas_empaquetada()
        print("----------------------------------------------------------")

    def _inicializar_tabla_paginas(self, tabla_empaquetada):
        """
        Inicializa la tabla de páginas, guardando el valor 'empaquetado' 
        (Entrada de Tabla de Páginas) o 0 si no hay entrada.
        
        :param tabla_empaquetada: Mapeos {número_página: valor_empaquetado}.
        """
        for i in range(self.num_paginas):
            # Si la página no está en el mapeo, se considera no presente (valor 0 o 'X')
            self.tabla_de_paginas[i] = tabla_empaquetada.get(i, 0) 


    def imprimir_tabla_paginas_empaquetada(self):
        """Imprime la tabla de páginas con la entrada empaquetada y el valor desempaquetado."""
        print("📘 Tabla de Páginas (Desempaquetado para Visualización):")
        print("-------------------------------------------------------------------------")
        print(f"{'Página':<8}{'Entrada (Dec)':<15}{'Entrada (Bin)':<20}{'Marco':<10}{'P/A':<5}")
        print("-------------------------------------------------------------------------")
        for pagina, entrada_packed in self.tabla_de_paginas.items():
            if entrada_packed == 0 and pagina not in [3, 5, 6, 7, 10]: # Las páginas con 'X' en la imagen
                 marco = 'n/a'
                 presente = '0'
                 entrada_bin = '0' * 8
            else:
                 # 1. Desempaquetar el bit Presente/Ausente (P/A)
                 presente = (entrada_packed & self.MASK_PRESENTE) >> self.SHIFT_PRESENTE
                 # 2. Desempaquetar el Número de Marco
                 numero_marco = entrada_packed & self.MASK_MARCO # 5
                 marco = numero_marco
                 entrada_bin = imprimir_binario(entrada_packed, self.BITS_MARCO + self.BITS_CONTROL_TOTAL).replace(" ", "")
                 
            print(f"{pagina:<8}{entrada_packed:<15}{entrada_bin:<20}{marco:<10}{presente:<5}")
        print("-------------------------------------------------------------------------")

    def traducir(self, direccion_virtual):
        """
        Realiza la traducción de una dirección virtual (DV) a una dirección física (DF).
        
        :param direccion_virtual: La dirección virtual a traducir (entero).
        """
        max_bits_dv = self.bits_pagina_virtual + self.bits_desplazamiento
        print(f"\n--- Traduciendo Dirección Virtual: {direccion_virtual} (0x{direccion_virtual:X}) ---")
        print(f"DV en binario ({max_bits_dv} bits): {imprimir_binario(direccion_virtual, max_bits_dv)}")
        
        # 1. Extracción de Número de Página y Desplazamiento
        numero_pagina = direccion_virtual >> self.bits_desplazamiento
        desplazamiento = direccion_virtual & self.mascara_desplazamiento

        print("\n1. Extracción de Componentes:")
        print(f"   Número de Página = {numero_pagina} (bin: {imprimir_binario(numero_pagina, self.bits_pagina_virtual)})") 
        print(f"   Desplazamiento   = {desplazamiento} (bin: {imprimir_binario(desplazamiento, self.bits_desplazamiento)})")
        
        print("\n2. Consulta y Desempaquetado de la Entrada de Páginas:")
        if numero_pagina not in self.tabla_de_paginas:
            print(f"   ❌ Error: La página {numero_pagina} es inválida para este espacio de direcciones.")
            return

        entrada_packed = self.tabla_de_paginas[numero_pagina]
        entrada_bin_full = imprimir_binario(entrada_packed, self.BITS_MARCO + self.BITS_CONTROL_TOTAL).replace(" ", "")
        print(f"   Entrada Empaquetada (Dec): {entrada_packed}")
        print(f"   Entrada Empaquetada (Bin): {entrada_bin_full}")
        
        # --- DESEMPAQUETADO ---
        # 2.1 Desempaquetar el bit Presente/Ausente (P/A)
        presente = (entrada_packed & self.MASK_PRESENTE) >> self.SHIFT_PRESENTE
        # 2.2 Desempaquetar el Número de Marco
        numero_marco = (entrada_packed & self.MASK_MARCO) >> self.BITS_CONTROL_TOTAL # Shift de 5 bits
        
        print(f"   ➡️ Bit P/A (Presente) = {presente}")
        print(f"   ➡️ Número de Marco = {numero_marco}")


        if presente == 0:
            print(f"   ❌ FALLO DE PÁGINA: La página {numero_pagina} no está cargada en memoria.")
            return

        print(f"   ✅ La página está presente en el Marco {numero_marco}.")
        
        # 3. Cálculo de la Dirección Física (Concatenación)
        # Marco_Físico << bits_desplazamiento: Coloca el número de marco en los bits altos.
        # | desplazamiento: Añade el desplazamiento original en los bits bajos.
        direccion_fisica = (numero_marco << self.bits_desplazamiento) | desplazamiento

        print("\n3. Cálculo de la Dirección Física:")
        print(f"   Marco binario: {imprimir_binario(numero_marco, self.bits_marco)}")
        print(f"   Desplazamiento binario: {imprimir_binario(desplazamiento, self.bits_desplazamiento)}")
        
        print("\n--- Resultado de la Traducción ---")
        print(f"Dirección Física: Decimal = {direccion_fisica}")
        print(f"                   Hexadecimal = 0x{direccion_fisica:X}")
        print(f"                   Binario ({self.bits_direccion_fisica} bits) = {imprimir_binario(direccion_fisica, self.bits_direccion_fisica)}")
        print("----------------------------------")
        return direccion_fisica


# --- DATOS DE ENTRADA SEGÚN LA IMAGEN ---

# 1. Parámetros de Memoria
TAMANO_PAGINA = 32
TAMANO_MEMORIA_FISICA = 256
TAMANO_MEMORIA_VIRTUAL = 512

# 2. Tabla de Páginas con el valor 'Empaquetado' (Entrada de Tabla de páginas)
# Solo se incluyen las páginas que tienen una entrada de tabla definida.
# {Número_página: Entrada_Tabla_de_páginas (Decimal)}
tabla_de_paginas_empaquetada = {
    3: 223,
    5: 168,
    6: 235,
    7: 57,
    10: 138 
}


# --- INICIALIZACIÓN Y PRUEBAS ---
try:
    mmu = TraductorDeDirecciones(
        tamano_memoria_virtual=TAMANO_MEMORIA_VIRTUAL,
        tamano_memoria_fisica=TAMANO_MEMORIA_FISICA,
        tamano_pagina=TAMANO_PAGINA,
        tabla_empaquetada=tabla_de_paginas_empaquetada
    )

    # Ejemplos de prueba:
    # 1. Dirección que corresponde a la Página 5 (Marco 0, P/A=1)
    # Dirección Virtual = Pág 5 (160 - 191). Ejemplo: 180 (0b10110100)
    mmu.traducir(direccion_virtual=180) 
    
    # 2. Dirección que corresponde a la Página 3 (Marco 7, P/A=1)
    # Dirección Virtual = Pág 3 (96 - 127). Ejemplo: 105 (0b01101001)
    mmu.traducir(direccion_virtual=105)

    # 3. Dirección que corresponde a una página NO presente (Página 1, 'X')
    # Dirección Virtual = Pág 1 (32 - 63). Ejemplo: 40 (0b00101000)
    mmu.traducir(direccion_virtual=40) 

except ValueError as e:
    print(f"Error de configuración: {e}")