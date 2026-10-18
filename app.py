
import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta
from decimal import Decimal

st.set_page_config(
    page_title="Hotel and Restaurant Management System",
    page_icon="🏨",
    layout="wide"
)
st.title("🏨 Centralized Hotel & Restaurant Management System")
st.caption(
    "Created by — "
    "SANJAY THANDEESWARAN (25BCE2759) & "
    "MONISH KUMAR T O (25BCE2819)"
)

# ============================================================
# 1. CLOUD DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Connect to your cloud MySQL-compatible database.

    IMPORTANT:
    Enter the host, username and password in Streamlit Cloud
    -> App Settings -> Secrets. Do not hardcode credentials here.
    """
    cfg = st.secrets["mysql"]

    return mysql.connector.connect(
        # CLOUD HOST: configured in Streamlit Secrets
        host=cfg["gateway01.ap-northeast-1.prod.aws.tidbcloud.com"],

        # CLOUD PORT: configured in Streamlit Secrets
        port=int(cfg.get("port", 4000)),

        # DATABASE NAME: e.g. "test" from your screenshot
        database=cfg["test"],

        # CLOUD USERNAME: configured in Streamlit Secrets
        user=cfg["JnPFvQX5aXG9eK8.root"],

        # CLOUD PASSWORD: configured in Streamlit Secrets
        password=cfg["wgOMqav1ZAdVyyzV"],

        connection_timeout=15,
        ssl_disabled=False
    )


def fetch_all(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()


def execute(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        result = cur.lastrowid
        cur.close()
        return result
    finally:
        conn.close()


# ============================================================
# 2. CREATE TABLES IN THE SELECTED CLOUD DATABASE
# ============================================================

def initialize_database():
    # The database itself must already exist in your provider.
    # These statements create tables inside that database.

    statements = [
        """
        CREATE TABLE IF NOT EXISTS Guest (
            Guest_ID INT AUTO_INCREMENT PRIMARY KEY,
            Guest_Name VARCHAR(100) NOT NULL,
            Phone VARCHAR(20) NOT NULL UNIQUE,
            Email VARCHAR(100) UNIQUE,
            Address VARCHAR(255)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Room (
            Room_ID INT AUTO_INCREMENT PRIMARY KEY,
            Room_Number VARCHAR(10) NOT NULL UNIQUE,
            Room_Type VARCHAR(50) NOT NULL,
            Price_Per_Night DECIMAL(10,2) NOT NULL,
            Status VARCHAR(20) NOT NULL DEFAULT 'Available'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Reservation (
            Reservation_ID INT AUTO_INCREMENT PRIMARY KEY,
            Guest_ID INT NOT NULL,
            Room_ID INT NOT NULL,
            Check_In_Date DATE NOT NULL,
            Check_Out_Date DATE NOT NULL,
            Number_of_Guests INT NOT NULL DEFAULT 1,
            Reservation_Status VARCHAR(20) NOT NULL DEFAULT 'Confirmed',
            FOREIGN KEY (Guest_ID) REFERENCES Guest(Guest_ID),
            FOREIGN KEY (Room_ID) REFERENCES Room(Room_ID)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Restaurant (
            Restaurant_ID INT AUTO_INCREMENT PRIMARY KEY,
            Restaurant_Name VARCHAR(100) NOT NULL,
            Location VARCHAR(100)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Menu_Item (
            Menu_Item_ID INT AUTO_INCREMENT PRIMARY KEY,
            Restaurant_ID INT NOT NULL,
            Item_Name VARCHAR(100) NOT NULL,
            Category VARCHAR(50),
            Price DECIMAL(10,2) NOT NULL,
            Availability VARCHAR(20) DEFAULT 'Available',
            FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS `Food_Order` (
            Order_ID INT AUTO_INCREMENT PRIMARY KEY,
            Guest_ID INT NOT NULL,
            Restaurant_ID INT NOT NULL,
            Order_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
            Order_Status VARCHAR(30) DEFAULT 'Placed',
            FOREIGN KEY (Guest_ID) REFERENCES Guest(Guest_ID),
            FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Order_Item (
            Order_Item_ID INT AUTO_INCREMENT PRIMARY KEY,
            Order_ID INT NOT NULL,
            Menu_Item_ID INT NOT NULL,
            Quantity INT NOT NULL,
            Unit_Price DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (Order_ID) REFERENCES `Food_Order`(Order_ID),
            FOREIGN KEY (Menu_Item_ID) REFERENCES Menu_Item(Menu_Item_ID)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Payment (
            Payment_ID INT AUTO_INCREMENT PRIMARY KEY,
            Guest_ID INT NOT NULL,
            Reservation_ID INT NULL,
            Amount DECIMAL(10,2) NOT NULL,
            Payment_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
            Payment_Method VARCHAR(30) DEFAULT 'Cash',
            Payment_Status VARCHAR(30) DEFAULT 'Paid',
            FOREIGN KEY (Guest_ID) REFERENCES Guest(Guest_ID),
            FOREIGN KEY (Reservation_ID) REFERENCES Reservation(Reservation_ID)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Staff (
            Staff_ID INT AUTO_INCREMENT PRIMARY KEY,
            Staff_Name VARCHAR(100) NOT NULL,
            Role VARCHAR(50) NOT NULL,
            Phone VARCHAR(20),
            Salary DECIMAL(10,2)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Service_Request (
            Request_ID INT AUTO_INCREMENT PRIMARY KEY,
            Guest_ID INT NOT NULL,
            Staff_ID INT NULL,
            Request_Type VARCHAR(100) NOT NULL,
            Request_Description VARCHAR(255),
            Request_Status VARCHAR(30) DEFAULT 'Pending',
            Request_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Guest_ID) REFERENCES Guest(Guest_ID),
            FOREIGN KEY (Staff_ID) REFERENCES Staff(Staff_ID)
        )
        """,
        """
        CREATE OR REPLACE VIEW View_Active_Billing_Summary AS
        SELECT
            g.Guest_ID,
            g.Guest_Name,
            COALESCE(SUM(p.Amount), 0) AS Total_Paid
        FROM Guest g
        LEFT JOIN Payment p
            ON g.Guest_ID = p.Guest_ID
            AND p.Payment_Status = 'Paid'
        GROUP BY g.Guest_ID, g.Guest_Name
        """
    ]

    conn = get_connection()
    try:
        cur = conn.cursor()
        for statement in statements:
            cur.execute(statement)
        conn.commit()
        cur.close()
    finally:
        conn.close()


# ============================================================
# 3. APPLICATION STARTUP
# ============================================================

st.title("🏨 Hotel and Restaurant Management System")
st.write("Manage hotel guests, rooms, reservations, restaurant orders and payments.")

try:
    initialize_database()
except Exception as e:
    st.error("Unable to connect to or initialize your cloud database.")
    st.write("Check your host, database name, username, password and database permissions.")
    st.code(str(e))
    st.stop()

page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Guest Management",
        "Room Management",
        "Reservations",
        "Restaurant & Menu",
        "Food Orders",
        "Payments",
        "Staff & Service Requests",
        "SQL Analytics & Views",
        "Test Database Connection"
    ]
)


# ============================================================
# 4. DASHBOARD
# ============================================================

if page == "Dashboard":
    st.header("Dashboard")

    try:
        guests = fetch_all("SELECT COUNT(*) AS n FROM Guest")[0]["n"]
        rooms = fetch_all("SELECT COUNT(*) AS n FROM Room")[0]["n"]
        reservations = fetch_all(
            "SELECT COUNT(*) AS n FROM Reservation "
            "WHERE Reservation_Status='Confirmed'"
        )[0]["n"]
        revenue = fetch_all(
            "SELECT COALESCE(SUM(Amount),0) AS n FROM Payment "
            "WHERE Payment_Status='Paid'"
        )[0]["n"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Guests", guests)
        c2.metric("Rooms", rooms)
        c3.metric("Confirmed Reservations", reservations)
        c4.metric("Payments Received", f"{revenue:.2f}")

        st.subheader("Recent reservations")
        st.dataframe(fetch_all("""
            SELECT r.Reservation_ID, g.Guest_Name, rm.Room_Number,
                   r.Check_In_Date, r.Check_Out_Date, r.Reservation_Status
            FROM Reservation r
            JOIN Guest g ON r.Guest_ID=g.Guest_ID
            JOIN Room rm ON r.Room_ID=rm.Room_ID
            ORDER BY r.Reservation_ID DESC
            LIMIT 10
        """), use_container_width=True)

    except Exception as e:
        st.error(str(e))


# ============================================================
# 5. GUEST MANAGEMENT - CREATE, READ, UPDATE, DELETE
# ============================================================

elif page == "Guest Management":
    st.header("Guest Management")

    with st.expander("➕ Add New Guest", expanded=True):
        with st.form("add_guest"):
            name = st.text_input("Guest Name")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            address = st.text_area("Address")
            submitted = st.form_submit_button("Add Guest")

        if submitted:
            if not name.strip() or not phone.strip():
                st.warning("Guest name and phone are required.")
            else:
                try:
                    execute(
                        "INSERT INTO Guest "
                        "(Guest_Name,Phone,Email,Address) VALUES (%s,%s,%s,%s)",
                        (name.strip(), phone.strip(), email.strip() or None,
                         address.strip() or None)
                    )
                    st.success("Guest added successfully!")
                    st.rerun()
                except Error as e:
                    st.error(f"Unable to add guest: {e}")

    st.subheader("Guest Records")
    search = st.text_input("Search guests by name, phone or email")

    try:
        guests = fetch_all("""
            SELECT * FROM Guest
            WHERE Guest_Name LIKE %s
               OR Phone LIKE %s
               OR COALESCE(Email,'') LIKE %s
            ORDER BY Guest_ID DESC
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))

        st.dataframe(guests, use_container_width=True)

        if guests:
            guest_map = {
                f'{g["Guest_ID"]} - {g["Guest_Name"]}': g for g in guests
            }
            selected = st.selectbox("Select a guest to edit/delete", list(guest_map))
            guest = guest_map[selected]

            with st.form("edit_guest"):
                new_name = st.text_input("Name", guest["Guest_Name"])
                new_phone = st.text_input("Phone", guest["Phone"])
                new_email = st.text_input("Email", guest["Email"] or "")
                new_address = st.text_area("Address", guest["Address"] or "")
                col1, col2 = st.columns(2)
                update = col1.form_submit_button("Update Guest")
                delete = col2.form_submit_button("Delete Guest")

            if update:
                try:
                    execute("""
                        UPDATE Guest
                        SET Guest_Name=%s, Phone=%s, Email=%s, Address=%s
                        WHERE Guest_ID=%s
                    """, (new_name.strip(), new_phone.strip(),
                          new_email.strip() or None, new_address.strip() or None,
                          guest["Guest_ID"]))
                    st.success("Guest updated.")
                    st.rerun()
                except Error as e:
                    st.error(str(e))

            if delete:
                try:
                    execute("DELETE FROM Guest WHERE Guest_ID=%s",
                            (guest["Guest_ID"],))
                    st.success("Guest deleted.")
                    st.rerun()
                except Error as e:
                    st.error("This guest may have related records. " + str(e))

    except Exception as e:
        st.error(str(e))


# ============================================================
# 6. ROOM MANAGEMENT
# ============================================================

elif page == "Room Management":
    st.header("Room Management")

    with st.form("add_room"):
        room_no = st.text_input("Room Number")
        room_type = st.selectbox(
            "Room Type", ["Single", "Double", "Deluxe", "Suite", "Family", "Other"]
        )
        price = st.number_input("Price Per Night", min_value=0.01, value=1500.0)
        status = st.selectbox("Status", ["Available", "Occupied", "Maintenance"])
        add = st.form_submit_button("Add Room")

    if add:
        try:
            execute("""
                INSERT INTO Room (Room_Number,Room_Type,Price_Per_Night,Status)
                VALUES (%s,%s,%s,%s)
            """, (room_no.strip(), room_type, price, status))
            st.success("Room added.")
            st.rerun()
        except Error as e:
            st.error(str(e))

    st.subheader("Room Inventory")
    try:
        st.dataframe(fetch_all("SELECT * FROM Room ORDER BY Room_Number"),
                     use_container_width=True)
    except Exception as e:
        st.error(str(e))

    st.subheader("Change Room Status")
    rooms = fetch_all("SELECT Room_ID, Room_Number, Status FROM Room")
    if rooms:
        room_map = {f'{r["Room_Number"]} ({r["Status"]})': r for r in rooms}
        choice = st.selectbox("Room", list(room_map))
        new_status = st.selectbox(
            "New Status", ["Available", "Occupied", "Maintenance"]
        )
        if st.button("Update Room Status"):
            try:
                execute("UPDATE Room SET Status=%s WHERE Room_ID=%s",
                        (new_status, room_map[choice]["Room_ID"]))
                st.success("Room status updated.")
                st.rerun()
            except Error as e:
                st.error(str(e))


# ============================================================
# 7. RESERVATIONS AND ROOM AVAILABILITY
# ============================================================

elif page == "Reservations":
    st.header("Reservations & Room Availability")

    guests = fetch_all("SELECT Guest_ID, Guest_Name FROM Guest ORDER BY Guest_Name")
    rooms = fetch_all(
        "SELECT Room_ID, Room_Number, Room_Type, Price_Per_Night "
        "FROM Room WHERE Status='Available' ORDER BY Room_Number"
    )

    if not guests:
        st.info("Add a guest before creating a reservation.")
    elif not rooms:
        st.info("No rooms are currently marked Available.")
    else:
        guest_map = {
            f'{g["Guest_ID"]} - {g["Guest_Name"]}': g["Guest_ID"] for g in guests
        }
        room_map = {
            f'{r["Room_Number"]} - {r["Room_Type"]} ({r["Price_Per_Night"]})':
                r["Room_ID"] for r in rooms
        }

        with st.form("reservation_form"):
            guest_label = st.selectbox("Guest", list(guest_map))
            room_label = st.selectbox("Room", list(room_map))
            checkin = st.date_input("Check-in", value=date.today())
            checkout = st.date_input(
                "Check-out", value=date.today() + timedelta(days=1)
            )
            number_guests = st.number_input(
                "Number of Guests", min_value=1, max_value=20, value=1
            )
            submit = st.form_submit_button("Create Reservation")

        if submit:
            if checkout <= checkin:
                st.error("Check-out must be after check-in.")
            else:
                room_id = room_map[room_label]
                overlap = fetch_all("""
                    SELECT COUNT(*) AS n FROM Reservation
                    WHERE Room_ID=%s AND Reservation_Status='Confirmed'
                      AND Check_In_Date < %s AND Check_Out_Date > %s
                """, (room_id, checkout, checkin))[0]["n"]

                if overlap:
                    st.error("That room is already reserved for those dates.")
                else:
                    try:
                        execute("""
                            INSERT INTO Reservation
                            (Guest_ID,Room_ID,Check_In_Date,Check_Out_Date,
                             Number_of_Guests,Reservation_Status)
                            VALUES (%s,%s,%s,%s,%s,'Confirmed')
                        """, (guest_map[guest_label], room_id, checkin, checkout,
                              number_guests))
                        st.success("Reservation created.")
                        st.rerun()
                    except Error as e:
                        st.error(str(e))

    st.subheader("Reservation Records")
    try:
        st.dataframe(fetch_all("""
            SELECT r.Reservation_ID, g.Guest_Name, rm.Room_Number,
                   r.Check_In_Date, r.Check_Out_Date, r.Number_of_Guests,
                   r.Reservation_Status
            FROM Reservation r
            JOIN Guest g ON r.Guest_ID=g.Guest_ID
            JOIN Room rm ON r.Room_ID=rm.Room_ID
            ORDER BY r.Reservation_ID DESC
        """), use_container_width=True)

        reservation_ids = fetch_all("""
            SELECT Reservation_ID FROM Reservation
            WHERE Reservation_Status='Confirmed'
        """)
        if reservation_ids:
            rid = st.selectbox(
                "Reservation to cancel",
                [r["Reservation_ID"] for r in reservation_ids]
            )
            if st.button("Cancel Reservation"):
                execute("""
                    UPDATE Reservation SET Reservation_Status='Cancelled'
                    WHERE Reservation_ID=%s
                """, (rid,))
                st.success("Reservation cancelled.")
                st.rerun()
    except Exception as e:
        st.error(str(e))


# ============================================================
# 8. RESTAURANT AND MENU MANAGEMENT
# ============================================================

elif page == "Restaurant & Menu":
    st.header("Restaurant & Menu Management")

    with st.expander("Add Restaurant"):
        with st.form("add_restaurant"):
            restaurant_name = st.text_input("Restaurant Name")
            location = st.text_input("Location")
            add_restaurant = st.form_submit_button("Add Restaurant")
        if add_restaurant:
            try:
                execute("""
                    INSERT INTO Restaurant (Restaurant_Name,Location)
                    VALUES (%s,%s)
                """, (restaurant_name.strip(), location.strip() or None))
                st.success("Restaurant added.")
                st.rerun()
            except Error as e:
                st.error(str(e))

    restaurants = fetch_all(
        "SELECT Restaurant_ID, Restaurant_Name FROM Restaurant ORDER BY Restaurant_Name"
    )

    if restaurants:
        restaurant_map = {
            f'{r["Restaurant_ID"]} - {r["Restaurant_Name"]}': r["Restaurant_ID"]
            for r in restaurants
        }

        with st.expander("Add Menu Item"):
            with st.form("add_menu_item"):
                restaurant_label = st.selectbox("Restaurant", list(restaurant_map))
                item_name = st.text_input("Menu Item Name")
                category = st.selectbox(
                    "Category", ["Breakfast", "Starter", "Main Course",
                                 "Dessert", "Beverage", "Other"]
                )
                item_price = st.number_input("Price", min_value=0.01, value=100.0)
                availability = st.selectbox(
                    "Availability", ["Available", "Unavailable"]
                )
                add_item = st.form_submit_button("Add Menu Item")
            if add_item:
                try:
                    execute("""
                        INSERT INTO Menu_Item
                        (Restaurant_ID,Item_Name,Category,Price,Availability)
                        VALUES (%s,%s,%s,%s,%s)
                    """, (restaurant_map[restaurant_label], item_name.strip(),
                          category, item_price, availability))
                    st.success("Menu item added.")
                    st.rerun()
                except Error as e:
                    st.error(str(e))

    st.subheader("Menu Items")
    try:
        st.dataframe(fetch_all("""
            SELECT m.Menu_Item_ID, r.Restaurant_Name, m.Item_Name,
                   m.Category, m.Price, m.Availability
            FROM Menu_Item m
            JOIN Restaurant r ON r.Restaurant_ID=m.Restaurant_ID
            ORDER BY r.Restaurant_Name, m.Item_Name
        """), use_container_width=True)
    except Exception as e:
        st.error(str(e))


# ============================================================
# 9. FOOD ORDERS AND SUBTOTAL CALCULATION
# ============================================================

elif page == "Food Orders":
    st.header("Food Orders")

    guests = fetch_all("SELECT Guest_ID, Guest_Name FROM Guest ORDER BY Guest_Name")
    restaurants = fetch_all(
        "SELECT Restaurant_ID, Restaurant_Name FROM Restaurant ORDER BY Restaurant_Name"
    )

    if not guests:
        st.info("Add a guest first.")
    elif not restaurants:
        st.info("Add a restaurant and menu items first.")
    else:
        guest_map = {
            f'{g["Guest_ID"]} - {g["Guest_Name"]}': g["Guest_ID"] for g in guests
        }
        restaurant_map = {
            f'{r["Restaurant_ID"]} - {r["Restaurant_Name"]}': r["Restaurant_ID"]
            for r in restaurants
        }

        guest_label = st.selectbox("Guest", list(guest_map))
        restaurant_label = st.selectbox("Restaurant", list(restaurant_map))

        menu = fetch_all("""
            SELECT Menu_Item_ID, Item_Name, Category, Price
            FROM Menu_Item
            WHERE Restaurant_ID=%s AND Availability='Available'
            ORDER BY Item_Name
        """, (restaurant_map[restaurant_label],))

        if menu:
            item_map = {
                f'{m["Item_Name"]} - {m["Price"]}': m for m in menu
            }
            item_label = st.selectbox("Menu Item", list(item_map))
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
            item = item_map[item_label]
            subtotal = Decimal(str(item["Price"])) * quantity
            st.metric("Order Subtotal", f"{subtotal:.2f}")

            if st.button("Place Food Order"):
                conn = None
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO `Food_Order`
                        (Guest_ID,Restaurant_ID,Order_Status)
                        VALUES (%s,%s,'Placed')
                    """, (guest_map[guest_label],
                          restaurant_map[restaurant_label]))
                    order_id = cur.lastrowid
                    cur.execute("""
                        INSERT INTO Order_Item
                        (Order_ID,Menu_Item_ID,Quantity,Unit_Price)
                        VALUES (%s,%s,%s,%s)
                    """, (order_id, item["Menu_Item_ID"], quantity, item["Price"]))
                    conn.commit()
                    cur.close()
                    st.success(f"Order #{order_id} created. Subtotal: {subtotal:.2f}")
                    st.rerun()
                except Exception as e:
                    if conn:
                        conn.rollback()
                    st.error(str(e))
                finally:
                    if conn:
                        conn.close()
        else:
            st.info("No available menu items for this restaurant.")

    st.subheader("Order History")
    try:
        st.dataframe(fetch_all("""
            SELECT fo.Order_ID, g.Guest_Name, r.Restaurant_Name,
                   fo.Order_Date, fo.Order_Status,
                   COALESCE(SUM(oi.Quantity*oi.Unit_Price),0) AS Subtotal
            FROM `Food_Order` fo
            JOIN Guest g ON g.Guest_ID=fo.Guest_ID
            JOIN Restaurant r ON r.Restaurant_ID=fo.Restaurant_ID
            LEFT JOIN Order_Item oi ON oi.Order_ID=fo.Order_ID
            GROUP BY fo.Order_ID, g.Guest_Name, r.Restaurant_Name,
                     fo.Order_Date, fo.Order_Status
            ORDER BY fo.Order_ID DESC
        """), use_container_width=True)
    except Exception as e:
        st.error(str(e))


# ============================================================
# 10. PAYMENTS
# ============================================================

elif page == "Payments":
    st.header("Payments")

    guests = fetch_all("SELECT Guest_ID, Guest_Name FROM Guest ORDER BY Guest_Name")
    reservations = fetch_all("""
        SELECT Reservation_ID, Guest_ID
        FROM Reservation ORDER BY Reservation_ID DESC
    """)

    if guests:
        guest_map = {
            f'{g["Guest_ID"]} - {g["Guest_Name"]}': g["Guest_ID"] for g in guests
        }
        reservation_map = {"No reservation linked": None}
        for r in reservations:
            reservation_map[f'Reservation #{r["Reservation_ID"]}'] = r["Reservation_ID"]

        with st.form("payment_form"):
            guest_label = st.selectbox("Guest", list(guest_map))
            reservation_label = st.selectbox(
                "Reservation (optional)", list(reservation_map)
            )
            amount = st.number_input("Amount", min_value=0.01, value=100.0)
            method = st.selectbox(
                "Payment Method", ["Cash", "Card", "UPI", "Bank Transfer", "Other"]
            )
            payment_status = st.selectbox(
                "Payment Status", ["Paid", "Pending", "Failed", "Refunded"]
            )
            submit_payment = st.form_submit_button("Record Payment")

        if submit_payment:
            try:
                execute("""
                    INSERT INTO Payment
                    (Guest_ID,Reservation_ID,Amount,Payment_Method,Payment_Status)
                    VALUES (%s,%s,%s,%s,%s)
                """, (guest_map[guest_label], reservation_map[reservation_label],
                      amount, method, payment_status))
                st.success("Payment recorded.")
                st.rerun()
            except Error as e:
                st.error(str(e))
    else:
        st.info("Add a guest before recording a payment.")

    st.subheader("Payment History")
    try:
        st.dataframe(fetch_all("""
            SELECT p.Payment_ID, g.Guest_Name, p.Reservation_ID,
                   p.Amount, p.Payment_Date, p.Payment_Method, p.Payment_Status
            FROM Payment p
            JOIN Guest g ON g.Guest_ID=p.Guest_ID
            ORDER BY p.Payment_ID DESC
        """), use_container_width=True)
    except Exception as e:
        st.error(str(e))


# ============================================================
# 11. STAFF AND SERVICE REQUESTS
# ============================================================

elif page == "Staff & Service Requests":
    st.header("Staff & Service Requests")

    with st.expander("Add Staff Member"):
        with st.form("add_staff"):
            staff_name = st.text_input("Staff Name")
            role = st.text_input("Role")
            phone = st.text_input("Staff Phone")
            salary = st.number_input("Salary", min_value=0.0, value=0.0)
            add_staff = st.form_submit_button("Add Staff")
        if add_staff:
            try:
                execute("""
                    INSERT INTO Staff (Staff_Name,Role,Phone,Salary)
                    VALUES (%s,%s,%s,%s)
                """, (staff_name.strip(), role.strip(), phone.strip() or None,
                      salary or None))
                st.success("Staff member added.")
                st.rerun()
            except Error as e:
                st.error(str(e))

    guests = fetch_all("SELECT Guest_ID, Guest_Name FROM Guest ORDER BY Guest_Name")
    staff = fetch_all("SELECT Staff_ID, Staff_Name FROM Staff ORDER BY Staff_Name")

    st.subheader("Create Service Request")
    if guests:
        guest_map = {
            f'{g["Guest_ID"]} - {g["Guest_Name"]}': g["Guest_ID"] for g in guests
        }
        staff_map = {"Unassigned": None}
        for s in staff:
            staff_map[f'{s["Staff_ID"]} - {s["Staff_Name"]}'] = s["Staff_ID"]

        with st.form("request_form"):
            guest_label = st.selectbox("Guest", list(guest_map))
            staff_label = st.selectbox("Assign Staff", list(staff_map))
            request_type = st.selectbox(
                "Request Type", ["Housekeeping", "Room Service",
                                 "Maintenance", "Restaurant", "Other"]
            )
            description = st.text_area("Description")
            status = st.selectbox(
                "Request Status", ["Pending", "In Progress", "Completed", "Cancelled"]
            )
            submit_request = st.form_submit_button("Create Request")

        if submit_request:
            try:
                execute("""
                    INSERT INTO Service_Request
                    (Guest_ID,Staff_ID,Request_Type,Request_Description,Request_Status)
                    VALUES (%s,%s,%s,%s,%s)
                """, (guest_map[guest_label], staff_map[staff_label], request_type,
                      description.strip() or None, status))
                st.success("Service request created.")
                st.rerun()
            except Error as e:
                st.error(str(e))
    else:
        st.info("Add a guest first.")

    st.subheader("Service Request Records")
    try:
        st.dataframe(fetch_all("""
            SELECT sr.Request_ID, g.Guest_Name, s.Staff_Name,
                   sr.Request_Type, sr.Request_Description,
                   sr.Request_Status, sr.Request_Date
            FROM Service_Request sr
            JOIN Guest g ON g.Guest_ID=sr.Guest_ID
            LEFT JOIN Staff s ON s.Staff_ID=sr.Staff_ID
            ORDER BY sr.Request_ID DESC
        """), use_container_width=True)
    except Exception as e:
        st.error(str(e))


# ============================================================
# 12. ADVANCED SQL ANALYTICS AND VIEW
# ============================================================

elif page == "SQL Analytics & Views":
    st.header("Advanced SQL Analytics & Views")

    analytics = {
        "Payments by Guest (JOIN + GROUP BY)": """
            SELECT g.Guest_ID, g.Guest_Name,
                   COALESCE(SUM(p.Amount),0) AS Total_Payments
            FROM Guest g
            LEFT JOIN Payment p
                ON p.Guest_ID=g.Guest_ID AND p.Payment_Status='Paid'
            GROUP BY g.Guest_ID,g.Guest_Name
            ORDER BY Total_Payments DESC
        """,
        "Menu Category Analysis (GROUP BY + HAVING)": """
            SELECT Category, COUNT(*) AS Item_Count, AVG(Price) AS Average_Price
            FROM Menu_Item
            GROUP BY Category
            HAVING COUNT(*) >= 1
            ORDER BY Item_Count DESC
        """,
        "Food Items by Units Sold": """
            SELECT m.Item_Name, SUM(oi.Quantity) AS Units_Sold,
                   SUM(oi.Quantity*oi.Unit_Price) AS Sales
            FROM Order_Item oi
            JOIN Menu_Item m ON m.Menu_Item_ID=oi.Menu_Item_ID
            GROUP BY m.Menu_Item_ID,m.Item_Name
            ORDER BY Units_Sold DESC
        """,
        "Restaurant Revenue": """
            SELECT r.Restaurant_Name,
                   COALESCE(SUM(oi.Quantity*oi.Unit_Price),0) AS Revenue
            FROM Restaurant r
            LEFT JOIN `Food_Order` fo ON fo.Restaurant_ID=r.Restaurant_ID
            LEFT JOIN Order_Item oi ON oi.Order_ID=fo.Order_ID
            GROUP BY r.Restaurant_ID,r.Restaurant_Name
            ORDER BY Revenue DESC
        """,
        "Rooms Above Average Price (Subquery)": """
            SELECT Room_ID,Room_Number,Room_Type,Price_Per_Night
            FROM Room
            WHERE Price_Per_Night > (SELECT AVG(Price_Per_Night) FROM Room)
            ORDER BY Price_Per_Night DESC
        """,
        "Billing Summary View": """
            SELECT * FROM View_Active_Billing_Summary
            ORDER BY Total_Paid DESC
        """,
        "Reservations with Guest and Room": """
            SELECT r.Reservation_ID,g.Guest_Name,rm.Room_Number,
                   r.Check_In_Date,r.Check_Out_Date,r.Reservation_Status
            FROM Reservation r
            JOIN Guest g ON g.Guest_ID=r.Guest_ID
            JOIN Room rm ON rm.Room_ID=r.Room_ID
            ORDER BY r.Check_In_Date
        """
    }

    choice = st.selectbox("Choose an SQL query", list(analytics))
    st.code(analytics[choice].strip(), language="sql")

    if st.button("Run Selected Query"):
        try:
            st.dataframe(fetch_all(analytics[choice]), use_container_width=True)
        except Error as e:
            st.error(str(e))

    st.divider()
    st.subheader("Custom SELECT Query")
    st.caption("For safety, this tool allows only SELECT or WITH queries.")
    custom_sql = st.text_area(
        "Enter SQL",
        "SELECT * FROM Guest LIMIT 20"
    )

    if st.button("Run Custom Query"):
        cleaned = custom_sql.strip().lower()
        if not (cleaned.startswith("select") or cleaned.startswith("with")):
            st.warning("Only SELECT or WITH queries are allowed.")
        elif ";" in cleaned.rstrip(";"):
            st.warning("Please enter one query at a time.")
        else:
            try:
                st.dataframe(fetch_all(custom_sql), use_container_width=True)
            except Error as e:
                st.error(str(e))


# ============================================================
# 13. TEST CASES AND CLOUD CONNECTION TEST
# ============================================================

elif page == "Test Database Connection":
    st.header("Test Cases & Database Connection")

    st.markdown("""
    | Test | Expected result |
    |---|---|
    | Add guest with valid details | Guest saved |
    | Add duplicate phone number | Error shown |
    | Create valid reservation | Reservation saved |
    | Check-out before check-in | Reservation rejected |
    | Reserve overlapping room dates | Reservation rejected |
    | Place a food order | Order and order item saved |
    | Record payment | Payment appears in history |
    | Run analytics | SQL result displayed |
    """)

    st.subheader("Test Cloud Database")
    if st.button("Test Connection Now"):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT DATABASE(), VERSION()")
            database_name, version = cur.fetchone()
            st.success(f"Connected successfully to database: {database_name}")
            st.write(f"Database server version: {version}")
            cur.close()
        except Exception as e:
            st.error("Connection failed. Check your cloud database settings.")
            st.code(str(e))
        finally:
            if conn is not None and conn.is_connected():
                conn.close()

    st.subheader("Subtotal Calculator")
    unit_price = st.number_input("Unit Price", min_value=0.0, value=100.0)
    quantity = st.number_input("Quantity", min_value=1, value=1)
    st.metric("Subtotal", f"{unit_price * quantity:.2f}")


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("Hotel and Restaurant Management System | Database Systems Project")
