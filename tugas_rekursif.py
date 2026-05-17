#!/usr/bin/env python3
# ================================================================
#  TUGAS REKURSIF — Program Lengkap dengan Terminal UI
#  Soal 1 : N-Queens     (N-Ratu)
#  Soal 2 : Knight's Tour (Tur Kuda)
#  Soal 3 : Knapsack      (Masalah Karung)
#
#  Cara pakai:
#    python tugas_rekursif.py              → menu interaktif
#    python tugas_rekursif.py --soal 1     → langsung N-Queens
#    python tugas_rekursif.py --soal 2     → langsung Knight's Tour
#    python tugas_rekursif.py --soal 3     → langsung Knapsack
#    python tugas_rekursif.py --help       → tampilkan bantuan
#
#  Opsi tambahan:
#    --n    <int>    ukuran papan (soal 1 & 2)
#    --baris <int>   baris awal kuda (soal 2)
#    --kolom <int>   kolom awal kuda (soal 2)
#    --items <int..> daftar berat barang (soal 3)
#    --target <int>  target berat (soal 3)
#    --semua         tampilkan semua solusi
#    --no-color      nonaktifkan warna ANSI
# ================================================================

import argparse
import sys
import os
import time

# ----------------------------------------------------------------
#  WARNA ANSI — auto-disable jika terminal tidak mendukung
# ----------------------------------------------------------------
class C:
    """Namespace warna ANSI. Di-reset oleh --no-color."""
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    # Teks
    WHITE  = "\033[97m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"
    # Background
    BG_GREEN  = "\033[42m"
    BG_BLUE   = "\033[44m"
    BG_YELLOW = "\033[43m"
    BG_CYAN   = "\033[46m"
    BG_RED    = "\033[41m"
    BG_WHITE  = "\033[47m"

def disable_color():
    """Ganti semua atribut C menjadi string kosong."""
    for attr in vars(C):
        if not attr.startswith('_'):
            setattr(C, attr, "")

def colored(text, *codes):
    return "".join(codes) + str(text) + C.RESET

def header(title, width=50, color=C.CYAN):
    bar = "═" * width
    pad = (width - len(title) - 2) // 2
    print(f"\n{colored(bar, C.BOLD, color)}")
    print(colored(f"{'':>{pad}} {title} ", C.BOLD, color))
    print(f"{colored(bar, C.BOLD, color)}")

def subheader(title, width=50):
    print(f"\n{colored('─'*width, C.DIM)}")
    print(f" {colored(title, C.BOLD, C.WHITE)}")
    print(f"{colored('─'*width, C.DIM)}")

def ok(msg):   print(f"  {colored('✓', C.BOLD, C.GREEN)} {msg}")
def err(msg):  print(f"  {colored('✗', C.BOLD, C.RED)} {msg}")
def info(msg): print(f"  {colored('ℹ', C.BOLD, C.CYAN)} {msg}")
def warn(msg): print(f"  {colored('⚠', C.BOLD, C.YELLOW)} {msg}")

def prompt(label, default=None):
    """Input dengan label berwarna dan nilai default."""
    suffix = f" [{colored(default, C.DIM)}]" if default is not None else ""
    val = input(f"  {colored('›', C.BOLD, C.CYAN)} {label}{suffix}: ").strip()
    if val == "" and default is not None:
        return str(default)
    return val

def loading(msg, duration=0.4):
    """Animasi spinner sederhana."""
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    start  = time.time()
    i = 0
    while time.time() - start < duration:
        print(f"\r  {colored(frames[i % len(frames)], C.CYAN)} {msg}...", end="", flush=True)
        time.sleep(0.07)
        i += 1
    print(f"\r  {colored('✓', C.GREEN)} {msg}   ")

def press_enter():
    input(f"\n  {colored('[ Tekan Enter untuk lanjut ]', C.DIM)}")


# ================================================================
#  SOAL 1 — N-QUEENS
# ================================================================

def nq_is_safe(board, row, col, n):
    for r in range(row):
        if board[r] == col:
            return False
    r, c = row - 1, col - 1
    while r >= 0 and c >= 0:
        if board[r] == c: return False
        r -= 1; c -= 1
    r, c = row - 1, col + 1
    while r >= 0 and c < n:
        if board[r] == c: return False
        r -= 1; c += 1
    return True

