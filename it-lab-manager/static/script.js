function filterDevices() {
    const input = document.getElementById("deviceSearch");
    const table = document.getElementById("devicesTable");

    if (!input || !table) {
        return;
    }

    const filter = input.value.toLowerCase();
    const rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        const rowText = rows[i].innerText.toLowerCase();

        if (rowText.includes(filter)) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
        }
    }
}


function confirmDelete() {
    return confirm("Are you sure you want to delete this device?");
}


function validateDeviceForm() {
    const ipInput = document.querySelector("input[name='ip_address']");

    if (!ipInput) {
        return true;
    }

    const ip = ipInput.value.trim();

    const ipPattern =
        /^(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)){3}$/;

    if (!ipPattern.test(ip)) {
        alert("Please enter a valid IPv4 address, for example 10.1.1.10");
        return false;
    }

    return true;
}