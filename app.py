from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import secrets
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from hashlib import sha256
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Fungsi GCD dan Modulo Exponentiation
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def mod_exp(base, exp, mod):
    result = 1
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result

# Fungsi CTR-DRBG
def ctr_drbg(seed, length):
    key = sha256(seed.encode()).digest()
    counter = 0
    random_bytes = b""
    while len(random_bytes) < length:
        cipher = AES.new(key, AES.MODE_ECB)
        counter_bytes = counter.to_bytes(16, 'big')
        random_bytes += cipher.encrypt(counter_bytes)
        counter += 1
    return random_bytes[:length]

# Fungsi Fortuna
def fortuna(seed_pool, length):
    if not isinstance(seed_pool, list) or len(seed_pool) < 32:
        raise ValueError("Seed pool must contain at least 32 random seeds")
    hash_pool = sha256(b"".join(seed_pool)).digest()
    key = hash_pool[:16]
    cipher = AES.new(key, AES.MODE_CTR)
    return cipher.encrypt(b"\x00" * length)

# Fungsi RSA
def generate_rsa_keys(drbg_func, seed):
    p = 61
    q = 53
    n = p * q
    phi = (p - 1) * (q - 1)
    e = int.from_bytes(drbg_func(seed, 4), 'big') % phi
    while gcd(e, phi) != 1:
        e = int.from_bytes(drbg_func(seed, 4), 'big') % phi
    d = pow(e, -1, phi)
    return ((e, n), (d, n))

public_key_ctr, private_key_ctr = generate_rsa_keys(ctr_drbg, "CTR-Seed")
public_key_fortuna, private_key_fortuna = generate_rsa_keys(fortuna, [os.urandom(32) for _ in range(32)])

def encrypt_reservation(data, key):
    e, n = key
    encrypted_data = [mod_exp(ord(char), e, n) for char in data]
    return ''.join(f'{num:04x}' for num in encrypted_data)

def decrypt_reservation(hex_data, key):
    d, n = key
    encrypted_data = [int(hex_data[i:i+4], 16) for i in range(0, len(hex_data), 4)]
    return ''.join([chr(mod_exp(char, d, n)) for char in encrypted_data])

reservations = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/reservasi-ctr', methods=['GET', 'POST'])
def reservasi_ctr():
    if request.method == 'POST':
        name = request.form['name']
        table_number = request.form['table_number']
        reservation_time = request.form['reservation_time']

        reservation_data = f'{name},{table_number},{reservation_time}'
        encrypted_token = encrypt_reservation(reservation_data, public_key_ctr)
        reservations[name] = encrypted_token
        session['token'] = encrypted_token

        flash('Reservasi menggunakan CTR-DRBG berhasil! Berikut adalah token Anda.')
        return render_template('reservasi-ctr.html', token=session['token'])

    return render_template('reservasi-ctr.html', token=None)

@app.route('/reservasi-fortuna', methods=['GET', 'POST'])
def reservasi_fortuna():
    if request.method == 'POST':
        name = request.form['name']
        table_number = request.form['table_number']
        reservation_time = request.form['reservation_time']

        reservation_data = f'{name},{table_number},{reservation_time}'
        encrypted_token = encrypt_reservation(reservation_data, public_key_fortuna)
        reservations[name] = encrypted_token
        session['token'] = encrypted_token

        flash('Reservasi menggunakan Fortuna berhasil! Berikut adalah token Anda.')
        return render_template('reservasi-fortuna.html', token=session['token'])

    return render_template('reservasi-fortuna.html', token=None)

@app.route('/token-ctr', methods=['GET', 'POST'])
def validate_token_ctr():
    if request.method == 'POST':
        token_input = request.form['token']
        try:
            decrypted_data = decrypt_reservation(token_input, private_key_ctr)
            name, table_number, reservation_time = decrypted_data.split(',')
            flash(f'Token valid! Reservasi untuk {name} di meja {table_number} pada {reservation_time}.')
        except:
            flash('Token tidak valid atau tidak dapat didekripsi.')
        return redirect(url_for('validate_token_ctr'))

    return render_template('token-ctr.html')

@app.route('/token-fortuna', methods=['GET', 'POST'])
def validate_token_fortuna():
    if request.method == 'POST':
        token_input = request.form['token']
        try:
            decrypted_data = decrypt_reservation(token_input, private_key_fortuna)
            name, table_number, reservation_time = decrypted_data.split(',')
            flash(f'Token valid! Reservasi untuk {name} di meja {table_number} pada {reservation_time}.')
        except:
            flash('Token tidak valid atau tidak dapat didekripsi.')
        return redirect(url_for('validate_token_fortuna'))

    return render_template('token-fortuna.html')

if __name__ == '__main__':
    app.run(debug=True)
