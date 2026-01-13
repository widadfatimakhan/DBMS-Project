from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QHeaderView, QMessageBox
import sys
import os
import pyodbc
from datetime import datetime, timedelta

# --- Database Connection Details ---
server = 'localhost\\SQLSERVER1'
database = 'project'
use_windows_authentication = True
username = 'sa'
password = 'your_password'

# Set up scaling
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0.5"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1.3"

def create_connection_string():
    if use_windows_authentication:
        return (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'Trusted_Connection=yes;'
        )
    else:
        return (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
        )

# ==================== MAIN WINDOW ====================
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            uic.loadUi("newmovie.ui", self)
        except Exception as e:
            QMessageBox.critical(self, "UI Load Error", f"Could not load newmovie.ui.\nError: {e}")
            sys.exit(1)

        # Buttons
        self.manageButton.clicked.connect(self.open_manage_bookings)
        self.book_next.clicked.connect(self.open_booking_window)

        # Load combos
        self.load_branch_names()
        self.load_active_movies()
        self.load_date_dropdown()

    # --- Combo Loaders ---
    def load_branch_names(self):
        conn_str = create_connection_string()
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT BranchName FROM Cinema ORDER BY BranchName;")
            branches = cursor.fetchall()
            self.branch_combo.clear()
            self.branch_combo.addItem("Select Branch")
            for b in branches:
                self.branch_combo.addItem(b[0])
            self.branch_combo.setCurrentIndex(0)
            cursor.close()
            conn.close()
        except Exception as e:
            print("Branch load error:", e)
            self.branch_combo.clear()
            self.branch_combo.addItem("Error")

    def load_active_movies(self):
        conn_str = create_connection_string()
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT Movie_Name FROM Movies WHERE Is_Active = 1 ORDER BY Movie_Name;")
            movies = cursor.fetchall()
            self.movie_combo.clear()
            self.movie_combo.addItem("Select Movie")
            for m in movies:
                self.movie_combo.addItem(m[0])
            self.movie_combo.setCurrentIndex(0)
            cursor.close()
            conn.close()
        except Exception as e:
            print("Movie load error:", e)
            self.movie_combo.clear()
            self.movie_combo.addItem("Error")

    def load_date_dropdown(self):
        self.date_combo.clear()
        self.date_combo.addItem("Select Date")
        today = datetime.today()
        for i in range(8):
            date_str = (today + timedelta(days=i)).strftime("%Y-%m-%d")
            self.date_combo.addItem(date_str)
        self.date_combo.setCurrentIndex(0)

    # --- Navigation ---
    def open_booking_window(self):
        if self.branch_combo.currentIndex() == 0:
            QMessageBox.warning(self, "Required", "Please select a Branch.")
            return
        if self.movie_combo.currentIndex() == 0:
            QMessageBox.warning(self, "Required", "Please select a Movie.")
            return
        if self.date_combo.currentIndex() == 0:
            QMessageBox.warning(self, "Required", "Please select a Date.")
            return

        try:
            self.booking_window = BookingWindow(
                selected_movie=self.movie_combo.currentText(),
                selected_date=self.date_combo.currentText(),
                selected_branch=self.branch_combo.currentText()
            )
            self.booking_window.show()
        except Exception as e:
            QMessageBox.critical(self, "UI Load Error", f"Could not load booking.ui.\nError: {e}")

    def open_manage_bookings(self):
        self.manage_window = ManageWindow()
        self.manage_window.show()


# ==================== BOOKING WINDOW ====================
class BookingWindow(QtWidgets.QMainWindow):
    def __init__(self, selected_movie, selected_date, selected_branch):
        super().__init__()
        self.selected_movie = selected_movie
        self.selected_date = selected_date
        self.selected_branch = selected_branch
        self.selected_time_btn = None

        try:
            uic.loadUi("booking.ui", self)
        except Exception as e:
            QMessageBox.critical(self, "UI Load Error", f"Could not load booking.ui.\nError: {e}")
            sys.exit(1)

        # Connect time buttons
        for btn_name in ['book_2', 'book_5', 'book_9']:
            btn = self.findChild(QtWidgets.QPushButton, btn_name)
            if btn:
                btn.clicked.connect(self.open_no_of_tickets_window)

    def open_no_of_tickets_window(self):
        sender = self.sender()
        if sender:
            self.selected_time_btn = sender.objectName()
        try:
            self.no_tickets_window = NoOfTicketsWindow(
                selected_movie=self.selected_movie,
                selected_date=self.selected_date,
                selected_branch=self.selected_branch,
                selected_time_btn=self.selected_time_btn
            )
            self.no_tickets_window.show()
        except Exception as e:
            QMessageBox.critical(self, "UI Load Error", f"Could not load no_of_tickets.ui.\nError: {e}")


