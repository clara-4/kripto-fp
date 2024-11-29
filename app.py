from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Fungsi RSA
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

def generate_rsa_keys():
    p = 61
    q = 53
    n = p * q
    phi = (p - 1) * (q - 1)
    e = random.randrange(2, phi)
    while gcd(e, phi) != 1:
        e = random.randrange(2, phi)
    d = pow(e, -1, phi)
    return ((e, n), (d, n))

public_key, private_key = generate_rsa_keys()

def encrypt_reservation(data, key):
    e, n = key
    encrypted_data = [mod_exp(ord(char), e, n) for char in data]
    return ''.join(f'{num:04x}' for num in encrypted_data)

def decrypt_reservation(hex_data, key):
    d, n = key
    encrypted_data = [int(hex_data[i:i+4], 16) for i in range(0, len(hex_data), 4)]
    return ''.join([chr(mod_exp(char, d, n)) for char in encrypted_data])

# Fungsi PRNG
def prng_rctm(seed, count):
    results = []
    x = seed
    for _ in range(count):
        x = (1103515245 * x + 12345) % (2**31 - 1)
        results.append(x)
    return results

def prng_henon_map(seed, count, a=1.4, b=0.3):
    results = []
    x, y = seed, seed
    for _ in range(count):
        a += 0.0001
        b -= 0.0001
        x_next = 1 - a * (x**2) + y
        y_next = b * x
        x, y = x_next, y_next
        results.append(x)
    return results

reservations = {}

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
        encrypted_token = encrypt_reservation(reservation_data, public_key)
        reservations[name] = encrypted_token
        session['token'] = encrypted_token

        flash('Reservasi menggunakan RCTM berhasil! Berikut adalah token Anda.')
        return render_template('reservasi-rctm.html', token=session['token'])

    return render_template('reservasi-rctm.html', token=None)

@app.route('/reservasi-henon', methods=['GET', 'POST'])
def reservasi_henon():
    if request.method == 'POST':
        name = request.form['name']
        table_number = request.form['table_number']
        reservation_time = request.form['reservation_time']

        reservation_data = f'{name},{table_number},{reservation_time}'
        encrypted_token = encrypt_reservation(reservation_data, public_key)
        reservations[name] = encrypted_token
        session['token'] = encrypted_token

        flash('Reservasi menggunakan Hénon Map berhasil! Berikut adalah token Anda.')
        return render_template('reservasi-henon.html', token=session['token'])

    return render_template('reservasi-henon.html', token=None)

@app.route('/token-rctm', methods=['GET', 'POST'])
def validate_token_rctm():
    if request.method == 'POST':
        token_input = request.form['token']
        try:
            decrypted_data = decrypt_reservation(token_input, private_key)
            name, table_number, reservation_time = decrypted_data.split(',')
            flash(f'Token valid! Reservasi untuk {name} di meja {table_number} pada {reservation_time}.')
        except:
            flash('Token tidak valid atau tidak dapat didekripsi.')
        return redirect(url_for('validate_token_rctm'))

    return render_template('token-rctm.html')

@app.route('/token-henon', methods=['GET', 'POST'])
def validate_token_henon():
    if request.method == 'POST':
        token_input = request.form['token']
        try:
            decrypted_data = decrypt_reservation(token_input, private_key)
            name, table_number, reservation_time = decrypted_data.split(',')
            flash(f'Token valid! Reservasi untuk {name} di meja {table_number} pada {reservation_time}.')
        except:
            flash('Token tidak valid atau tidak dapat didekripsi.')
        return redirect(url_for('validate_token_henon'))

    return render_template('token-henon.html')

if __name__ == '__main__':
    app.run(debug=True)
