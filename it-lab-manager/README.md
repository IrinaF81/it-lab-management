# IT Lab Manager

#### Video Demo: <(https://youtu.be/DUn163Fgh2k)>

#### Description:

IT Lab Manager is a web-based application built with Python, Flask, SQLite, HTML, CSS and JavaScript. The purpose of the application is to help students and junior system administrators document a small IT lab environment. The project focuses on practical infrastructure topics such as servers, clients, IP addresses, gateways, DNS servers, DHCP, NAT and troubleshooting tickets.

The application allows users to register, log in and manage their own IT lab data. After logging in, a user can add network devices such as servers, clients, routers, switches, access points and printers. For every device, the user can store the hostname, device type, IP address, subnet mask, gateway, DNS server, operating system, role, location and notes. The application also includes a troubleshooting ticket system where the user can document technical problems, assign them to devices, update their status and record possible solutions.

The main file of the project is `app.py`. It contains the Flask application, all routes, session handling, authentication logic and database queries. The application uses SQLite as its database. The database structure is defined in `schema.sql`, which creates the tables for users, devices and tickets. The file `init_db.py` is used to create the database file `lab.db` based on the SQL schema.

The `templates` folder contains the HTML pages of the application. `layout.html` defines the common page structure and navigation bar. `index.html` is the home page with a visual overview of the project. `dashboard.html` shows statistics about the lab, such as total devices, servers, clients and open tickets. `devices.html` displays all documented devices, while `add_device.html` and `edit_device.html` are used to create and update device information. The ticket pages, including `tickets.html`, `add_ticket.html` and `edit_ticket.html`, allow the user to manage troubleshooting tickets.

The `static` folder contains the visual and interactive parts of the frontend. `style.css` defines the layout, colors, dark tech design, tables, forms, buttons and responsive behavior. `script.js` contains JavaScript functions for filtering devices, confirming delete actions and validating IPv4 addresses before submitting a device form.

I chose SQLite because it is simple, lightweight and suitable for a small student project. Flask was chosen because it works well with Python and HTML templates and makes it possible to build a clear web application without unnecessary complexity. I designed the project around IT system integration because the topic connects programming with real infrastructure tasks such as network documentation, server roles and troubleshooting.

One important design choice was to keep the interface practical rather than overloaded. The application is meant to support a realistic lab workflow: document devices, check IP information, create tickets and update solutions. The dashboard gives a quick overview, while the device and ticket tables provide detailed information. JavaScript is used only where it improves usability, for example for live filtering and basic form validation.

Overall, IT Lab Manager demonstrates the use of Python for backend logic, SQL for structured data storage, HTML and CSS for the user interface and JavaScript for interactivity. The project is also personally useful because it reflects the kind of infrastructure documentation and troubleshooting tasks that are relevant in IT system integration.