def nq_solve(board, row, n, solutions):
    if row == n:
        solutions.append(board[:]); return
    for col in range(n):
        if nq_is_safe(board, row, col, n):
            board[row] = col
            nq_solve(board, row + 1, n, solutions)
            board[row] = -1

def nq_print_board(solution, n):
    """Cetak papan dengan warna."""
    border = colored("+" + ("───+" * n), C.DIM)
    print(f"  {border}")
    for row in range(n):
        row_str = colored("|", C.DIM)
        for col in range(n):
            if solution[row] == col:
                cell = colored(" Q ", C.BOLD, C.BG_GREEN, C.WHITE)
            else:
                # kotak terang/gelap selang-seling
                cell = colored(" · ", C.DIM) if (row + col) % 2 == 0 else colored("   ", C.DIM)
            row_str += cell + colored("|", C.DIM)
        print(f"  {row_str}")
        print(f"  {border}")

def run_nqueens(args):
    header("SOAL 1 — N-QUEENS (N-RATU)", color=C.GREEN)
    print(f"""
  {colored('Tujuan:', C.BOLD)} Tempatkan N ratu di papan N×N sehingga tidak ada
           dua ratu yang saling menyerang (baris, kolom, diagonal).
  {colored('Algoritma:', C.BOLD)} Backtracking Rekursif
""")

    # Ambil N
    if args.n:
        n = args.n
        info(f"Ukuran papan dari argumen: {colored(n, C.YELLOW)}")
    else:
        raw = prompt("Masukkan ukuran papan N (1–12)", default=8)
        try:
            n = int(raw)
        except ValueError:
            err("Input tidak valid."); return

    if not 1 <= n <= 12:
        err("N harus antara 1 dan 12."); return

    loading(f"Mencari semua solusi papan {n}×{n}")

    board, solutions = [-1] * n, []
    nq_solve(board, 0, n, solutions)

    if not solutions:
        warn(f"Tidak ada solusi untuk papan {n}×{n}."); return

    ok(f"Ditemukan {colored(len(solutions), C.BOLD, C.GREEN)} solusi untuk papan {n}×{n}.")

    # Pilihan tampil
    if args.semua:
        tampilkan_semua = True
    else:
        jawab = prompt("Tampilkan semua solusi? (y/n)", default="n").lower()
        tampilkan_semua = (jawab == 'y')

    if tampilkan_semua:
        for idx, sol in enumerate(solutions, 1):
            subheader(f"Solusi ke-{idx} / {len(solutions)}")
            nq_print_board(sol, n)
            print(f"  Posisi kolom: {colored([c+1 for c in sol], C.CYAN)}")
            if idx < len(solutions):
                lanjut = prompt("Lanjut ke solusi berikutnya? (y/n)", default="y").lower()
                if lanjut != 'y': break
    else:
        # Navigasi solusi interaktif
        idx = 0
        while True:
            subheader(f"Solusi ke-{idx+1} / {len(solutions)}")
            nq_print_board(solutions[idx], n)
            print(f"  Posisi kolom: {colored([c+1 for c in solutions[idx]], C.CYAN)}")
            print()
            print(f"  {colored('[p]', C.BOLD)} Sebelumnya  "
                  f"{colored('[n]', C.BOLD)} Berikutnya  "
                  f"{colored('[q]', C.BOLD)} Kembali ke menu")
            nav = prompt("Navigasi", default="q").lower()
            if nav == 'n':
                idx = min(idx + 1, len(solutions) - 1)
            elif nav == 'p':
                idx = max(idx - 1, 0)
            else:
                break


# ================================================================
#  SOAL 2 — KNIGHT'S TOUR
# ================================================================

KT_MOVES = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]

def kt_is_valid(r, c, n, board):
    return 0 <= r < n and 0 <= c < n and board[r][c] == -1

def kt_degree(r, c, n, board):
    return sum(1 for dr, dc in KT_MOVES if kt_is_valid(r+dr, c+dc, n, board))

