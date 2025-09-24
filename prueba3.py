from collections import deque, OrderedDict

# ======= Algoritmos de reemplazo =======
def fifo_replacement(trace, num_frames):
    frames, in_frame, faults, timeline = deque(), set(), 0, []
    for page in trace:
        hit = page in in_frame
        if not hit:
            faults += 1
            if len(frames) < num_frames:
                frames.append(page)
                in_frame.add(page)
            else:
                old = frames.popleft()
                in_frame.remove(old)
                frames.append(page)
                in_frame.add(page)
        timeline.append((page, list(frames), hit))
    return {"faults": faults, "timeline": timeline}

def lru_replacement(trace, num_frames):
    frames, faults, timeline = OrderedDict(), 0, []
    for page in trace:
        hit = page in frames
        if hit:
            frames.move_to_end(page)
        else:
            faults += 1
            if len(frames) >= num_frames:
                frames.popitem(last=False)
            frames[page] = True
        timeline.append((page, list(frames.keys()), hit))
    return {"faults": faults, "timeline": timeline}


# ======= Entrada de datos =======
print("=== Simulador de memoria virtual con reemplazo de páginas ===")

# Tamaños básicos
virtual_size = int(input("Tamaño de memoria virtual (bytes, potencia de 2): "))
physical_size = int(input("Tamaño de memoria física (bytes, potencia de 2): "))
page_size = int(input("Tamaño de página (bytes, potencia de 2): "))

# Cálculos
num_pages = virtual_size // page_size
num_frames = physical_size // page_size
print(f"\nNúmero de páginas virtuales: {num_pages}")
print(f"Número de marcos físicos: {num_frames}")

# Construcción de tabla de páginas
print("\nIngrese el mapeo de la tabla de páginas (use -1 si la página no está cargada):")
page_table = {}
for i in range(num_pages):
    marco = int(input(f"Página {i} -> Marco: "))
    page_table[i] = marco

# Entrada de direcciones virtuales (en hex)
print("\nIngrese direcciones virtuales en HEX (ejemplo: 0x1F 0x20 0xAB):")
virtual_addrs = [int(x, 16) for x in input().split()]

# Traducción a direcciones físicas
physical_addrs, page_trace = [], []
print("\n=== Traducción de direcciones ===")
for va in virtual_addrs:
    page = va // page_size
    offset = va % page_size
    marco = page_table.get(page, -1)

    print(f"VA {hex(va)}:")
    print(f"   Página virtual = {page}")
    print(f"   Desplazamiento = {offset} (dec) -> {bin(offset)} (bin) -> {hex(offset)} (hex)")

    if marco == -1:
        print("   -> Fallo de página (no asignado)\n")
        physical_addrs.append(None)
    else:
        pa = marco * page_size + offset
        physical_addrs.append(pa)
        page_trace.append(page)
        print(f"   Marco asignado = {marco}")
        print(f"   Dirección física = {bin(pa)} (bin) -> {hex(pa)} (hex)\n")

# Ejecutar algoritmos de reemplazo
print("\n=== Comparación de algoritmos de reemplazo ===")
fifo_res = fifo_replacement(page_trace, num_frames)
lru_res = lru_replacement(page_trace, num_frames)

print(f"FIFO: Fallos = {fifo_res['faults']}")
print(f"LRU : Fallos = {lru_res['faults']}")

print("\nDetalle de accesos:")
print("Acceso | FIFO (hit?) | LRU (hit?)")
for i, page in enumerate(page_trace):
    f_page, f_frames, f_hit = fifo_res['timeline'][i]
    l_page, l_frames, l_hit = lru_res['timeline'][i]
    print(f"{page:6} | {f_frames!s:12} ({'H' if f_hit else 'M'}) | {l_frames!s:12} ({'H' if l_hit else 'M'})")
