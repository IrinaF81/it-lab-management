import sqlite3
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "change-this-secret-key"


def get_db_connection():
    connection = sqlite3.connect("lab.db")
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()

    total_devices = connection.execute(
        "SELECT COUNT(*) FROM devices WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()[0]

    total_servers = connection.execute(
        "SELECT COUNT(*) FROM devices WHERE user_id = ? AND device_type = 'Server'",
        (session["user_id"],)
    ).fetchone()[0]

    total_clients = connection.execute(
        "SELECT COUNT(*) FROM devices WHERE user_id = ? AND device_type = 'Client'",
        (session["user_id"],)
    ).fetchone()[0]

    open_tickets = connection.execute("""
        SELECT COUNT(*)
        FROM tickets
        JOIN devices ON tickets.device_id = devices.id
        WHERE devices.user_id = ? AND tickets.status = 'open'
    """, (session["user_id"],)).fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        total_devices=total_devices,
        total_servers=total_servers,
        total_clients=total_clients,
        open_tickets=open_tickets
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            flash("All fields are required.")
            return redirect("/register")

        if password != confirmation:
            flash("Passwords do not match.")
            return redirect("/register")

        password_hash = generate_password_hash(password)

        connection = get_db_connection()

        try:
            connection.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                (username, password_hash)
            )
            connection.commit()

        except sqlite3.IntegrityError:
            connection.close()
            flash("Username already exists.")
            return redirect("/register")

        connection.close()

        flash("Account created successfully. Please log in.")
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required.")
            return redirect("/login")

        connection = get_db_connection()

        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        connection.close()

        if user is None or not check_password_hash(user["hash"], password):
            flash("Invalid username or password.")
            return redirect("/login")

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/devices")
def devices():
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()

    devices = connection.execute(
        "SELECT * FROM devices WHERE user_id = ? ORDER BY hostname",
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template("devices.html", devices=devices)


@app.route("/devices/add", methods=["GET", "POST"])
def add_device():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        hostname = request.form.get("hostname")
        device_type = request.form.get("device_type")
        ip_address = request.form.get("ip_address")

        if not hostname or not device_type or not ip_address:
            flash("Hostname, device type and IP address are required.")
            return redirect("/devices/add")

        connection = get_db_connection()

        connection.execute("""
            INSERT INTO devices
            (
                user_id,
                hostname,
                device_type,
                ip_address,
                subnet_mask,
                gateway,
                dns_server,
                operating_system,
                role,
                location,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            hostname,
            device_type,
            ip_address,
            request.form.get("subnet_mask"),
            request.form.get("gateway"),
            request.form.get("dns_server"),
            request.form.get("operating_system"),
            request.form.get("role"),
            request.form.get("location"),
            request.form.get("notes")
        ))

        connection.commit()
        connection.close()

        flash("Device added successfully.")
        return redirect("/devices")

    return render_template("add_device.html")


@app.route("/devices/<int:device_id>/edit", methods=["GET", "POST"])
def edit_device(device_id):
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()

    device = connection.execute(
        "SELECT * FROM devices WHERE id = ? AND user_id = ?",
        (device_id, session["user_id"])
    ).fetchone()

    if device is None:
        connection.close()
        flash("Device not found.")
        return redirect("/devices")

    if request.method == "POST":
        hostname = request.form.get("hostname")
        device_type = request.form.get("device_type")
        ip_address = request.form.get("ip_address")

        if not hostname or not device_type or not ip_address:
            connection.close()
            flash("Hostname, device type and IP address are required.")
            return redirect(f"/devices/{device_id}/edit")

        connection.execute("""
            UPDATE devices
            SET hostname = ?,
                device_type = ?,
                ip_address = ?,
                subnet_mask = ?,
                gateway = ?,
                dns_server = ?,
                operating_system = ?,
                role = ?,
                location = ?,
                notes = ?
            WHERE id = ? AND user_id = ?
        """, (
            hostname,
            device_type,
            ip_address,
            request.form.get("subnet_mask"),
            request.form.get("gateway"),
            request.form.get("dns_server"),
            request.form.get("operating_system"),
            request.form.get("role"),
            request.form.get("location"),
            request.form.get("notes"),
            device_id,
            session["user_id"]
        ))

        connection.commit()
        connection.close()

        flash("Device updated successfully.")
        return redirect("/devices")

    connection.close()
    return render_template("edit_device.html", device=device)


@app.route("/devices/<int:device_id>/delete", methods=["POST"])
def delete_device(device_id):
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM devices WHERE id = ? AND user_id = ?",
        (device_id, session["user_id"])
    )

    connection.commit()
    connection.close()

    flash("Device deleted successfully.")
    return redirect("/devices")

@app.route("/tickets")
def tickets():
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()

    tickets = connection.execute("""
        SELECT tickets.*, devices.hostname
        FROM tickets
        JOIN devices ON tickets.device_id = devices.id
        WHERE devices.user_id = ?
        ORDER BY tickets.created_at DESC
    """, (session["user_id"],)).fetchall()

    connection.close()

    return render_template("tickets.html", tickets=tickets)


@app.route("/tickets/add", methods=["GET", "POST"])
def add_ticket():
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()

    devices = connection.execute(
        "SELECT * FROM devices WHERE user_id = ? ORDER BY hostname",
        (session["user_id"],)
    ).fetchall()

    if request.method == "POST":
        device_id = request.form.get("device_id")
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status")
        solution = request.form.get("solution")

        if not device_id or not title or not description:
            connection.close()
            flash("Device, title and description are required.")
            return redirect("/tickets/add")

        connection.execute("""
            INSERT INTO tickets
            (device_id, title, description, status, solution)
            VALUES (?, ?, ?, ?, ?)
        """, (
            device_id,
            title,
            description,
            status,
            solution
        ))

        connection.commit()
        connection.close()

        flash("Ticket added successfully.")
        return redirect("/tickets")

    connection.close()

    return render_template("add_ticket.html", devices=devices)

@app.route("/tickets/<int:ticket_id>/edit", methods=["GET", "POST"])
def edit_ticket(ticket_id):
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()

    ticket = connection.execute("""
        SELECT tickets.*
        FROM tickets
        JOIN devices ON tickets.device_id = devices.id
        WHERE tickets.id = ? AND devices.user_id = ?
    """, (ticket_id, session["user_id"])).fetchone()

    if ticket is None:
        connection.close()
        flash("Ticket not found.")
        return redirect("/tickets")

    devices = connection.execute(
        "SELECT * FROM devices WHERE user_id = ? ORDER BY hostname",
        (session["user_id"],)
    ).fetchall()

    if request.method == "POST":
        device_id = request.form.get("device_id")
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status")
        solution = request.form.get("solution")

        if not device_id or not title or not description:
            connection.close()
            flash("Device, title and description are required.")
            return redirect(f"/tickets/{ticket_id}/edit")

        connection.execute("""
            UPDATE tickets
            SET device_id = ?,
                title = ?,
                description = ?,
                status = ?,
                solution = ?
            WHERE id = ?
        """, (
            device_id,
            title,
            description,
            status,
            solution,
            ticket_id
        ))

        connection.commit()
        connection.close()

        flash("Ticket updated successfully.")
        return redirect("/tickets")

    connection.close()

    return render_template(
        "edit_ticket.html",
        ticket=ticket,
        devices=devices
    )


@app.route("/tickets/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket(ticket_id):
    if "user_id" not in session:
        return redirect("/login")

    connection = get_db_connection()

    connection.execute("""
        DELETE FROM tickets
        WHERE id = ?
        AND device_id IN (
            SELECT id FROM devices WHERE user_id = ?
        )
    """, (ticket_id, session["user_id"]))

    connection.commit()
    connection.close()

    flash("Ticket deleted successfully.")
    return redirect("/tickets")

if __name__ == "__main__":
    app.run(debug=True)