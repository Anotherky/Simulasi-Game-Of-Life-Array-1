"""
Labirin Random + Penyelesaian Otomatis menggunakan Stack (DFS)
Struktur Data - Bab 7: Tumpukan (Stacks)

Konsep yang digunakan:
  - Stack (LIFO) untuk algoritma DFS
  - Recursive Backtracking untuk generate labirin
  - Backtracking path via parent dictionary
"""

import random
import time


# ============================================================
#  KELAS STACK  (implementasi manual, sesuai materi Bab 7)
# ============================================================

class Stack:
    """Implementasi Stack dengan Python List (LIFO)."""

    def __init__(self):
        self._data = []

    def push(self, item):
        """Tambahkan item ke puncak stack."""
        self._data.append(item)

    def pop(self):
        """Hapus dan kembalikan item teratas. Raise jika kosong."""
        if self.is_empty():
            raise IndexError("pop dari stack kosong")
        return self._data.pop()

    def peek(self):
        """Lihat item teratas tanpa menghapus."""
        if self.is_empty():
            raise IndexError("peek dari stack kosong")
        return self._data[-1]

    def is_empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"Stack(top={self._data[-1] if self._data else 'kosong'}, size={len(self._data)})"


# ============================================================
#  GENERATE LABIRIN  (Recursive Backtracking via Stack)
# ============================================================