# ==================== NO OF TICKETS WINDOW ====================
class NoOfTicketsWindow(QtWidgets.QMainWindow):
    def __init__(self, selected_movie, selected_date, selected_branch, selected_time_btn):
        super().__init__()
        self.selected_movie = selected_movie
        self.selected_date = selected_date
        self.selected_branch = selected_branch
        self.selected_time_btn = selected_time_btn

        try:
            uic.loadUi("no_of_tickets.ui", self)
        except Exception as e:
            QMessageBox.critical(self, "UI Load Error", f"Could not load no_of_tickets.ui.\nError: {e}")
            sys.exit(1)

        self.ticket_line = self.findChild(QtWidgets.QLineEdit, "ticket_line")
        self.proceed_pay = self.findChild(QtWidgets.QPushButton, "proceed_pay")
        self.proceed_pay.clicked.connect(self.show_total_amount)

    def show_total_amount(self):
        tickets = self.ticket_line.text().strip()
        if tickets == "" or not tickets.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number of tickets.")
            return

        total_amount = int(tickets) * 1000
        QMessageBox.information(self, "Total Amount", f"Your total amount is {total_amount}")

        try:
            self.payment_window = PaymentWindow(
                selected_movie=self.selected_movie,
                selected_date=self.selected_date,
                selected_branch=self.selected_branch,
                selected_time_btn=self.selected_time_btn,
                no_of_tickets=int(tickets)
            )
            self.payment_window.show()
        except Exception as e:
            QMessageBox.critical(self, "UI Error", f"Could not load payment.ui\nError: {e}")


