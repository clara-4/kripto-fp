from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import secrets
import logging

import time
import psutil
import numpy as np
from timeit import timeit


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Logging untuk debugging
logging.basicConfig(level=logging.DEBUG)

# Fungsi GCD
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# Fungsi eksponensiasi modular
def mod_exp(base, exp, mod):
    result = 1
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result

# PRNG RCTM
def prng_rctm(seed, count):
    results = []
    x = seed
    for _ in range(count):
        x = (1103515245 * x + 12345) % (2**31 - 1)
        results.append(x)
    return results

# PRNG HC-MRLM
def prng_hcmrlm(seed, count, gamma=31):
    results = []
    x = seed / (2**31 - 1)  # Normalisasi seed
    for _ in range(count):
        x = (gamma * x * (1 - x)) % 1
        if 0.1 <= x <= 0.6:
            x = (x * 10**10) % 1
        results.append(int(x * (2**31 - 1)))
    return results

# Fungsi untuk menghasilkan bilangan prima dari PRNG
def generate_prime_from_prng(prng_function, seed, count):
    numbers = prng_function(seed, count)
    for num in numbers:
        if is_prime(num) and num > 1:
            return num
    raise ValueError("Tidak ada bilangan prima yang ditemukan dalam hasil PRNG.")

# Fungsi untuk memeriksa bilangan prima
def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

# Fungsi untuk menghasilkan kunci RSA
def generate_rsa_keys_with_prng(prng_function, seed):
    p = generate_prime_from_prng(prng_function, seed, 100)
    q = generate_prime_from_prng(prng_function, seed + 1, 100)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = random.randrange(2, phi)
    while gcd(e, phi) != 1:
        e = random.randrange(2, phi)
    d = pow(e, -1, phi)
    return ((e, n), (d, n))

# Fungsi enkripsi dan dekripsi
def encrypt_reservation(data, key):
    logging.debug(f"Encrypting data: {data} with key: {key}")
    e, n = key
    encrypted_data = [mod_exp(ord(char), e, n) for char in data]
    hex_length = (n.bit_length() + 3) // 4  # Panjang hexadecimal sesuai modulus
    result = ''.join(f'{num:0{hex_length}x}' for num in encrypted_data)
    logging.debug(f"Encrypted data: {result}")
    return result

def decrypt_reservation(hex_data, key):
    logging.debug(f"Decrypting data: {hex_data} with key: {key}")
    d, n = key
    hex_length = (n.bit_length() + 3) // 4
    encrypted_data = [int(hex_data[i:i + hex_length], 16) for i in range(0, len(hex_data), hex_length)]
    result = ''.join([chr(mod_exp(char, d, n)) for char in encrypted_data])
    logging.debug(f"Decrypted data: {result}")
    return result

# Inisialisasi kunci RSA
rctm_seed = 12345
hcmrlm_seed = 67890

public_key_rctm, private_key_rctm = generate_rsa_keys_with_prng(prng_rctm, rctm_seed)
public_key_hcmrlm, private_key_hcmrlm = generate_rsa_keys_with_prng(prng_hcmrlm, hcmrlm_seed)

reservations = {}

