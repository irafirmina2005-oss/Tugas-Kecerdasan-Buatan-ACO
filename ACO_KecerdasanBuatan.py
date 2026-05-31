import random

# Graph berdasarkan gambar 
graph = {
    '#': {'A': 3, 'C': 2, 'G': 5},
    'A': {'#': 3, 'C': 6},
    'B': {'C': 9, 'D': 8},
    'C': {'#': 2, 'A': 6, 'B': 9, 'F': 4},
    'D': {'B': 8, 'E': 7, 'H': 9},
    'E': {'D': 7, 'F': 2, 'G': 1, 'H': 1},
    'F': {'C': 4, 'E': 2},
    'G': {'#': 5, 'E': 1, 'H': 3},
    'H': {'D': 9, 'E': 1, 'G': 3}
}

# Titik Awal, Akhir, dan Titik Wajib Dilewati
start = 'H'
end = 'D'
mandatory_points = '#'

# Parameter ACO
num_ants = 20
num_iterations = 100
alpha = 1.0  # Pengaruh pheromone
beta = 2.0   # Pengaruh jarak 
evaporation_rate = 0.5   # Tingkat penguapan pheromone
Q = 100      # Konstanta untuk update pheromone

# Inisialisasi pheromone
pheromone = {}
for node in graph:
    pheromone[node] = {}
    for neighbor in graph[node]:
        pheromone[node][neighbor] = 1.0  # Inisialisasi pheromone awal

# Menghitung total jarak jalur
def hitung_jarak(jalur):
    total_jarak = 0
    for i in range(len(jalur) - 1):
        dari = jalur[i]
        ke = jalur[i + 1]   
        total_jarak += graph[dari][ke]
    return total_jarak

# Pemilihan jalur berdasarkan probabilitas (rumus probabilitas ACO)
def pilihan_berikutnya(posisi_sekarang, sudah_dikunjungi, node_target=None):
    kandidat = []
    for node in graph[posisi_sekarang]:
        if node in sudah_dikunjungi: 
            continue

        tau = pheromone[posisi_sekarang][node] ** alpha
        eta = (1.0 / graph[posisi_sekarang][node]) ** beta

        if node_target and node == node_target:
            nilai = tau * eta * 3.0  # Diberikan bobot lebih untuk mandatory point
        else:
            nilai = tau * eta
        
        kandidat.append((node, nilai))

    if not kandidat:
        return None
    
    total_nilai = sum(nilai for _, nilai in kandidat)  #Total probabilitas

    angka_acak = random.random()  #roulette wheel selection
    kumulatif = 0.0

    for node, nilai in kandidat:
        kumulatif += nilai / total_nilai
        if angka_acak <= kumulatif:
            return node
    return kandidat[-1][0]  # Fallback jika terjadi kesalahan

# Membangun jalur untuk setiap semut
def bangun_jalur():
    jalur = [start]
    sudah_dikunjungi = {start}
    posisi = start
    sudah_mandatory = False

    for langkah in range (50):  # H sampai # (Fase 1)
        if posisi == mandatory_points:
            sudah_mandatory = True
            break
        node_berikut = pilihan_berikutnya(posisi, sudah_dikunjungi, node_target=mandatory_points)
        if node_berikut is None:
            return None, float ('inf')  # Tidak ada jalur yang valid
        
        jalur.append(node_berikut)
        sudah_dikunjungi.add(node_berikut)
        posisi = node_berikut

    if not sudah_mandatory:
        return None, float('inf')  # Tidak melewati titik wajib
    
    for langkah in range(50):  # # sampai D (Fase 2)
        if posisi == end:
            break
        node_berikut = pilihan_berikutnya(posisi, sudah_dikunjungi, node_target=end)
        if node_berikut is None:
            return None, float('inf')  # Tidak ada jalur yang valid
        
        jalur.append(node_berikut)
        sudah_dikunjungi.add(node_berikut)
        posisi = node_berikut
    
    if posisi != end:
        return None, float('inf')  # Tidak mencapai tujuan akhir
    jarak_total = hitung_jarak(jalur)
    return jalur, jarak_total

# Update pheromone berdasarkan jalur yang ditemukan
def update_pheromone(hasil_semua_semut):
    for node in pheromone:
        for neighbor in pheromone[node]:
            pheromone[node][neighbor] *= (1 - evaporation_rate)  # Penguapan
            if pheromone[node][neighbor] < 0.0001:
                pheromone[node][neighbor] = 0.0001  # Batas minimum pheromone

    for jalur, jarak in hasil_semua_semut:
        if jalur is None or jarak == float('inf'):
            continue  # Lewati jalur yang tidak valid
       
        kontribusi = Q / jarak  # Kontribusi pheromone berdasarkan kualitas jalur

        for i in range(len(jalur) - 1):
            dari = jalur[i]
            ke = jalur[i + 1]
            pheromone[dari][ke] += kontribusi
            pheromone[ke][dari] += kontribusi  # Pheromone bersifat undirected

# Proses utama ACO
random.seed(42)  # Untuk hasil yang konsisten
best_jalur = None
best_jarak = float('inf')

print("=" * 50)
print("Algoritma Ant Colony Optimization (ACO)")
print("Travelling Salesman Problem dengan Titik Wajib Dilewati")
print("=" * 50)
print(f"Titik Awal: {start}")
print(f"Titik Akhir: {end}")    
print(f"Titik Wajib Dilewati: {mandatory_points}")
print(f"Jumlah Semut: {num_ants}")
print(f"Jumlah Iterasi: {num_iterations}")
print("=" * 50)

for i in range(1, num_iterations + 1):
    hasil_iterasi = []

    for semut in range(num_ants):  # Setiap semut membangun jalur
        jalur, jarak = bangun_jalur()
        hasil_iterasi.append((jalur, jarak))

        if jalur is not None and jarak < best_jarak:  # Update apabila jalur terbaik
            best_jalur = list(jalur)
            best_jarak = jarak
    update_pheromone(hasil_iterasi)  # Update pheromone setelah semua semut selesai

    if i % 10 == 0 or i == 1:
        valid = [j for _, j in hasil_iterasi if j != float('inf')]
        best_iterasi = min(valid) if valid else float('inf')
        print(f"Iterasi {i:3d} | Jalur Terbaik Iterasi: {best_iterasi}"
            f"| Jarak Terbaik Saat Ini: {best_jarak}")

#Menampilkan hasil akhir
print("=" * 50)
print("Hasil Akhir:")
if best_jalur:
    print(f"\n Jalur Terbaik: {' -> '.join(best_jalur)}")

    print(f"\n Detail:")
    total_jarak = 0
    for i in range(len(best_jalur) - 1):
        a = best_jalur[i]
        b = best_jalur[i + 1]
        d = graph[a][b]
        total_jarak += d
        print(f" {a} menuju {b} = {d} (total sejauh ini: {total_jarak})")

    print(f"\n Jarak Total: {total_jarak}")

    print(f"\n Syarat:")
    print(f" Titik Awal: {start} {'(terpenuhi)' if best_jalur[0] == start else '(tidak terpenuhi)'}")
    print(f" Titik Akhir: {end} {'(terpenuhi)' if best_jalur[-1] == end else '(tidak terpenuhi)'}")
    print(f" Titik Wajib Dilewati: {mandatory_points} {'(terpenuhi)' if all(point in best_jalur for point in mandatory_points) else '(tidak terpenuhi)'}")
else:
    print("Jalur tidak ditemukan.")

print("=" * 50)