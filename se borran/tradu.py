
    def traducir(self, direccion_virtual_hex_str):
        """
        Realiza la traducción de una dirección virtual (DV) a una dirección física (DF).
        Devuelve la dirección física (int) o None si hay fallo de página / error.
        """
        
        try:
            direccion_virtual = int(str(direccion_virtual_hex_str), 16)
        except ValueError:
            print(f"\n   ❌ Error: Dirección virtual '{direccion_virtual_hex_str}' no es un formato hexadecimal válido.")
            
            
        max_bits_dv = self.bits_pagina_virtual + self.bits_desplazamiento  # Bits para representar la DV
        print(f"\n--- Traduciendo Dirección Virtual: {direccion_virtual_hex_str} (0x{direccion_virtual:X}) ---")
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
