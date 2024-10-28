document.addEventListener("DOMContentLoaded", function() {
    const seats = document.querySelectorAll('.seat');
    const selectedSeatsInput = document.getElementById('selected_seats');
    const movieSelect = document.getElementById('movie');
    const showtimeSelect = document.getElementById('showtime');

    // Lưu trữ ghế đã chọn
    let selectedSeats = [];

    // Hàm cập nhật ghế đã đặt từ cơ sở dữ liệu
    function updateBookedSeats() {
        const selectedMovie = movieSelect.value;
        const selectedShowtime = showtimeSelect.value;

        if (selectedMovie && selectedShowtime) {
            fetch(`/get_booked_seats?movie=${selectedMovie}&showtime=${selectedShowtime}`)
                .then(response => response.json())
                .then(data => {
                    // Đặt ghế đã đặt
                    seats.forEach(seat => {
                        seat.classList.remove('booked');
                    });
                    data.booked_seats.forEach(seat => {
                        const bookedSeat = document.querySelector(`.seat[data-seat-number='${seat}']`);
                        if (bookedSeat) {
                            bookedSeat.classList.add('booked');
                        }
                    });
                });
        }
    }

    // Gọi hàm để cập nhật ghế đã đặt khi chọn phim hoặc giờ chiếu
    movieSelect.addEventListener('change', updateBookedSeats);
    showtimeSelect.addEventListener('change', updateBookedSeats);

    seats.forEach(seat => {
        seat.addEventListener('click', function() {
            const seatNumber = this.getAttribute('data-seat-number');

            // Nếu ghế đã được đặt, không làm gì
            if (this.classList.contains('booked')) {
                alert("Ghế này đã được đặt!");
                return;
            }

            // Nếu ghế đã được chọn, bỏ chọn
            if (this.classList.contains('selected')) {
                this.classList.remove('selected');
                selectedSeats = selectedSeats.filter(seat => seat !== seatNumber);
            } else {
                // Chọn ghế
                this.classList.add('selected');
                selectedSeats.push(seatNumber);
            }

            // Cập nhật giá trị của input ẩn
            selectedSeatsInput.value = selectedSeats.join(',');
        });
    });

    // Gọi hàm để tải ghế đã đặt ban đầu nếu có
    updateBookedSeats();
});
