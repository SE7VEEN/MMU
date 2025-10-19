import math

# Su propósito es asegurar que la representación binaria tenga la longitud de bits correcta.
def imprimir_binario(n, bits):
    """Imprime un número en formato binario con espacios cada 4 bits, agrupando desde la derecha."""
    if bits <= 0:
        return "0"
    mascara = (1 << bits) - 1
    bin_str = format(n & mascara, f'0{bits}b')

    # Calcular el tamaño del primer grupo (puede ser menor a 4)
    resto = len(bin_str) % 4
    grupos = []
    if resto != 0:
        grupos.append(bin_str[:resto])
    # Agregar los grupos restantes de 4 bits
    grupos.extend(bin_str[resto + i:resto + i + 4] for i in range(0, len(bin_str) - resto, 4))
    
    return ' '.join(grupos)


class TraductorDeDirecciones:
    """
    Simula la Unidad de Gestión de Memoria (MMU) para la traducción de
    direcciones virtuales a físicas mediante paginación con entradas empaquetadas.
    Incluye algoritmo de reemplazo LFU (Least Frequently Used).
    """

    def __init__(self, tamano_memoria_virtual, tamano_memoria_fisica, tamano_pagina, tabla_empaquetada):
        # --- Validaciones iniciales ---
        def es_potencia_de_dos(x):
            return x > 0 and (x & (x - 1)) == 0

        if tamano_pagina <= 0 or (tamano_pagina & (tamano_pagina - 1)) != 0:
            raise ValueError("El tamano de pagina debe ser potencia de 2 y > 0")
        if tamano_memoria_virtual % tamano_pagina != 0:
            raise ValueError("El tamano de memoria virtual debe ser divisible por el tamano de pagina")
        if tamano_memoria_fisica % tamano_pagina != 0:
            raise ValueError("El tamano de memoria fisica debe ser divisible por el tamano de pagina")

        # Comprobamos que los tamaños totales sean potencias de 2 para que log2 sea entero
        if not es_potencia_de_dos(tamano_memoria_virtual):
            raise ValueError("tamano_memoria_virtual debe ser potencia de 2")
        if not es_potencia_de_dos(tamano_memoria_fisica):
            raise ValueError("tamano_memoria_fisica debe ser potencia de 2")

        # --- Parámetros básicos ---
        self.tamano_pagina = tamano_pagina
        self.num_paginas = tamano_memoria_virtual // tamano_pagina
        self.num_marcos = tamano_memoria_fisica // tamano_pagina

        self.bits_desplazamiento = int(math.log2(tamano_pagina))
        self.bits_pagina_virtual = int(math.log2(self.num_paginas))
        self.bits_marco = 0 if self.num_marcos <= 1 else int((math.log2(self.num_marcos)))
        self.bits_direccion_fisica = int(math.log2(tamano_memoria_fisica))

        self.mascara_desplazamiento = (1 << self.bits_desplazamiento) - 1

        # --- Diseño del campo empaquetado ---
        # FIJAMOS 5 bits de control 
        self.BITS_CONTROL_TOTAL = 5
        self.BITS_PRESENTE = 1  # dentro de esos 5 bits, el primero es el bit P/A
        if self.BITS_CONTROL_TOTAL < self.BITS_PRESENTE:
            raise ValueError("BITS_CONTROL_TOTAL debe ser >= BITS_PRESENTE")

        # Tamano total (bits) de cada entrada empaquetada.
        self.ENTRADA_BITS = self.bits_marco + self.BITS_CONTROL_TOTAL

        # --- Generación de máscaras ---
        # Orden: [bits de control] [bits de marco]
        self.MASK_CONTROL = ((1 << self.BITS_CONTROL_TOTAL) - 1) << self.bits_marco  # Aisla los bits de control de la entrada
        self.MASK_MARCO = (1 << self.bits_marco) - 1  # Aisla los bits del marco

        self.SHIFT_PRESENTE = self.bits_marco  # primer bit del campo control (posición del bit 'presente')
        self.MASK_PRESENTE = 1 << self.SHIFT_PRESENTE  # Aisla el bit P/A

        # tabla de páginas
        self.tabla_de_paginas = {}
        # Contadores de uso (frecuencias) por página
        self.frecuencias_uso = {}
        # conjunto de marcos ocupados
        self.marcos_ocupados = set()
        # contador de fallos de página
        self.fallos_pagina = 0

        self._inicializar_tabla_paginas(tabla_empaquetada)

        # --- Impresiones informativas ---
        print("\n--- Parámetros del Traductor (cargados desde archivo) ---")
        print(f"Tamaño Memoria Virtual: {tamano_memoria_virtual} bytes")
        print(f"Tamaño Memoria Física: {tamano_memoria_fisica} bytes")
        print(f"Tamaño de Página: {tamano_pagina} bytes")
        print("-" * 40)
        print(f"Número total de páginas: {self.num_paginas}")
        print(f"Número total de marcos: {self.num_marcos}")
        print(f"Bits para página virtual: {self.bits_pagina_virtual}")
        print(f"Bits para marco (calculados): {self.bits_marco}")
        print(f"Bits para desplazamiento: {self.bits_desplazamiento}")
        print(f"Bits para dirección física: {self.bits_direccion_fisica}")
        print(f"Tamaño Entrada Empaquetada (bits): {self.ENTRADA_BITS}")
        print(f"MASCARA_MARCO (hex): 0x{self.MASK_MARCO:X}")
        print(f"MASCARA_PRESENTE (hex): 0x{self.MASK_PRESENTE:X} (bit pos {self.SHIFT_PRESENTE})")
        print("\n✅ Tabla de páginas inicializada desde el archivo con valores empaquetados.\n")

        # Imprimir estado inicial
        self.imprimir_tabla_paginas_empaquetada()
        print("----------------------------------------------------------")

    def _inicializar_tabla_paginas(self, tabla_empaquetada):
        """
        Inicializa la tabla de páginas, guardando el valor 'empaquetado'
        (Entrada de Tabla de Páginas) o 0 si no hay entrada. Valida rangos.
        Además inicializa frecuencias y detecta marcos ocupados.
        """
        # primero llenar con 0 por defecto y frecuencias en 0
        for i in range(self.num_paginas):
            self.tabla_de_paginas[i] = 0
            self.frecuencias_uso[i] = 0

        # ahora cargar las entradas provistas
        for pagina, entrada in tabla_empaquetada.items():
            # asegurar tipos int (por si vienen como strings)
            try:
                pagina_int = int(pagina)
                entrada_int = int(str(entrada), 16)
            except Exception:
                raise ValueError(f"Clave/valor inválido en tabla_empaquetada: {pagina}->{entrada}")

            if not (0 <= pagina_int < self.num_paginas):
                raise ValueError(f"Página {pagina_int} inválida (0..{self.num_paginas-1})")

            # validar que la entrada cabe en los bits definidos
            if entrada_int >= (1 << self.ENTRADA_BITS):
                raise ValueError(f"Entrada empaquetada {entrada_int} para página {pagina_int} excede los {self.ENTRADA_BITS} bits definidos.")

            # si entrada != 0, extraer marco y validar rango, y registrar marco como ocupado si PRESENTE=1
            if entrada_int != 0:
                presente = (entrada_int & self.MASK_PRESENTE) >> self.SHIFT_PRESENTE
                numero_marco = entrada_int & self.MASK_MARCO
                if presente == 1:
                    if numero_marco < 0 or numero_marco >= self.num_marcos:
                        raise ValueError(f"Numero de marco {numero_marco} inválido para la página {pagina_int}.")
                    self.marcos_ocupados.add(numero_marco)

            # guardamos tal cual la entrada empaquetada (como en tu versión original)
            self.tabla_de_paginas[pagina_int] = entrada_int

    def desempaquetar_entrada(self, entrada_packed):
        """
        Devuelve un dict con campos desempaquetados: {'presente': 0/1, 'marco': int, 'raw': entrada_packed}
        """
        presente = (entrada_packed & self.MASK_PRESENTE) >> self.SHIFT_PRESENTE
        numero_marco = entrada_packed & self.MASK_MARCO
        return {"presente": int(presente), "marco": int(numero_marco), "raw": int(entrada_packed)}

    def imprimir_tabla_paginas_empaquetada(self):
        """Imprime la tabla de páginas con la entrada empaquetada y el valor desempaquetado."""
        print("📘 Tabla de Páginas:")
        print("----------------------------------------------------------------------------------------")
        # Encabezado modificado para incluir Hex/Dec
        print(f"{'Página':<8}{'Entrada (Hex/Dec)':<23}{'Entrada (Bin)':<20}{'Marco':<10}{'P/A':<5}")
        print("----------------------------------------------------------------------------------------")

        for pagina, entrada_packed in self.tabla_de_paginas.items():
            entrada_bin = imprimir_binario(entrada_packed, self.ENTRADA_BITS).replace(" ", "")
            desem = self.desempaquetar_entrada(entrada_packed)
            marco = desem['marco'] if entrada_packed != 0 else 'n/a'
            presente = desem['presente'] if entrada_packed != 0 else 0
            entrada_display = f"0x{entrada_packed:X} / {entrada_packed}" 
            print(f"{pagina:<8}{entrada_display:<23}{entrada_bin:<20}{marco:<10}{presente:<5}")

        print("-------------------------------------------------------------------------------")
        print(f"Marcos ocupados: {sorted(list(self.marcos_ocupados))}")
        print(f"Fallos de página (acumulados): {self.fallos_pagina}")
        print("-------------------------------------------------------------------------------")    


    def _encontrar_marco_libre(self):
        """Devuelve el número de un marco libre o None si no hay."""
        for m in range(self.num_marcos):
            if m not in self.marcos_ocupados:
                return m
        return None

    def _reemplazar_pagina_LFU(self, pagina_faltante):
        """Reemplaza la página menos usada (LFU). Devuelve el marco usado."""
        # buscar páginas presentes
        paginas_presentes = [p for p, e in self.tabla_de_paginas.items() if self.desempaquetar_entrada(e)['presente'] == 1]

        if not paginas_presentes:
            return None

        # página menos usada (si hay empate, min por número de página para determinismo)
        pagina_LFU = min(paginas_presentes, key=lambda p: (self.frecuencias_uso.get(p, 0), p))
        entrada_LFU = self.tabla_de_paginas[pagina_LFU]
        marco_liberado = self.desempaquetar_entrada(entrada_LFU)['marco']

        print(f"\n🔁 Reemplazo LFU: Página {pagina_LFU} (uso={self.frecuencias_uso.get(pagina_LFU,0)}) "
              f"→ será reemplazada por Página {pagina_faltante} usando Marco {marco_liberado}.\n")

        # marcar la reemplazada como no presente (ponemos 0, como en tu versión original)
        self.tabla_de_paginas[pagina_LFU] = 0
        # resetear contador de uso de la reemplazada (opcional)
        self.frecuencias_uso[pagina_LFU] = 0

        # asignar el marco al nuevo: construimos la entrada empaquetada con marco y bit presente.
        nueva_entrada = (marco_liberado & self.MASK_MARCO) | self.MASK_PRESENTE
        self.tabla_de_paginas[pagina_faltante] = nueva_entrada
        # marcar uso inicial
        self.frecuencias_uso[pagina_faltante] = 1

        # marcos ocupados no cambian (el marco sigue ocupado)
        # retornar marco asignado
        return marco_liberado

    def traducir(self, direccion_virtual):
        """
        Realiza la traducción de una dirección virtual (DV) a una dirección física (DF).
        Devuelve la dirección física (int) o None si hay fallo de página / error.
        """
        max_bits_dv = self.bits_pagina_virtual + self.bits_desplazamiento  # Bits para representar la DV
        print(f"\n--- Traduciendo Dirección Virtual: {direccion_virtual} (0x{direccion_virtual:X}) ---")
        print(f"DV en binario ({max_bits_dv} bits): {imprimir_binario(direccion_virtual, max_bits_dv)}")

        # 1. Extracción de Número de Página y Desplazamiento
        numero_pagina = direccion_virtual >> self.bits_desplazamiento  # Bits más altos de la DV
        desplazamiento = direccion_virtual & self.mascara_desplazamiento

        print("\n1. Extracción de Componentes:")
        print(f"   Número de Página = {numero_pagina} (bin: {imprimir_binario(numero_pagina, self.bits_pagina_virtual)})")
        print(f"   Desplazamiento   = {desplazamiento} (bin: {imprimir_binario(desplazamiento, self.bits_desplazamiento)})")

        print("\n2. Consulta y Desempaquetado de la Entrada de Páginas:")
        if numero_pagina not in self.tabla_de_paginas:
            print(f"   ❌ Error: La página {numero_pagina} es inválida para este espacio de direcciones.")
            return None

        entrada_packed = self.tabla_de_paginas[numero_pagina]
        entrada_bin_full = imprimir_binario(entrada_packed, self.ENTRADA_BITS).replace(" ", "")
        print(f"   Entrada Empaquetada (Dec): {entrada_packed}")
        print(f"   Entrada Empaquetada (Bin): {entrada_bin_full}")

        desem = self.desempaquetar_entrada(entrada_packed)
        presente = desem['presente']
        numero_marco = desem['marco']

        print(f"   ➡️ Bit P/A (Presente) = {presente}")
        print(f"   ➡️ Número de Marco   = {numero_marco}")

        # ---------------- MANEJO DE FALLO DE PÁGINA ----------------
        if presente == 0:
            self.fallos_pagina += 1
            print(f"   ❌ FALLO DE PÁGINA: La página {numero_pagina} no está cargada en memoria.")

            marco_asignado = None

            # Buscar marco libre
            marco_libre = self._encontrar_marco_libre()
            if marco_libre is not None:
                nueva_entrada = (marco_libre & self.MASK_MARCO) | self.MASK_PRESENTE
                self.tabla_de_paginas[numero_pagina] = nueva_entrada
                self.marcos_ocupados.add(marco_libre)
                self.frecuencias_uso[numero_pagina] = 1
                marco_asignado = marco_libre
                print(f"   🆕 Se cargó la página {numero_pagina} en el marco libre {marco_libre}.")
            else:
                # Reemplazo LFU
                marco_asignado = self._reemplazar_pagina_LFU(numero_pagina)
                if marco_asignado is None:
                    print("   ❌ No se pudo realizar reemplazo: no hay páginas presentes.")
                    return None
                print(f"   ✅ Página {numero_pagina} ahora ocupa el marco {marco_asignado} después del reemplazo.")

            # Mostrar tabla actualizada
            self.imprimir_tabla_paginas_empaquetada()

            # 🔁 CONTINUAR AUTOMÁTICAMENTE CON LA TRADUCCIÓN DESPUÉS DEL REEMPLAZO
            numero_marco = marco_asignado
            direccion_fisica = (numero_marco << self.bits_desplazamiento) | desplazamiento
            print("\n3. Cálculo de la Dirección Física (tras el reemplazo):")
            if self.bits_marco > 0:
                print(f"   Marco binario: {imprimir_binario(numero_marco, self.bits_marco)}")
            print(f"   Desplazamiento binario: {imprimir_binario(desplazamiento, self.bits_desplazamiento)}")
            print("\n--- Resultado de la Traducción ---")
            print(f"Dirección Física: Decimal = {direccion_fisica}")
            print(f"                   Hexadecimal = 0x{direccion_fisica:X}")
            print(f"                   Binario ({self.bits_direccion_fisica} bits) = {imprimir_binario(direccion_fisica, self.bits_direccion_fisica)}")
            print(f"📈 Frecuencia de uso página {numero_pagina}: {self.frecuencias_uso[numero_pagina]}")
            print(f"🔢 Fallos de página acumulados: {self.fallos_pagina}")
            print("----------------------------------")
            return direccion_fisica

        # ---------------- PÁGINA PRESENTE ----------------
        self.frecuencias_uso[numero_pagina] = self.frecuencias_uso.get(numero_pagina, 0) + 1
        direccion_fisica = (numero_marco << self.bits_desplazamiento) | desplazamiento

        print(f"   ✅ La página está presente en el Marco {numero_marco}.")
        print("\n3. Cálculo de la Dirección Física:")
        if self.bits_marco > 0:
            print(f"   Marco binario: {imprimir_binario(numero_marco, self.bits_marco)}")
        print(f"   Desplazamiento binario: {imprimir_binario(desplazamiento, self.bits_desplazamiento)}")

        print("\n--- Resultado de la Traducción ---")
        print(f"Dirección Física: Decimal = {direccion_fisica}")
        print(f"                   Hexadecimal = 0x{direccion_fisica:X}")
        print(f"                   Binario ({self.bits_direccion_fisica} bits) = {imprimir_binario(direccion_fisica, self.bits_direccion_fisica)}")
        print(f"📈 Frecuencia de uso página {numero_pagina}: {self.frecuencias_uso[numero_pagina]}")
        print(f"🔢 Fallos de página acumulados: {self.fallos_pagina}")
        print("----------------------------------")
        return direccion_fisica
