# Programa Python: Transformación de direcciones y comparación de reemplazo de páginas (FIFO vs LRU)

from collections import deque, OrderedDict

# --- Funciones de direcciones ---
def split_address(bin_str, offset_bits):
    total_bits = len(bin_str)
    page_bits = total_bits - offset_bits
    page_bin = bin_str[:page_bits]
    offset_bin = bin_str[page_bits:]
    return page_bin, offset_bin

def pretty_print_address_info(name, bin_str, offset_bits):
    page_bin, offset_bin = split_address(bin_str, offset_bits)
    page_val = int(page_bin, 2)
    offset_val = int(offset_bin, 2)
    full_val = int(bin_str, 2)
    print(f"--- {name} ---")
    print(f"Longitud total (bits): {len(bin_str)}")
    print(f"Offset (bits): {offset_bits}")
    print(f"Bits de página: {len(page_bin)}")
    print(f"Página (bin): {page_bin}  -> (dec): {page_val}  -> (hex): {hex(page_val)}")
    print(f"Offset (bin): {offset_bin}  -> (dec): {offset_val}  -> (hex): {hex(offset_val)}")
    print(f"Dirección completa (bin): {bin_str}  -> (dec): {full_val}  -> (hex): {hex(full_val)}\n")

# --- Algoritmos de reemplazo ---
def fifo_replacement(trace, num_frames):
    frames = deque()
    in_frame = set()
    faults = 0
    timeline = []
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
    return {"faults": faults, "final_frames": list(frames), "timeline": timeline}

def lru_replacement(trace, num_frames):
    frames = OrderedDict()
    faults = 0
    timeline = []
    for page in trace:
        hit = page in frames
        if hit:
            frames.move_to_end(page)
        else:
            faults += 1
            if len(frames) < num_frames:
                frames[page] = True
            else:
                oldest = next(iter(frames))
                del frames[oldest]
                frames[page] = True
        timeline.append((page, list(frames.keys()), hit))
    return {"faults": faults, "final_frames": list(frames.keys()), "timeline": timeline}


# ================== DEMO ==================
virtual_bin = "01100010101010111100"   # dirección virtual (20 bits)
physical_bin = "0000111111001110"      # dirección física (16 bits)
offset_bits = 8                        # desplazamiento

# Info de direcciones
pretty_print_address_info("Dirección virtual", virtual_bin, offset_bits)
pretty_print_address_info("Dirección física", physical_bin, offset_bits)

# --- Cálculos de tamaños ---
virtual_address_bits = len(virtual_bin)
physical_address_bits = len(physical_bin)
page_size = 2 ** offset_bits
virtual_space = 2 ** virtual_address_bits
physical_space = 2 ** physical_address_bits
num_virtual_pages = virtual_space // page_size
num_physical_frames = physical_space // page_size

print("### Tamaños y capacidades ###")
print(f"Tamaño de página = {page_size} bytes")
print(f"Espacio de direcciones virtual = {virtual_space} bytes")
print(f"Memoria física = {physical_space} bytes")
print(f"Número de páginas virtuales = {num_virtual_pages}")
print(f"Número de marcos físicos = {num_physical_frames}\n")

# --- Traza de ejemplo ---
vpage_bin, _ = split_address(virtual_bin, offset_bits)
vpage = int(vpage_bin, 2)
page_trace = [2, 3, 2, 1, vpage, 4, 2, 3, 5, vpage, 6, 2, 7, 3, 2]
print("Traza de acceso a páginas:", page_trace, "\n")

# --- Comparación FIFO vs LRU ---
demo_frames = 4
fifo_res = fifo_replacement(page_trace, demo_frames)
lru_res = lru_replacement(page_trace, demo_frames)

print(f"Comparación (marcos = {demo_frames}):")
print(f"FIFO -> Fallos: {fifo_res['faults']} | Marcos finales: {fifo_res['final_frames']}")
print(f"LRU  -> Fallos: {lru_res['faults']} | Marcos finales: {lru_res['final_frames']}\n")

print("Detalle de los primeros accesos:")
print("Acceso | FIFO_frames (hit?)        | LRU_frames (hit?)")
for i, page in enumerate(page_trace[:12]):
    f_page, f_frames, f_hit = fifo_res['timeline'][i]
    l_page, l_frames, l_hit = lru_res['timeline'][i]
    print(f"{page:6} | {f_frames!s:22} ({'H' if f_hit else 'M'}) | {l_frames!s:22} ({'H' if l_hit else 'M'})")
