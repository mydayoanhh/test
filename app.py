from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Kết nối đến MongoDB
client = MongoClient('mongodb+srv://phuongquynh:Chichi1973%40@cluster0.50xns.mongodb.net/?retryWrites=true&w=majority')
db = client['movies_theate']
customers_collection = db['customers']
bookings_collection = db['bookings']

# Route cho đăng nhập và đăng ký
@app.route('/', methods=['GET', 'POST'])
def login_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form['action']

        if action == 'register':
            if customers_collection.find_one({'username': username}):
                return "Tên đăng nhập đã tồn tại", 400  # Tên đăng nhập đã tồn tại
            hashed_password = generate_password_hash(password)
            customers_collection.insert_one({'username': username, 'password': hashed_password})
            return redirect(url_for('login_register'))

        elif action == 'login':
            customer = customers_collection.find_one({'username': username})
            if customer and check_password_hash(customer['password'], password):
                session['customer_logged_in'] = True
                session['username'] = username
                return redirect('/booking')
            else:
                return 'Sai tên đăng nhập hoặc mật khẩu', 401  # Sai tên đăng nhập hoặc mật khẩu

    return render_template('login_register.html')

# Route cho trang đặt vé
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'customer_logged_in' in session:
        username = session['username']

        if request.method == 'POST':
            movie = request.form['movie']
            showtime = request.form['showtime']
            seats = request.form['selected_seats'].split(',') if request.form.get('selected_seats') else []

            # Xác thực chọn lựa
            if not movie or not showtime or not seats:
                return "Vui lòng chọn phim, giờ chiếu và ghế!", 400  # Vui lòng chọn phim, giờ chiếu và ghế

            # Lưu đặt vé vào cơ sở dữ liệu
            if save_booking(username, movie, showtime, seats):
                return f"<p>Đặt vé thành công cho phim {movie} lúc {showtime} với {len(seats)} ghế!</p>"
            else:
                return "Có lỗi xảy ra khi lưu đặt vé.", 500  # Lỗi lưu đặt vé

        return render_template('booking.html', username=username)
    else:
        return redirect(url_for('login_register'))

# Lưu đặt vé
def save_booking(username, movie, showtime, seats):
    try:
        bookings_collection.insert_one({
            'username': username,
            'movie': movie,
            'showtime': showtime,
            'seats': seats
        })
        return True  # Trả về True nếu đặt vé thành công
    except Exception as e:
        return False  # Trả về False nếu có lỗi

# Route để lấy thông tin ghế đã đặt
@app.route('/get_booked_seats', methods=['GET'])
def get_booked_seats():
    movie = request.args.get('movie')  # Lấy tên phim từ query string
    showtime = request.args.get('showtime')  # Lấy giờ chiếu từ query string

    # Tìm các ghế đã đặt cho phim và giờ chiếu này
    bookings = bookings_collection.find({'movie': movie, 'showtime': showtime})
    booked_seats = []
    for booking in bookings:
        booked_seats.extend(booking['seats'])

    return {'booked_seats': booked_seats}

@app.route('/logout')
def logout():
    session.pop('customer_logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login_register'))

if __name__ == '__main__':
    app.run(debug=True)
