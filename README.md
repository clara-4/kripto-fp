# Sistem Reservasi Ruang Belajar dengan RSA dan CSPRNG

## 📌 Deskripsi Proyek
Sistem ini merupakan implementasi algoritma **RSA (Rivest-Shamir-Adleman)** untuk mengamankan data reservasi ruang belajar. Proyek ini juga membandingkan performa dua metode **CSPRNG (Cryptographically Secure Pseudo-Random Number Generator)**, yaitu:
1. **Random Congruential Transition Method (RCTM)** - Metode deterministik berbasis Linear Congruential Generator (LCG).
2. **Hybrid Chaos-Modified Logistic Map (HC-MRLM)** - Metode berbasis chaos untuk meningkatkan keamanan.

Kedua metode tersebut digunakan untuk menghasilkan bilangan acak yang dipakai dalam pembentukan kunci publik dan privat RSA. Sistem ini memastikan bahwa token yang dihasilkan sulit untuk diprediksi atau diakses secara tidak sah.

## 📊 Hasil Pengujian
Hasil perbandingan **RCTM** dan **HC-MRLM** setelah diuji sebanyak **100 kali**:
| Metode  | Execution Time (ms) | CPU Usage (%) |
|---------|--------------------|--------------|
| RCTM    | Lebih cepat       | Lebih rendah |
| HC-MRLM | Lebih lambat       | Lebih tinggi |

### 🔍 Analisis Hasil Pengujian
- **Execution Time**: RCTM memiliki waktu eksekusi yang lebih cepat karena menggunakan operasi aritmatika sederhana, sedangkan HC-MRLM memerlukan perhitungan lebih kompleks.
- **CPU Usage**: RCTM lebih efisien dalam penggunaan CPU, sementara HC-MRLM membutuhkan lebih banyak sumber daya karena sifat chaos yang dimilikinya.

Kesimpulan:
- **RCTM** lebih cocok untuk aplikasi yang memprioritaskan **kecepatan dan efisiensi**.
- **HC-MRLM** lebih aman karena memiliki tingkat entropi lebih tinggi, tetapi mengorbankan performa.



## Dokumentasi

<img width="481" alt="image" src="https://github.com/user-attachments/assets/cb8637c2-b8f1-4203-a178-52e40f1a02af" />

<img width="481" alt="image" src="https://github.com/user-attachments/assets/4d71d888-47ac-4bcd-af7f-dff2a6f9819a" />

<img width="477" alt="image" src="https://github.com/user-attachments/assets/0ff26437-2ddf-4a23-b2d6-9c552c667237" />

<img width="479" alt="image" src="https://github.com/user-attachments/assets/76c638d0-7fed-413e-839c-54cba2952557" />

<img width="477" alt="image" src="https://github.com/user-attachments/assets/2259e077-b2c1-41f7-9ab9-d8936eb4c8c3" />

<img width="475" alt="image" src="https://github.com/user-attachments/assets/9d91afb5-470d-4fff-8cd1-c1e8779ed365" />

<img width="478" alt="image" src="https://github.com/user-attachments/assets/b177ac12-ec9e-4016-abcd-283374f5ea5e" />

<img width="478" alt="image" src="https://github.com/user-attachments/assets/c649a737-4625-4b88-aa4b-29243c17f93a" />