# ==================== PAYMENT WINDOW ====================
class PaymentWindow(QtWidgets.QMainWindow):
    def __init__(self, selected_movie, selected_date, selected_branch, selected_time_btn, no_of_tickets):
        super().__init__()
        self.selected_movie = selected_movie
        self.selected_date = selected_date
        self.selected_branch = selected_branch
        self.selected_time_btn = selected_time_btn
        self.no_of_tickets = no_of_tickets

        try:
            uic.loadUi("payment.ui", self)
        except Exception as e:
            QMessageBox.critical(self, "UI Error", f"Could not load payment.ui\nError: {e}")
            sys.exit(1)

        self.pay_name = self.findChild(QtWidgets.QLineEdit, "pay_name")
        self.pay_mail = self.findChild(QtWidgets.QLineEdit, "pay_mail")
        self.pay_combo = self.findChild(QtWidgets.QComboBox, "pay_combo")
        self.pay_combo.clear()
        self.pay_combo.addItems(["Select Payment Mode", "Cash", "Card"])
        self.pay_combo.setCurrentIndex(0)

        self.pay_next_btn = self.findChild(QtWidgets.QPushButton, "pay_next")
        self.pay_return_btn = self.findChild(QtWidgets.QPushButton, "pay_return")

        self.pay_next_btn.clicked.connect(self.process_payment)
        self.pay_return_btn.clicked.connect(self.confirm_return)

    def process_payment(self):
        name = self.pay_name.text().strip()
        mail = self.pay_mail.text().strip()
        mode = self.pay_combo.currentText()

        if name == "" or mail == "":
            QMessageBox.warning(self, "Missing Input", "Please fill all fields.")
            return
        if mode == "Select Payment Mode":
            QMessageBox.warning(self, "Missing Input", "Please select a payment mode.")
            return

        conn_str = create_connection_string()
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # --------------------------
            # 1. Insert customer if not exists
            # --------------------------
            cursor.execute("SELECT COUNT(*) FROM Customer WHERE Customer_Email = ?", mail)
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO Customer (Customer_Name, Customer_Email) VALUES (?, ?)",
                    name, mail
                )

            # --------------------------
            # 2. BranchID mapping
            # --------------------------
            branch_map = {"Karachi": 1, "Islamabad": 2}
            branch_id = branch_map.get(self.selected_branch, 1)

            # --------------------------
            # 3. Convert selected_time_btn + date to datetime
            # --------------------------
            hour_map = {"book_2": 14, "book_5": 17, "book_9": 21}
            hour = hour_map.get(self.selected_time_btn, 14)
            booking_time = datetime.strptime(self.selected_date, "%Y-%m-%d").replace(
                hour=hour, minute=0, second=0, microsecond=0
            )

            # --------------------------
            # 4. Insert into Bookings and get BookingID
            # --------------------------
            cursor.execute("""
                INSERT INTO Bookings (Time, No_Of_Tickets, Mode_Of_Payment, Movie_Name, Customer_Email, BranchID)
                OUTPUT INSERTED.BookingID
                VALUES (?, ?, ?, ?, ?, ?)
            """, booking_time, self.no_of_tickets, mode, self.selected_movie, mail, branch_id)

            row = cursor.fetchone()
            if row is None or row[0] is None:
                QMessageBox.critical(self, "DB Error", "Failed to retrieve Booking ID after insert.")
                conn.rollback()
                cursor.close()
                conn.close()
                return

            booking_id = int(row[0])

            # --------------------------
            # 5. Insert into Tickets
            # --------------------------
            price_per_ticket = 1000
            total_amount = price_per_ticket * self.no_of_tickets

            cursor.execute("""
                INSERT INTO Tickets (Date, Price_Per_Ticket, Total_Amount, Booking_Status, Movie_Name, BookingID)
                VALUES (?, ?, ?, ?, ?, ?)
            """, booking_time, price_per_ticket, total_amount, 'Confirmed', self.selected_movie, booking_id)
            # 1. Insert customer if not exists
            cursor.execute("SELECT COUNT(*) FROM Customer WHERE Customer_Email = ?", (mail,))
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO Customer (Customer_Name, Customer_Email) VALUES (?, ?)",
                    (name, mail)
                )

            # --------------------------
            # Commit transaction
            # --------------------------
            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "DB Error", f"Could not save booking.\nError: {e}")
            return

        # --------------------------
        # 6. Open ticket screen
        # --------------------------
        try:
            self.ticket_window = uic.loadUi("ticket.ui")
            try:
                self.ticket_window.name_label.setText(name)
                self.ticket_window.movie_label.setText(self.selected_movie)
                self.ticket_window.date_label.setText(self.selected_date)

                time_str = booking_time.strftime("%I:%M %p")
                self.ticket_window.time_label.setText(time_str)

                self.ticket_window.num_label.setText(str(self.no_of_tickets))

                # Download button
                self.ticket_window.download.clicked.connect(
                    lambda: QMessageBox.information(self.ticket_window, "Downloaded", "Your ticket has been downloaded.")
                )

                # Home button
                self.ticket_window.home_return.clicked.connect(self.close_all_and_return)

            except Exception as e:
                print("Warning: Some ticket labels not found.", e)

            self.ticket_window.show()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "UI Error", f"Could not load ticket.ui\nError: {e}")


    def close_all_and_return(self):
        for w in QApplication.topLevelWidgets():
            if isinstance(w, QtWidgets.QMainWindow):
                w.close()
        self.main_window = MainWindow()
        self.main_window.show()

    def confirm_return(self):
        reply = QMessageBox.question(
            self,
            "Cancel Payment",
            "Are you sure you want to cancel payment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()



# ==================== RECORDS CUSTOMER WINDOW ====================
class RecordsCustomerWindow(QtWidgets.QMainWindow):
    def __init__(self, customer_name="", customer_email=""):
        super().__init__()

        try:
            uic.loadUi("records_customer.ui", self)
        except Exception as e:
            QMessageBox.critical(self, "UI Load Error", f"Could not load records_customer.ui.\nError: {e}")
            sys.exit(1)

        self.customer_name = customer_name
        self.customer_email = customer_email
        self.has_data = False

        self.recordsTable = self.findChild(QtWidgets.QTableWidget, "recordsTable")
        self.returnButton = self.findChild(QtWidgets.QPushButton, "returnButton")
        if self.returnButton:
            self.returnButton.clicked.connect(self.close)

        self.cancelButton = self.findChild(QtWidgets.QPushButton, "cancelButton")
        if self.cancelButton:
            self.cancelButton.clicked.connect(self.cancel_booking)

        self.load_customer_bookings()

    def load_customer_bookings(self):
        if not self.recordsTable:
            return

        conn_str = create_connection_string()
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            query = """
            SELECT
                C.Customer_Name,
                B.BookingID,
                B.Movie_Name,  -- Use directly from Bookings
                CAST(B.[Time] AS DATE) AS ShowDate,
                CAST(B.[Time] AS TIME) AS ShowTime,
                B.No_Of_Tickets,
                T.Booking_Status
            FROM
                Customer C
                JOIN Bookings B ON C.Customer_Email = B.Customer_Email
                JOIN Tickets T ON B.BookingID = T.BookingID
            WHERE 1=1

            """
            params = []
            if self.customer_name:
                query += " AND C.Customer_Name = ?"
                params.append(self.customer_name)
            if self.customer_email:
                query += " AND C.Customer_Email = ?"
                params.append(self.customer_email)

            query += " ORDER BY B.[Time] DESC;"

            cursor.execute(query, params)
            data = cursor.fetchall()
            cursor.close()
            conn.close()

            if not data:
                QMessageBox.information(self, "No Records", "No bookings found for the given customer details.")
                self.has_data = False
                return

            self.has_data = True
            headers = ["Customer Name", "Booking ID", "Movie", "Date", "Time", "No of tickets", "Booking Status"]
            self.recordsTable.setColumnCount(len(headers))
            self.recordsTable.setHorizontalHeaderLabels(headers)
            self.recordsTable.setRowCount(len(data))

            for r, row in enumerate(data):
                for c, item in enumerate(row):
                    if c == 3 and hasattr(item, 'strftime'):  # Date
                        item_str = item.strftime("%Y-%m-%d")
                    elif c == 4 and hasattr(item, 'strftime'):  # Time
                        item_str = item.strftime("%H:%M")
                    else:
                        item_str = str(item) if item is not None else ""
                    self.recordsTable.setItem(r, c, QTableWidgetItem(item_str))

            self.recordsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.recordsTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        except Exception as e:
            QMessageBox.critical(self, "DB Error", f"Error loading customer bookings: {e}")

    def cancel_booking(self):
        selected_row = self.recordsTable.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a booking to cancel.")
            return

        booking_id = self.recordsTable.item(selected_row, 1).text()
        status_item = self.recordsTable.item(selected_row, 6)
        current_status = status_item.text() if status_item else ""

        if current_status.lower() == "cancelled":
            QMessageBox.information(self, "Already Cancelled",
                                    f"Booking ID {booking_id} is already cancelled.")
            return

        reply = QMessageBox.question(self, "Confirm Cancellation",
                                     f"Are you sure you want to cancel Booking ID: {booking_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            conn = pyodbc.connect(create_connection_string())
            cursor = conn.cursor()
            cursor.execute("UPDATE Tickets SET Booking_Status = 'Cancelled' WHERE BookingID = ?", booking_id)
            conn.commit()
            cursor.close()
            conn.close()
            QMessageBox.information(self, "Cancelled", f"Booking {booking_id} has been cancelled.")
            self.load_customer_bookings()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", f"Could not cancel booking.\nError: {e}")


# ==================== MANAGE BOOKINGS WINDOW ====================
class ManageWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        try:
            uic.loadUi("manage_bookings.ui", self)
        except Exception as e:
            QMessageBox.critical(self, "UI Load Error", f"Could not load manage_bookings.ui.\nError: {e}")
            sys.exit(1)

        self.nameInput = self.findChild(QtWidgets.QLineEdit, "name_input")
        self.emailInput = self.findChild(QtWidgets.QLineEdit, "email_input")
        self.returnButton = self.findChild(QtWidgets.QPushButton, "book_return")
        if self.returnButton:
            self.returnButton.clicked.connect(self.close)

        self.nextButton = self.findChild(QtWidgets.QPushButton, "next_button")
        if self.nextButton:
            self.nextButton.clicked.connect(self.open_records_customer)

    def open_records_customer(self):
        customer_name = self.nameInput.text().strip() if self.nameInput else ""
        customer_email = self.emailInput.text().strip() if self.emailInput else ""
        if not customer_name and not customer_email:
            QMessageBox.warning(self, "Input Required", "Please enter Customer Name or Email.")
            return

        self.records_customer_window = RecordsCustomerWindow(customer_name, customer_email)
        if self.records_customer_window.has_data:
            self.records_customer_window.show()
        else:
            self.records_customer_window.deleteLater()


# ==================== APPLICATION EXECUTION ====================
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