def kt_solve(board, r, c, move_num, n, path):
    if move_num == n * n:
        return True
    next_moves = []
    for dr, dc in KT_MOVES:
        nr, nc = r + dr, c + dc
        if kt_is_valid(nr, nc, n, board):
            next_moves.append((kt_degree(nr, nc, n, board), nr, nc))
    next_moves.sort()
    for _, nr, nc in next_moves:
        board[nr][nc] = move_num
        path.append((nr, nc))
        if kt_solve(board, nr, nc, move_num + 1, n, path):
            return True
        board[nr][nc] = -1
        path.pop()
    return False

def kt_print_board(board, n, start=None, highlight=None):
    """Cetak papan tur kuda dengan warna."""
    cell_w = len(str(n * n)) + 2
    border_cell = "─" * cell_w + "┼"
    border = colored("├" + border_cell * n, C.DIM)
    top    = colored("┌" + ("─"*cell_w + "┬") * (n-1) + "─"*cell_w + "┐", C.DIM)
    bot    = colored("└" + ("─"*cell_w + "┴") * (n-1) + "─"*cell_w + "┘", C.DIM)
    vsep   = colored("│", C.DIM)

    print(f"  {top}")
    for r in range(n):
        row_str = f"  {vsep}"
        for c in range(n):
            val = board[r][c]
            num = str(val).rjust(cell_w - 1) + " "
            if start and (r, c) == start:
                cell = colored(num, C.BOLD, C.BG_YELLOW, "\033[30m")
            elif highlight and (r, c) == highlight:
                cell = colored(num, C.BOLD, C.BG_GREEN, C.WHITE)
            elif val >= 0:
                # gradasi dari biru ke putih berdasarkan urutan
                cell = colored(num, C.CYAN)
            else:
                cell = colored(num, C.DIM)
            row_str += cell + vsep
        print(row_str)
        if r < n - 1:
            print(f"  {border}")
    print(f"  {bot}")

def kt_print_path(path, n):
    print()
    subheader("Urutan Langkah Kuda")
    per_row = 6
    for i, (r, c) in enumerate(path):
        badge = colored(f" {i+1:3d}:({r},{c}) ", C.CYAN if i % 2 == 0 else C.BLUE)
        print(badge, end="\n" if (i + 1) % per_row == 0 else "")
    print()

def run_knights_tour(args):
    header("SOAL 2 — KNIGHT'S TOUR (TUR KUDA)", color=C.CYAN)
    print(f"""
  {colored('Tujuan:', C.BOLD)} Temukan urutan langkah kuda sehingga mengunjungi
           setiap petak tepat satu kali.
  {colored('Algoritma:', C.BOLD)} Backtracking Rekursif + Heuristik Warnsdorff
""")

    # Ukuran papan
    if args.n:
        n = args.n
        info(f"Ukuran papan dari argumen: {colored(n, C.YELLOW)}")
    else:
        raw = prompt("Ukuran papan N (5–8 disarankan)", default=8)
        try: n = int(raw)
        except ValueError: err("Input tidak valid."); return

    if n < 3:
        err("Papan minimal 3×3."); return

    # Baris awal
    if args.baris is not None:
        sr = args.baris
        info(f"Baris awal dari argumen: {colored(sr, C.YELLOW)}")
    else:
        raw = prompt(f"Posisi awal BARIS  (0 s/d {n-1})", default=0)
        try: sr = int(raw)
        except ValueError: err("Input tidak valid."); return

    # Kolom awal
    if args.kolom is not None:
        sc = args.kolom
        info(f"Kolom awal dari argumen: {colored(sc, C.YELLOW)}")
    else:
        raw = prompt(f"Posisi awal KOLOM  (0 s/d {n-1})", default=0)
        try: sc = int(raw)
        except ValueError: err("Input tidak valid."); return

    if not (0 <= sr < n and 0 <= sc < n):
        err(f"Posisi ({sr},{sc}) di luar papan {n}×{n}."); return

    loading(f"Menjalankan algoritma pada papan {n}×{n} dari ({sr},{sc})")

    board = [[-1]*n for _ in range(n)]
    board[sr][sc] = 0
    path  = [(sr, sc)]
    found = kt_solve(board, sr, sc, 1, n, path)

    if not found:
        err("Tidak ada tur lengkap dari posisi tersebut.")
        warn("Coba posisi awal atau ukuran papan yang berbeda."); return

    ok(f"Tur kuda berhasil! {colored(f'{n*n} langkah', C.BOLD, C.GREEN)} telah diselesaikan.\n")

    subheader(f"Papan {n}×{n}  (angka = urutan kunjungan, kuning = start)")
    kt_print_board(board, n, start=(sr, sc))
    kt_print_path(path, n)

    # Mode animasi opsional
    anim = prompt("Tampilkan animasi langkah demi langkah? (y/n)", default="n").lower()
    if anim == 'y':
        speed_raw = prompt("Kecepatan animasi (1=lambat, 2=sedang, 3=cepat)", default="2")
        speeds = {"1": 0.4, "2": 0.15, "3": 0.05}
        delay  = speeds.get(speed_raw.strip(), 0.15)

        tmp_board = [[-1]*n for _ in range(n)]
        tmp_board[sr][sc] = 0
        for step, (r, c) in enumerate(path):
            os.system('cls' if os.name == 'nt' else 'clear')
            header("KNIGHT'S TOUR — Animasi", color=C.CYAN)
            print(f"\n  Langkah: {colored(step+1, C.BOLD, C.GREEN)} / {n*n}")
            kt_print_board(tmp_board, n, start=(sr, sc), highlight=(r, c))
            if step + 1 < len(path):
                nr, nc = path[step + 1]
                tmp_board[nr][nc] = step + 1
            time.sleep(delay)
        ok("Animasi selesai!")


