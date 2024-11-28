from flask import Flask, render_template, request, redirect, url_for, flash, session
import secrets
import random

app = Flask(__name__)

# Generate a random secret key
app.secret_key = secrets.token_hex(16)

# Fungsi untuk menghitung gcd
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# Fungsi untuk menghitung eksponen modular
def mod_exp(base, exp, mod):
    result = 1
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result

# Fungsi untuk menghasilkan kunci RSA
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

# Generate kunci publik dan privat
public_key, private_key = generate_rsa_keys()

reservations = {}

# Fungsi untuk enkripsi menggunakan kunci publik dan mengubahnya ke heksadesimal
def encrypt_reservation(data, key):
    e, n = key
    encrypted_data = [mod_exp(ord(char), e, n) for char in data]
    hex_data = ''.join(f'{num:04x}' for num in encrypted_data)  # Convert to hex without separator
    return hex_data

# Fungsi untuk dekripsi dari heksadesimal
def decrypt_reservation(hex_data, key):
    d, n = key
    encrypted_data = [int(hex_data[i:i+4], 16) for i in range(0, len(hex_data), 4)]  # Split hex back to integers
    decrypted_data = ''.join([chr(mod_exp(char, d, n)) for char in encrypted_data])
    return decrypted_data

@app.route('/')
def home():
    return render_template('reservasi.html', token=None)

@app.route('/reservasi', methods=['GET', 'POST'])
def reservasi():
    if request.method == 'POST':
        name = request.form['name']
        table_number = request.form['table_number']
        reservation_time = request.form['reservation_time']

        reservation_data = f'{name},{table_number},{reservation_time}'
        encrypted_token = encrypt_reservation(reservation_data, public_key)

        reservations[name] = encrypted_token
        session['token'] = encrypted_token

        flash('Reservasi berhasil! Berikut adalah token reservasi Anda.')
        return render_template('reservasi.html', token=session['token'])

    return render_template('reservasi.html', token=None)

@app.route('/token', methods=['GET', 'POST'])
def validate_token():
    if request.method == 'POST':
        token_input = request.form['token']
        
        try:
            decrypted_data = decrypt_reservation(token_input, private_key)

            if decrypted_data:
                name, table_number, reservation_time = decrypted_data.split(',')
                flash(f'Token valid! Reservasi untuk {name} di meja {table_number} pada {reservation_time}.')
            else:
                flash('Token tidak valid.')
        except:
            flash('Token tidak valid atau tidak dapat didekripsi.')

        return redirect(url_for('validate_token'))

    return render_template('token.html')

if __name__ == '__main__':
    app.run(debug=True)
