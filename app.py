from pathlib import Path

code = r'''import re
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

import mysql.connector
from mysql.connector import Error
import streamlit as st

st.set_page_config(
    page_title="Hotel & Restaurant Management",
    page_icon="🏨",
    layout="wide",
)

st.title("🏨 Centralized Hotel & Restaurant Management System")
st.caption(
    "SANJAY THANDEESWARAN (25BCE2759) & "
    "MONISH KUMAR T O (25BCE2819)"
)
# ============================================================
# 1. CLOUD DATABASE CONNECTION
# Configure these values in Streamlit Cloud > App > Settings > Secrets:
#
# [mysql]
# host = "gateway01.ap-northeast-1.prod.aws.tidbcloud.com"
# port = 4000
# database = "test"
# user = "YOUR_TIDB_USERNAME"
# password = "YOUR_TIDB_PASSWORD"
# ============================================================

def get_connection():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 4000)),
        database=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
        connection_timeout=15,
        ssl_disabled=False,
    )


def close_db(conn=None, cursor=None):
    if cursor is not None:
        try:
            cursor.close()
        except Error:
            pass
    if conn is not None:
        try:
            if conn.is_connected():
                conn.close()
        except Error:
            pass


def fetch_all(sql, params=()):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        close_db(conn, cursor)


def execute_write(sql, params=()):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid, cursor.rowcount
    except Error:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        close_db(conn, cursor)


def money(value):
    return Decimal(str(value)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def valid_phone(phone):
    return len(re.sub(r"\D", "", phone)) == 10


# ============================================================
# 2. ORIGINAL DATABASE SCHEMA
# Uses the table and column names from your original application.
# It does not create a new database or rename existing columns.
# ============================================================

def initialize_database():
    statements = [
        """
        CREATE TABLE IF NOT EXISTS Guest (
            Guest_ID INT AUTO_INCREMENT PRIMARY KEY,
            Guest_Name VARCHAR(100) NOT NULL,
            Phone VARCHAR(20) NOT NULL UNIQUE,
            Email VARCHAR(100) UNIQUE,
            Address VARCHAR(255)
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS Room (
            Room_ID INT AUTO_INCREMENT PRIMARY KEY,
            Room_Number VARCHAR(10) NOT NULL UNIQUE,
            Room_Type VARCHAR(50) NOT NULL,
            Price_Per_Night DECIMAL(10,2) NOT NULL,
            Status VARCHAR(20) NOT NULL DEFAULT 'Available'
        ) ENGINE=InnoDB
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
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS Restaurant (
            Restaurant_ID INT AUTO_INCREMENT PRIMARY KEY,
            Restaurant_Name VARCHAR(100) NOT NULL,
            Location VARCHAR(100)
        ) ENGINE=InnoDB
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
        ) ENGINE=InnoDB
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
        ) ENGINE=InnoDB
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
        ) ENGINE=InnoDB
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
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS Staff (
            Staff_ID INT AUTO_INCREMENT PRIMARY KEY,
            Staff_Name VARCHAR(100) NOT NULL,
            Role VARCHAR(50) NOT NULL,
            Phone VARCHAR(20),
            Salary DECIMAL(10,2)
        ) ENGINE=InnoDB
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
        ) ENGINE=InnoDB
        """,
        """
        CREATE OR REPLACE VIEW View_Active_Billing_Summary AS
        SELECT
            g.Guest_ID,
            g.Guest_Name,
            COALESCE(SUM(
                CASE WHEN p.Payment_Status = 'Paid' THEN p.Amount ELSE 0 END
            ), 0) AS Total_Paid
        FROM Guest g
        LEFT JOIN Payment p ON g.Guest_ID = p.Guest_ID
        GROUP BY g.Guest_ID, g.Guest_Name
        """,
    ]

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        for statement in statements:
            cursor.execute(statement)
        conn.commit()
        return True, "Cloud database connection successful; tables/view checked."
    except (Error, KeyError, TypeError, ValueError) as err:
        if conn is not None:
            try:
                conn.rollback()
            except Error:
                pass
        return False, str(err)
    finally:
        close_db(conn, cursor)


def ensure_ready():
    if not st.session_state.get("db_ready", False):
        st.warning(
            "Use **Initialize / Test Database** in the sidebar first. "
            "Your TiDB user must have permission to create tables and the view."
        )
        return False
    return True


# ============================================================
# 3. SIDEBAR / CONNECTION STATUS
# ============================================================

with st.sidebar:
    st.header("🔑 Cloud Database")
    st.caption("Uses the [mysql] credentials saved in Streamlit Secrets.")
    if st.button(
        "Initialize / Test Database",
        type="primary",
        use_container_width=True,
    ):
        ok, message = initialize_database()
        st.session_state["db_ready"] = ok
        if ok:
            st.success(message)
        else:
            st.error(message)

    if st.session_state.get("db_ready", False):
        st.success("Database ready for this session.")
    else:
        st.info("Connect to your cloud database to begin.")

    st.divider()
    st.caption("Database Systems Project")


# ============================================================
# 4. MODULE SELECTOR
# ============================================================

module = st.selectbox(
    "Select Module",
    [
        "1. Guest Management (CRUD)",
        "2. Room Availability & Search",
        "3. Food Orders & Subtotal",
        "4. Advanced SQL Analytics & Views",
        "5. Test Cases & Validation",
    ],
)

# ============================================================
# MODULE 1: GUEST CRUD
# ============================================================

if module == "1. Guest Management (CRUD)":
    st.header("👤 Guest Management Operations")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Add Guest", "View / Search", "Update Guest", "Delete Guest"]
    )

    with tab1:
        st.subheader("Register New Guest")
        with st.form("add_guest_form"):
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone Number (10 digits) *")
            email = st.text_input("Email Address")
            address = st.text_area("Postal Address")
            submitted = st.form_submit_button("Save Guest")

        if submitted and ensure_ready():
            if not name.strip():
                st.error("Guest name is required.")
            elif not valid_phone(phone):
                st.error("Enter a valid 10-digit phone number.")
            elif email.strip() and not re.fullmatch(
                r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()
            ):
                st.error("Enter a valid email address.")
            else:
                try:
                    guest_id, _ = execute_write(
                        """
                        INSERT INTO Guest (Guest_Name, Phone, Email, Address)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            name.strip(), phone.strip(),
                            email.strip() or None, address.strip() or None,
                        ),
                    )
                    st.success(f"Guest saved successfully! Guest ID: {guest_id}")
                except Error as err:
                    st.error(f"Database error: {err}")

    with tab2:
        st.subheader("Search and Retrieve Guests")
        search_term = st.text_input("Search by name, phone, or email")
        if st.button("Search Guests"):
            if ensure_ready():
                try:
                    term = f"%{search_term.strip()}%"
                    rows = fetch_all(
                        """
                        SELECT * FROM Guest
                        WHERE Guest_Name LIKE %s
                           OR Phone LIKE %s
                           OR COALESCE(Email, '') LIKE %s
                        ORDER BY Guest_ID DESC
                        """,
                        (term, term, term),
                    )
                    if rows:
                        st.dataframe(rows, use_container_width=True, hide_index=True)
                    else:
                        st.info("No guests found.")
                except Error as err:
                    st.error(f"Database error: {err}")

    with tab3:
        st.subheader("Update Guest Details")
        with st.form("update_guest_form"):
            gid_update = st.number_input(
                "Guest ID", min_value=1, step=1, key="update_guest_id"
            )
            new_name = st.text_input("New Guest Name")
            new_phone = st.text_input("New Phone Number")
            new_email = st.text_input("New Email Address")
            new_address = st.text_area("New Address")
            update_btn = st.form_submit_button("Update Guest")

        if update_btn and ensure_ready():
            if not new_name.strip():
                st.error("Guest name cannot be empty.")
            elif not valid_phone(new_phone):
                st.error("Enter a valid 10-digit phone number.")
            elif new_email.strip() and not re.fullmatch(
                r"[^@\s]+@[^@\s]+\.[^@\s]+", new_email.strip()
            ):
                st.error("Enter a valid email address.")
            else:
                try:
                    _, affected = execute_write(
                        """
                        UPDATE Guest
                        SET Guest_Name=%s, Phone=%s, Email=%s, Address=%s
                        WHERE Guest_ID=%s
                        """,
                        (
                            new_name.strip(), new_phone.strip(),
                            new_email.strip() or None, new_address.strip() or None,
                            gid_update,
                        ),
                    )
                    if affected:
                        st.success("Guest record updated successfully.")
                    else:
                        st.warning("No record changed. Check the ID or values.")
                except Error as err:
                    st.error(f"Database error: {err}")

    with tab4:
        st.subheader("Delete Guest Record")
        st.warning(
            "A guest with linked reservations, orders, payments, or service "
            "requests cannot be deleted while those related records exist."
        )
        with st.form("delete_guest_form"):
            gid_del = st.number_input(
                "Guest ID to Delete", min_value=1, step=1, key="delete_guest_id"
            )
            confirm_delete = st.checkbox("I confirm that I want to delete this guest.")
            delete_btn = st.form_submit_button("Delete Guest")

        if delete_btn and ensure_ready():
            if not confirm_delete:
                st.error("Confirm the deletion first.")
            else:
                try:
                    _, affected = execute_write(
                        "DELETE FROM Guest WHERE Guest_ID=%s", (gid_del,)
                    )
                    if affected:
                        st.success("Guest deleted successfully.")
                    else:
                        st.warning("Guest ID not found.")
                except Error as err:
                    st.error(f"Guest could not be deleted. Related records may exist: {err}")


# ============================================================
# MODULE 2: ROOM INVENTORY / DATE-BASED AVAILABILITY
# ============================================================

elif module == "2. Room Availability & Search":
    st.header("🛏️ Room Availability & Search")
    tab1, tab2 = st.tabs(["Room Inventory", "Date-Based Availability"])

    with tab1:
        status_filter = st.selectbox(
            "Filter by Room Status",
            ["All", "Available", "Occupied", "Maintenance"],
        )
        if st.button("Load Rooms"):
            if ensure_ready():
                try:
                    if status_filter == "All":
                        rooms = fetch_all(
                            "SELECT * FROM Room ORDER BY Price_Per_Night ASC"
                        )
                    else:
                        rooms = fetch_all(
                            """
                            SELECT * FROM Room WHERE Status=%s
                            ORDER BY Price_Per_Night ASC
                            """,
                            (status_filter,),
                        )
                    if rooms:
                        st.dataframe(rooms, use_container_width=True, hide_index=True)
                    else:
                        st.info("No rooms found. Add room records to the database.")
                except Error as err:
                    st.error(f"Database error: {err}")

    with tab2:
        st.subheader("Check room availability for selected dates")
        today = date.today()
        c1, c2 = st.columns(2)
        with c1:
            check_in = st.date_input(
                "Check-in Date", value=today, min_value=today, key="room_check_in"
            )
        with c2:
            check_out = st.date_input(
                "Check-out Date",
                value=today + timedelta(days=1),
                min_value=today + timedelta(days=1),
                key="room_check_out",
            )

        if st.button("Find Available Rooms"):
            if not ensure_ready():
                pass
            elif check_out <= check_in:
                st.error("Check-out must be after check-in.")
            else:
                try:
                    rooms = fetch_all(
                        """
                        SELECT rm.*
                        FROM Room rm
                        WHERE rm.Status='Available'
                          AND NOT EXISTS (
                              SELECT 1
                              FROM Reservation r
                              WHERE r.Room_ID=rm.Room_ID
                                AND r.Reservation_Status='Confirmed'
                                AND r.Check_In_Date < %s
                                AND r.Check_Out_Date > %s
                          )
                        ORDER BY rm.Price_Per_Night ASC
                        """,
                        (check_out, check_in),
                    )
                    if rooms:
                        st.success(
                            f"Found {len(rooms)} room(s) from {check_in} to {check_out}."
                        )
                        st.dataframe(rooms, use_container_width=True, hide_index=True)
                    else:
                        st.info("No rooms match those dates and current room status.")
                except Error as err:
                    st.error(f"Database error: {err}")

        st.caption(
            "Availability uses confirmed reservation date overlaps and the Room "
            "Status field. The app does not automatically change a room's status."
        )


# ============================================================
# MODULE 3: FOOD ORDERS / SUBTOTAL
# ============================================================

elif module == "3. Food Orders & Subtotal":
    st.header("🍽️ Food Orders & Automatic Subtotal")
    st.caption(
        "This screen creates one food order with one menu item per submission. "
        "The database schema supports multiple Order_Item rows per order."
    )

    if ensure_ready():
        try:
            guests = fetch_all(
                "SELECT Guest_ID, Guest_Name FROM Guest ORDER BY Guest_Name"
            )
            restaurants = fetch_all(
                "SELECT Restaurant_ID, Restaurant_Name FROM Restaurant ORDER BY Restaurant_Name"
            )

            if not guests:
                st.warning("Add at least one guest first.")
            elif not restaurants:
                st.warning("Add a restaurant and menu items in the database first.")
            else:
                guest_options = {
                    f"{g['Guest_Name']} (ID: {g['Guest_ID']})": g["Guest_ID"]
                    for g in guests
                }
                restaurant_options = {
                    f"{r['Restaurant_Name']} (ID: {r['Restaurant_ID']})":
                    r["Restaurant_ID"]
                    for r in restaurants
                }

                with st.form("order_form"):
                    selected_guest = st.selectbox("Select Guest", list(guest_options))
                    selected_restaurant = st.selectbox(
                        "Select Restaurant", list(restaurant_options)
                    )

                    selected_restaurant_id = restaurant_options[selected_restaurant]
                    menu_items = fetch_all(
                        """
                        SELECT Menu_Item_ID, Item_Name, Category, Price
                        FROM Menu_Item
                        WHERE Restaurant_ID=%s AND Availability='Available'
                        ORDER BY Item_Name
                        """,
                        (selected_restaurant_id,),
                    )

                    if menu_items:
                        item_options = {
                            f"{m['Item_Name']} — ₹{money(m['Price']):.2f} "
                            f"(ID: {m['Menu_Item_ID']})": m
                            for m in menu_items
                        }
                        selected_item_label = st.selectbox(
                            "Menu Item", list(item_options)
                        )
                        quantity = st.number_input(
                            "Quantity", min_value=1, max_value=100, value=1, step=1
                        )
                        selected_item = item_options[selected_item_label]
                        subtotal = money(
                            Decimal(str(selected_item["Price"])) * int(quantity)
                        )
                        st.write(f"**Unit price:** ₹{money(selected_item['Price']):.2f}")
                        st.metric("Order Subtotal", f"₹{subtotal:.2f}")
                        place_order = st.form_submit_button("Place Food Order")
                    else:
                        st.info("No available menu items for this restaurant.")
                        selected_item = None
                        quantity = 1
                        place_order = st.form_submit_button("Place Food Order", disabled=True)

                if place_order and selected_item:
                    conn = None
                    cursor = None
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        # Recheck availability and price at order time.
                        cursor.execute(
                            """
                            SELECT Price, Availability
                            FROM Menu_Item
                            WHERE Menu_Item_ID=%s AND Restaurant_ID=%s
                            """,
                            (selected_item["Menu_Item_ID"], selected_restaurant_id),
                        )
                        current_item = cursor.fetchone()
                        if not current_item or current_item[1] != "Available":
                            st.error("This menu item is no longer available.")
                        else:
                            unit_price = money(current_item[0])
                            subtotal = money(unit_price * int(quantity))
                            cursor.execute(
                                """
                                INSERT INTO `Food_Order`
                                    (Guest_ID, Restaurant_ID, Order_Status)
                                VALUES (%s, %s, 'Placed')
                                """,
                                (guest_options[selected_guest], selected_restaurant_id),
                            )
                            order_id = cursor.lastrowid
                            cursor.execute(
                                """
                                INSERT INTO Order_Item
                                    (Order_ID, Menu_Item_ID, Quantity, Unit_Price)
                                VALUES (%s, %s, %s, %s)
                                """,
                                (
                                    order_id,
                                    selected_item["Menu_Item_ID"],
                                    int(quantity),
                                    unit_price,
                                ),
                            )
                            conn.commit()
                            st.success(f"Order #{order_id} placed successfully!")
                            st.write(f"**Item:** {selected_item['Item_Name']}")
                            st.write(f"**Quantity:** {quantity}")
                            st.write(f"**Subtotal:** ₹{subtotal:.2f}")
                    except Error as err:
                        if conn is not None:
                            conn.rollback()
                        st.error(f"Order transaction failed: {err}")
                    finally:
                        close_db(conn, cursor)

        except Error as err:
            st.error(f"Unable to load order data: {err}")

    st.divider()
    st.subheader("Recent Food Orders")
    if st.button("Load Food Order History"):
        if ensure_ready():
            try:
                orders = fetch_all(
                    """
                    SELECT
                        fo.Order_ID,
                        g.Guest_Name,
                        r.Restaurant_Name,
                        fo.Order_Date,
                        fo.Order_Status,
                        COALESCE(SUM(oi.Quantity * oi.Unit_Price), 0) AS Subtotal
                    FROM `Food_Order` fo
                    JOIN Guest g ON g.Guest_ID=fo.Guest_ID
                    JOIN Restaurant r ON r.Restaurant_ID=fo.Restaurant_ID
                    LEFT JOIN Order_Item oi ON oi.Order_ID=fo.Order_ID
                    GROUP BY fo.Order_ID, g.Guest_Name, r.Restaurant_Name,
                             fo.Order_Date, fo.Order_Status
                    ORDER BY fo.Order_ID DESC
                    """
                )
                if orders:
                    st.dataframe(orders, use_container_width=True, hide_index=True)
                else:
                    st.info("No food orders have been recorded.")
            except Error as err:
                st.error(f"Database error: {err}")


# ============================================================
# MODULE 4: ANALYTICS / VIEW
# ============================================================

elif module == "4. Advanced SQL Analytics & Views":
    st.header("📊 Advanced SQL Analytics & Views")

    query_choice = st.selectbox(
        "Select Analytical Report",
        [
            "1. JOIN & Aggregate: Total Paid per Guest",
            "2. GROUP BY: Menu Categories and Average Price",
            "3. Subquery: Rooms Above Average Price",
            "4. View: Active Billing Summary",
            "5. JOIN: Most Ordered Menu Items",
            "6. Aggregate: Restaurant Food Sales",
            "7. JOIN: Reservations with Guest and Room",
        ],
    )

    query_map = {
        "1": """
            SELECT g.Guest_ID, g.Guest_Name,
                   COUNT(CASE WHEN p.Payment_Status='Paid' THEN 1 END) AS Paid_Transactions,
                   COALESCE(SUM(CASE WHEN p.Payment_Status='Paid'
                                     THEN p.Amount ELSE 0 END), 0) AS Total_Paid
            FROM Guest g
            LEFT JOIN Payment p ON p.Guest_ID=g.Guest_ID
            GROUP BY g.Guest_ID, g.Guest_Name
            ORDER BY Total_Paid DESC
        """,
        "2": """
            SELECT Category, COUNT(*) AS Item_Count, AVG(Price) AS Average_Price
            FROM Menu_Item
            GROUP BY Category
            HAVING COUNT(*) >= 1
            ORDER BY Item_Count DESC
        """,
        "3": """
            SELECT Room_ID, Room_Number, Room_Type, Price_Per_Night
            FROM Room
            WHERE Price_Per_Night > (SELECT AVG(Price_Per_Night) FROM Room)
            ORDER BY Price_Per_Night DESC
        """,
        "4": """
            SELECT * FROM View_Active_Billing_Summary
            ORDER BY Total_Paid DESC
        """,
        "5": """
            SELECT m.Menu_Item_ID, m.Item_Name,
                   SUM(oi.Quantity) AS Units_Sold,
                   SUM(oi.Quantity * oi.Unit_Price) AS Sales
            FROM Order_Item oi
            JOIN Menu_Item m ON m.Menu_Item_ID=oi.Menu_Item_ID
            JOIN `Food_Order` fo ON fo.Order_ID=oi.Order_ID
            WHERE fo.Order_Status <> 'Cancelled'
            GROUP BY m.Menu_Item_ID, m.Item_Name
            ORDER BY Units_Sold DESC
        """,
        "6": """
            SELECT r.Restaurant_ID, r.Restaurant_Name,
                   COALESCE(SUM(
                       CASE WHEN fo.Order_Status <> 'Cancelled'
                            THEN oi.Quantity * oi.Unit_Price ELSE 0 END
                   ), 0) AS Food_Sales
            FROM Restaurant r
            LEFT JOIN `Food_Order` fo ON fo.Restaurant_ID=r.Restaurant_ID
            LEFT JOIN Order_Item oi ON oi.Order_ID=fo.Order_ID
            GROUP BY r.Restaurant_ID, r.Restaurant_Name
            ORDER BY Food_Sales DESC
        """,
        "7": """
            SELECT r.Reservation_ID, g.Guest_Name, rm.Room_Number,
                   r.Check_In_Date, r.Check_Out_Date, r.Number_of_Guests,
                   r.Reservation_Status
            FROM Reservation r
            JOIN Guest g ON g.Guest_ID=r.Guest_ID
            JOIN Room rm ON rm.Room_ID=r.Room_ID
            ORDER BY r.Check_In_Date
        """,
    }

    if st.button("Execute Query", type="primary"):
        if ensure_ready():
            query_key = query_choice.split(".")[0]
            sql = query_map[query_key]
            st.subheader("SQL Query")
            st.code(sql.strip(), language="sql")
            try:
                results = fetch_all(sql)
                if results:
                    st.success(f"Query executed. {len(results)} row(s) returned.")
                    st.dataframe(results, use_container_width=True, hide_index=True)
                else:
                    st.info("Query executed successfully, but returned no rows.")
            except Error as err:
                st.error(f"Query execution error: {err}")

    st.info(
        "The billing view reports paid amounts recorded against each guest. "
        "It is not a hotel invoice balance or a combined restaurant bill."
    )


# ============================================================
# MODULE 5: TEST CASES / VALIDATION
# ============================================================

elif module == "5. Test Cases & Validation":
    st.header("🧪 Test Case Verification Matrix")

    test_cases = [
        {
            "Test ID": "TC-01",
            "Module": "Guest CRUD",
            "Input": "Empty name / invalid phone",
            "Expected Result": "Input rejected",
            "Implementation": "UI validation",
        },
        {
            "Test ID": "TC-02",
            "Module": "Reservation",
            "Input": "Check-out before check-in",
            "Expected Result": "Reservation rejected",
            "Implementation": "Date validation in reservation workflow",
        },
        {
            "Test ID": "TC-03",
            "Module": "Food Order",
            "Input": "Unavailable menu item",
            "Expected Result": "Order rejected",
            "Implementation": "Availability rechecked before insertion",
        },
        {
            "Test ID": "TC-04",
            "Module": "Subtotal",
            "Input": "Quantity=2, price=250.00",
            "Expected Result": "Subtotal=500.00",
            "Implementation": "Decimal calculation",
        },
        {
            "Test ID": "TC-05",
            "Module": "Guest Delete",
            "Input": "Delete guest with related records",
            "Expected Result": "Delete restricted",
            "Implementation": "Foreign-key constraints",
        },
        {
            "Test ID": "TC-06",
            "Module": "Room Availability",
            "Input": "Overlapping confirmed reservation",
            "Expected Result": "Room excluded",
            "Implementation": "NOT EXISTS date-overlap query",
        },
        {
            "Test ID": "TC-07",
            "Module": "Order Transaction",
            "Input": "Order item insert fails",
            "Expected Result": "Order rolled back",
            "Implementation": "Commit/rollback transaction",
        },
        {
            "Test ID": "TC-08",
            "Module": "SQL Analytics",
            "Input": "Run aggregate, joins and subqueries",
            "Expected Result": "Report results displayed",
            "Implementation": "Analytics query module",
        },
    ]

    st.dataframe(test_cases, use_container_width=True, hide_index=True)
    st.warning(
        "These are test definitions, not proof that every test passed. "
        "Run the tests on your populated database and record the actual results."
    )

    st.subheader("Quick Subtotal Validation")
    c1, c2 = st.columns(2)
    with c1:
        test_price = st.number_input(
            "Unit Price (₹)", min_value=0.0, value=250.0, step=10.0
        )
    with c2:
        test_qty = st.number_input(
            "Quantity", min_value=1, value=2, step=1
        )

    subtotal = money(Decimal(str(test_price)) * int(test_qty))
    st.metric("Calculated Subtotal", f"₹{subtotal:.2f}")

    if st.button("Verify Example TC-04"):
        if money(Decimal(str(test_price))) == Decimal("250.00") and int(test_qty) == 2:
            if subtotal == Decimal("500.00"):
                st.success("TC-04 passed: subtotal equals ₹500.00.")
            else:
                st.error("TC-04 failed.")
        else:
            st.info("For the example test, use unit price ₹250 and quantity 2.")


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption(
    "Hotel and Restaurant Management System | "
    "Database Systems Project | Streamlit + TiDB Cloud"
)
'''
path = Path("/mnt/data/hotel_restaurant_app.py")
path.write_text(code, encoding="utf-8")
print(f"Created {path} ({len(code.splitlines())} lines)")