# ================================================================
#  SOAL 3 — KNAPSACK
# ================================================================

def ks_solve_one(items, target, index, chosen, result):
    if target == 0:
        result.append(chosen[:]); return True
    if index >= len(items) or target < 0:
        return False
    chosen.append(items[index])
    if ks_solve_one(items, target - items[index], index + 1, chosen, result):
        return True
    chosen.pop()
    return ks_solve_one(items, target, index + 1, chosen, result)

def ks_solve_all(items, target, index, chosen, all_results):
    if target == 0:
        all_results.append(chosen[:]); return
    if index >= len(items) or target < 0:
        return
    chosen.append(items[index])
    ks_solve_all(items, target - items[index], index + 1, chosen, all_results)
    chosen.pop()
    ks_solve_all(items, target, index + 1, chosen, all_results)

def ks_find_best(items, target):
    """Cari kombinasi mendekati target (≤ target) jika tepat tidak ada."""
    best, best_combo = [0], [[]]
    def rec(idx, remaining, current):
        total = target - remaining
        if total > best[0]:
            best[0] = total
            best_combo[0] = current[:]
        if idx >= len(items): return
        for i in range(idx, len(items)):
            if items[i] <= remaining:
                current.append(items[i])
                rec(i + 1, remaining - items[i], current)
                current.pop()
    rec(0, target, [])
    return best[0], best_combo[0]

def ks_print_solution(items, chosen, target, label="Solusi"):
    not_chosen = items[:]
    for w in chosen:
        not_chosen.remove(w)
    total = sum(chosen)

    pct   = int((total / target) * 40) if target > 0 else 0
    bar   = colored("█" * pct, C.GREEN) + colored("░" * (40 - pct), C.DIM)

    print(f"\n  {colored('┌─ ' + label, C.BOLD, C.GREEN)}")
    print(f"  {colored('│', C.GREEN)}  Target berat  : {colored(target, C.BOLD, C.WHITE)} pon")
    print(f"  {colored('│', C.GREEN)}  Total dipilih : {colored(total, C.BOLD, C.GREEN)} pon")
    print(f"  {colored('│', C.GREEN)}  Kapasitas     : [{bar}] {total}/{target}")
    print(f"  {colored('└─', C.GREEN)}")

    print(f"\n  {colored('Dipilih  :', C.BOLD, C.GREEN)} ", end="")
    for w in sorted(chosen):
        print(colored(f" {w}kg ", C.BOLD, C.BG_GREEN, C.WHITE), end=" ")
    print()

    if not_chosen:
        print(f"  {colored('Dilewati :', C.BOLD, C.DIM)}  ", end="")
        for w in sorted(not_chosen):
            print(colored(f" {w}kg ", C.DIM), end=" ")
        print()

    print(f"\n  {colored('Visualisasi bar:', C.BOLD)}")
    max_w = max(chosen) if chosen else 1
    for w in sorted(chosen):
        bar_len = int((w / max_w) * 30)
        print(f"  {colored(f'{w:4d} pon', C.CYAN)}  {colored('█'*bar_len, C.GREEN)}")