def benchmark_prng_with_timeit(prng_function, seed, iterations, count):
    execution_times = []
    cpu_usages = []

    for _ in range(iterations):
        # Awal pengukuran CPU
        cpu_start = psutil.cpu_percent(interval=None)

        # Mengukur waktu eksekusi menggunakan timeit
        exec_time = timeit(lambda: prng_function(seed, count), number=1)

        # Akhir pengukuran CPU
        cpu_end = psutil.cpu_percent(interval=None)
        cpu_usage = cpu_end - cpu_start

        # Simpan hasil
        execution_times.append(exec_time)
        cpu_usages.append(cpu_usage)

    # Statistik waktu eksekusi
    avg_execution_time = np.mean(execution_times)
    std_execution_time = np.std(execution_times)

    # Statistik penggunaan CPU
    avg_cpu_usage = np.mean(cpu_usages)
    std_cpu_usage = np.std(cpu_usages)

    return {
        "avg_execution_time": avg_execution_time,
        "std_execution_time": std_execution_time,
        "avg_cpu_usage": avg_cpu_usage,
        "std_cpu_usage": std_cpu_usage
    }


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/reservasi-rctm', methods=['GET', 'POST'])
def reservasi_rctm():
    if request.method == 'POST':
        name = request.form['name']
        table_number = request.form['table_number']
        reservation_time = request.form['reservation_time']

        reservation_data = f'{name},{table_number},{reservation_time}'
        encrypted_token = encrypt_reservation(reservation_data, public_key_rctm)
        reservations[name] = encrypted_token
        session['token'] = encrypted_token

        flash('Reservasi menggunakan RCTM berhasil! Berikut adalah token Anda.')
        return render_template('reservasi-rctm.html', token=session['token'])

    return render_template('reservasi-rctm.html', token=None)

@app.route('/reservasi-hcmrlm', methods=['GET', 'POST'])
def reservasi_hcmrlm():
    if request.method == 'POST':
        name = request.form['name']
        table_number = request.form['table_number']
        reservation_time = request.form['reservation_time']

        reservation_data = f'{name},{table_number},{reservation_time}'
        encrypted_token = encrypt_reservation(reservation_data, public_key_hcmrlm)
        reservations[name] = encrypted_token
        session['token'] = encrypted_token

        flash('Reservasi menggunakan HC-MRLM berhasil! Berikut adalah token Anda.')
        return render_template('reservasi-hcmrlm.html', token=session['token'])

    return render_template('reservasi-hcmrlm.html', token=None)

@app.route('/token-rctm', methods=['GET', 'POST'])
def validate_token_rctm():
    if request.method == 'POST':
        token_input = request.form['token']
        try:
            decrypted_data = decrypt_reservation(token_input, private_key_rctm)
            name, table_number, reservation_time = decrypted_data.split(',')
            flash(f'Token valid! Reservasi untuk {name} di meja {table_number} pada {reservation_time}.')
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            flash('Token tidak valid atau tidak dapat didekripsi.')
        return redirect(url_for('validate_token_rctm'))

    return render_template('token-rctm.html')

@app.route('/token-hcmrlm', methods=['GET', 'POST'])
def validate_token_hcmrlm():
    if request.method == 'POST':
        token_input = request.form['token']
        try:
            decrypted_data = decrypt_reservation(token_input, private_key_hcmrlm)
            name, table_number, reservation_time = decrypted_data.split(',')
            flash(f'Token valid! Reservasi untuk {name} di meja {table_number} pada {reservation_time}.')
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            flash('Token tidak valid atau tidak dapat didekripsi.')
        return redirect(url_for('validate_token_hcmrlm'))

    return render_template('token-hcmrlm.html')

@app.route('/compare', methods=['GET'])
def compare_prng():
    rctm_seed = 12345
    hcmrlm_seed = 67890
    iterations = 1000  # Jumlah iterasi benchmark
    count = 5000      # Banyaknya bilangan yang dihasilkan per iterasi

    # Benchmark untuk RCTM
    rctm_benchmark = benchmark_prng_with_timeit(prng_rctm, rctm_seed, iterations, count)
    # Benchmark untuk HC-MRLM
    hcmrlm_benchmark = benchmark_prng_with_timeit(prng_hcmrlm, hcmrlm_seed, iterations, count)

    # Data untuk template
    performance = {
        "rctm": {
            "execution_time": f"{rctm_benchmark['avg_execution_time']:.6f} seconds",
            "cpu_usage": f"{rctm_benchmark['avg_cpu_usage']:.2f}%"
        },
        "hcmrlm": {
            "execution_time": f"{hcmrlm_benchmark['avg_execution_time']:.6f} seconds",
            "cpu_usage": f"{hcmrlm_benchmark['avg_cpu_usage']:.2f}%"
        }
    }

    return render_template('compare.html', performance=performance)



if __name__ == '__main__':
    app.run(debug=True)