def generate_maze(rows: int, cols: int) -> list[list[int]]:
    """
    Buat labirin acak dengan algoritma Recursive Backtracking.
    Menggunakan stack iteratif agar sesuai tema Bab 7.

    Grid:  1 = dinding,  0 = jalan

    Ukuran rows dan cols harus ganjil agar grid simetris.
    """
    # Pastikan dimensi ganjil
    if rows % 2 == 0:
        rows += 1
    if cols % 2 == 0:
        cols += 1

    grid = [[1] * cols for _ in range(rows)]

    # Stack untuk iterative DFS generator
    gen_stack = Stack()
    start_r, start_c = 1, 1
    grid[start_r][start_c] = 0
    gen_stack.push((start_r, start_c))

    while not gen_stack.is_empty():
        r, c = gen_stack.peek()

        # Cari tetangga yang belum dikunjungi (jarak 2 sel)
        neighbors = []
        for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nr, nc = r + dr, c + dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and grid[nr][nc] == 1:
                neighbors.append((nr, nc, r + dr // 2, c + dc // 2))

        if neighbors:
            nr, nc, wr, wc = random.choice(neighbors)
            grid[wr][wc] = 0   # buka dinding di antara
            grid[nr][nc] = 0   # buka sel tujuan
            gen_stack.push((nr, nc))
        else:
            gen_stack.pop()    # backtrack

    return grid


# ============================================================
#  SOLVER  (DFS dengan Stack — inti materi Bab 7)
# ============================================================

def solve_maze_dfs(grid: list[list[int]],
                   start: tuple[int, int],
                   end: tuple[int, int]) -> tuple[list[tuple], int]:
    """
    Selesaikan labirin dengan DFS menggunakan Stack.

    Parameters
    ----------
    grid  : grid labirin (1=dinding, 0=jalan)
    start : koordinat (row, col) titik awal
    end   : koordinat (row, col) titik akhir

    Returns
    -------
    path        : list koordinat dari start ke end  (kosong jika tidak ada)
    steps_count : jumlah langkah yang diambil selama pencarian
    """
    rows = len(grid)
    cols = len(grid[0])

    stack = Stack()
    stack.push(start)

    visited = set()
    visited.add(start)

    parent = {start: None}   # untuk rekonstruksi jalur
    steps = 0

    while not stack.is_empty():
        current = stack.pop()
        steps += 1

        # Cek apakah sudah sampai tujuan
        if current == end:
            path = _reconstruct_path(parent, end)
            return path, steps

        r, c = current
        # Eksplorasi 4 arah: atas, bawah, kiri, kanan
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)
            if (0 <= nr < rows and 0 <= nc < cols
                    and grid[nr][nc] == 0
                    and neighbor not in visited):
                visited.add(neighbor)
                parent[neighbor] = current
                stack.push(neighbor)

    return [], steps   # tidak ada solusi


def _reconstruct_path(parent: dict,
                       end: tuple[int, int]) -> list[tuple[int, int]]:
    """Rekonstruksi jalur dari dict parent (backtrack dari end ke start)."""
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


# ============================================================
#  TAMPILAN TERMINAL
# ============================================================

WALL  = "██"
PATH  = "  "
START = " S"
END   = " E"
ROUTE = " ·"
HEAD  = " @"


def print_maze(grid: list[list[int]],
               start: tuple[int, int],
               end: tuple[int, int],
               path: list[tuple[int, int]] | None = None,
               current: tuple[int, int] | None = None) -> None:
    """Cetak labirin ke terminal dengan simbol ASCII."""
    path_set = set(path) if path else set()
    rows = len(grid)
    cols = len(grid[0])

    # Border atas
    print("+" + "──" * cols + "+")

    for r in range(rows):
        row_str = "|"
        for c in range(cols):
            pos = (r, c)
            if pos == start:
                row_str += START
            elif pos == end:
                row_str += END
            elif current and pos == current:
                row_str += HEAD
            elif pos in path_set:
                row_str += ROUTE
            elif grid[r][c] == 1:
                row_str += WALL
            else:
                row_str += PATH
        row_str += "|"
        print(row_str)

    # Border bawah
    print("+" + "──" * cols + "+")


def print_separator(char: str = "─", width: int = 60) -> None:
    print(char * width)


# ============================================================
#  ANIMASI LANGKAH-LANGKAH DFS  (opsional, mode verbose)
# ============================================================

def solve_maze_animated(grid: list[list[int]],
                        start: tuple[int, int],
                        end: tuple[int, int],
                        delay: float = 0.05) -> tuple[list[tuple], int]:
    """
    Versi animasi DFS: cetak setiap langkah ke terminal.
    Tekan Ctrl+C untuk skip animasi.
    """
    import os

    rows = len(grid)
    cols = len(grid[0])

    stack = Stack()
    stack.push(start)
    visited = set([start])
    parent = {start: None}
    steps = 0

    try:
        while not stack.is_empty():
            current = stack.pop()
            steps += 1

            # Cetak keadaan saat ini
            os.system("cls" if os.name == "nt" else "clear")
            print(f"  Langkah: {steps:4d}  |  Stack size: {len(stack):3d}  |  Dikunjungi: {len(visited):4d}")
            print_separator()
            print_maze(grid, start, end, list(visited), current)
            print_separator()
            print(f"  Posisi sekarang : {current}")
            print(f"  Stack (peek)    : {stack.peek() if not stack.is_empty() else '(kosong)'}")
            time.sleep(delay)

            if current == end:
                path = _reconstruct_path(parent, end)
                return path, steps

            r, c = current
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                neighbor = (nr, nc)
                if (0 <= nr < rows and 0 <= nc < cols
                        and grid[nr][nc] == 0
                        and neighbor not in visited):
                    visited.add(neighbor)
                    parent[neighbor] = current
                    stack.push(neighbor)

    except KeyboardInterrupt:
        print("\n  [Animasi dihentikan, menyelesaikan tanpa animasi...]")
        return solve_maze_dfs(grid, start, end)

    return [], steps


# ============================================================
#  MENU UTAMA
# ============================================================

def main():
    print_separator("=")
    print("  LABIRIN RANDOM + SOLVER OTOMATIS")
    print("  Struktur Data — Bab 7: Tumpukan (Stack + DFS)")
    print_separator("=")

    # --- Pilih ukuran ---
    print("\nPilih ukuran labirin:")
    print("  1. Kecil  (11 × 11)")
    print("  2. Sedang (17 × 17)")
    print("  3. Besar  (23 × 23)")
    print("  4. Kustom")

    pilihan = input("\nMasukkan pilihan [1-4]: ").strip()
    if pilihan == "1":
        rows = cols = 11
    elif pilihan == "2":
        rows = cols = 17
    elif pilihan == "3":
        rows = cols = 23
    elif pilihan == "4":
        try:
            rows = int(input("  Baris  (ganjil, min 5): "))
            cols = int(input("  Kolom  (ganjil, min 5): "))
            rows = max(5, rows)
            cols = max(5, cols)
        except ValueError:
            print("  Input tidak valid, pakai 11×11.")
            rows = cols = 11
    else:
        rows = cols = 11

    # --- Mode animasi ---
    mode = input("\nTampilkan animasi langkah DFS? (y/n) [default: n]: ").strip().lower()
    animated = mode == "y"

    # --- Generate labirin ---
    print("\nMembuat labirin...")
    random.seed()          # seed acak setiap kali dijalankan
    grid = generate_maze(rows, cols)

    start = (1, 1)
    end   = (rows - 2, cols - 2)

    print("\nLabirin awal (sebelum diselesaikan):")
    print_separator()
    print_maze(grid, start, end)
    print_separator()

    # --- Selesaikan ---
    print("\nMenyelesaikan labirin dengan DFS Stack...")
    if animated and rows <= 17:
        path, steps = solve_maze_animated(grid, start, end, delay=0.03)
    else:
        if animated:
            print("  (Labirin terlalu besar untuk animasi, langsung selesaikan)")
        path, steps = solve_maze_dfs(grid, start, end)

    # --- Hasil ---
    print_separator("=")
    print("  HASIL")
    print_separator("=")

    if path:
        print(f"\n  Status      : JALUR DITEMUKAN!")
        print(f"  Panjang jalur: {len(path)} langkah")
        print(f"  Total eksplorasi: {steps} sel")
        print(f"  Efisiensi   : {len(path)/steps*100:.1f}% (jalur/eksplorasi)\n")
        print("Labirin dengan jalur solusi (·):")
        print_separator()
        print_maze(grid, start, end, path)
        print_separator()
    else:
        print("\n  Status: TIDAK ADA JALUR yang ditemukan.")
        print(f"  Total eksplorasi: {steps} langkah\n")

    # --- Info Stack ---
    print_separator()
    print("  Ringkasan konsep Stack yang dipakai:")
    print("  - push()  : setiap tetangga valid dimasukkan ke stack")
    print("  - pop()   : ambil sel berikutnya untuk dieksplorasi (LIFO)")
    print("  - parent[]: simpan jalur balik untuk rekonstruksi solusi")
    print("  - Backtracking otomatis karena urutan LIFO stack")
    print_separator()

    # --- Ulangi? ---
    lagi = input("\nBuat labirin baru? (y/n): ").strip().lower()
    if lagi == "y":
        main()
    else:
        print("\nSelesai. Sampai jumpa!")


if __name__ == "__main__":
    main()