def run_knapsack(args):
    header("SOAL 3 — KNAPSACK (MASALAH KARUNG)", color=C.YELLOW)
    print(f"""
  {colored('Tujuan:', C.BOLD)} Pilih kombinasi barang agar total berat
           tepat sama dengan target (atau mendekati).
  {colored('Algoritma:', C.BOLD)} Rekursif Backtracking (include/exclude)
""")

    # Daftar barang
    if args.items:
        items = args.items
        info(f"Barang dari argumen: {colored(items, C.YELLOW)}")
    else:
        raw = prompt("Berat barang (pisah spasi)", default="2 5 6 9 12 14 20")
        try:
            items = list(map(int, raw.split()))
        except ValueError:
            err("Input tidak valid."); return

    if not items:
        err("Daftar barang kosong."); return

    # Target
    if args.target:
        target = args.target
        info(f"Target dari argumen: {colored(target, C.YELLOW)}")
    else:
        raw = prompt("Target berat knapsack (pon)", default=30)
        try:
            target = int(raw)
        except ValueError:
            err("Input tidak valid."); return

    print(f"\n  {colored('Barang tersedia :', C.BOLD)} {colored(items, C.CYAN)}")
    print(f"  {colored('Jumlah barang   :', C.BOLD)} {len(items)} item")
    print(f"  {colored('Target berat    :', C.BOLD)} {colored(target, C.YELLOW)} pon")

    # Mode: satu / semua
    if args.semua:
        mode = "2"
    elif args.items and args.target:
        # semua argumen sudah disuplai via CLI, pakai default tanpa prompt
        mode = "1"
        info("Mode: satu solusi (gunakan --semua untuk semua solusi)")
    else:
        mode = prompt("\nCari (1) Satu solusi  atau (2) Semua solusi? [1/2]", default="1")

    loading("Menjalankan algoritma rekursif")

    if mode == "2":
        all_results = []
        ks_solve_all(items, target, 0, [], all_results)
        if not all_results:
            warn(f"Tidak ada kombinasi yang totalnya tepat {target} pon.")
            best_total, best_combo = ks_find_best(items, target)
            if best_combo:
                info(f"Kombinasi terbaik mendekati target:")
                ks_print_solution(items, best_combo, target, label="Solusi Terbaik (mendekati)")
            return
        ok(f"Ditemukan {colored(len(all_results), C.BOLD, C.GREEN)} kombinasi valid.\n")
        for i, sol in enumerate(all_results, 1):
            ks_print_solution(items, sol, target, label=f"Kombinasi ke-{i}")
            if i < len(all_results):
                lanjut = prompt("Tampilkan kombinasi berikutnya? (y/n)", default="y").lower()
                if lanjut != 'y': break
    else:
        result = []
        found  = ks_solve_one(items, target, 0, [], result)
        if not found:
            warn(f"Tidak ada kombinasi yang totalnya tepat {target} pon.")
            best_total, best_combo = ks_find_best(items, target)
            if best_combo:
                info(f"Menampilkan kombinasi terbaik ({best_total} pon dari target {target} pon):")
                ks_print_solution(items, best_combo, target, label="Solusi Terbaik (mendekati)")
            return
        ks_print_solution(items, result[0], target)


# ================================================================
#  MENU UTAMA
# ================================================================

MENU_ITEMS = [
    ("1", "N-Queens      (N-Ratu)",       C.GREEN,   run_nqueens),
    ("2", "Knight's Tour (Tur Kuda)",      C.CYAN,    run_knights_tour),
    ("3", "Knapsack      (Masalah Karung)",C.YELLOW,  run_knapsack),
    ("0", "Keluar",                        C.RED,     None),
]

def print_main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    w = 52
    print()
    print(colored("  ╔" + "═"*(w-2) + "╗", C.CYAN))
    print(colored("  ║" + " "*(w-2) + "║", C.CYAN))
    title = "PROGRAM REKURSIF & BACKTRACKING"
    pad   = (w - 2 - len(title)) // 2
    print(colored(f"  ║{' '*pad}{title}{' '*(w-2-pad-len(title))}║", C.BOLD, C.CYAN))
    sub   = "Tugas Struktur Data & Algoritma"
    pad2  = (w - 2 - len(sub)) // 2
    print(colored(f"  ║{' '*pad2}{sub}{' '*(w-2-pad2-len(sub))}║", C.DIM))
    print(colored("  ║" + " "*(w-2) + "║", C.CYAN))
    print(colored("  ╚" + "═"*(w-2) + "╝", C.CYAN))
    print()

    for key, label, color, _ in MENU_ITEMS:
        bullet = colored(f"  [{key}]", C.BOLD, color)
        print(f"{bullet}  {colored(label, color if key != '0' else C.DIM)}")

    print()
    print(colored("  ─"*26, C.DIM))
    print(f"  {colored('Tip:', C.BOLD)} Jalankan dengan flag untuk skip menu:")
    print(f"  {colored('python tugas_rekursif.py --soal 1 --n 8', C.DIM)}")
    print(colored("  ─"*26, C.DIM))
    print()

def main():
    parser = argparse.ArgumentParser(
        prog="tugas_rekursif.py",
        description="Program Rekursif: N-Queens, Knight's Tour, Knapsack",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Contoh penggunaan:
  python tugas_rekursif.py                        # menu interaktif
  python tugas_rekursif.py --soal 1               # N-Queens interaktif
  python tugas_rekursif.py --soal 1 --n 6 --semua # N-Queens 6x6 semua solusi
  python tugas_rekursif.py --soal 2 --n 8 --baris 0 --kolom 0
  python tugas_rekursif.py --soal 3 --items 2 5 6 9 12 14 20 --target 30
  python tugas_rekursif.py --soal 3 --semua --items 1 3 5 7 --target 10
"""
    )
    parser.add_argument("--soal",   type=int, choices=[1,2,3],
                        help="Pilih soal langsung: 1=N-Queens, 2=Knight's Tour, 3=Knapsack")
    parser.add_argument("--n",      type=int,
                        help="Ukuran papan N (soal 1 & 2)")
    parser.add_argument("--baris",  type=int,
                        help="Baris awal kuda, mulai 0 (soal 2)")
    parser.add_argument("--kolom",  type=int,
                        help="Kolom awal kuda, mulai 0 (soal 2)")
    parser.add_argument("--items",  type=int, nargs="+",
                        help="Daftar berat barang (soal 3), cth: --items 2 5 9 14")
    parser.add_argument("--target", type=int,
                        help="Target berat knapsack (soal 3)")
    parser.add_argument("--semua",  action="store_true",
                        help="Tampilkan semua solusi yang ditemukan")
    parser.add_argument("--no-color", action="store_true",
                        help="Nonaktifkan warna ANSI (berguna jika terminal tidak mendukung)")

    args = parser.parse_args()

    if args.no_color or not sys.stdout.isatty():
        disable_color()

    runners = {1: run_nqueens, 2: run_knights_tour, 3: run_knapsack}

    if args.soal:
        # Mode langsung — jalankan soal tanpa menu
        runners[args.soal](args)
        print()
    else:
        # Mode interaktif — tampilkan menu
        while True:
            print_main_menu()
            pilihan = prompt("Pilih menu [0–3]", default="0")

            if pilihan == "0":
                print(f"\n  {colored('Sampai jumpa!', C.BOLD, C.CYAN)}\n")
                break
            elif pilihan in runners:
                try:
                    runners[int(pilihan)](args)
                except KeyboardInterrupt:
                    print(f"\n\n  {colored('Dibatalkan.', C.YELLOW)}")
                press_enter()
            else:
                warn("Pilihan tidak valid. Masukkan 0, 1, 2, atau 3.")
                time.sleep(1)


if __name__ == "__main__":
    main()
