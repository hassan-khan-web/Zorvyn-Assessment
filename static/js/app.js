const API = window.location.origin;

async function fetchData() {
    const userSelect = document.getElementById('userSelect');
    if (!userSelect) return;
    
    const email = userSelect.value;
    const headers = { 'email': email, 'Content-Type': 'application/json' };
    const typeFilter = document.getElementById('typeFilter').value;

    try {
        const summaryRes = await fetch(`${API}/dashboard/summary`, { headers });
        if (summaryRes.ok) {
            const data = await summaryRes.json();
            document.getElementById('balance').innerText = `$${data.net_balance.toLocaleString()}`;
            document.getElementById('incomeTotal').innerText = `$${data.total_income.toLocaleString()}`;
            document.getElementById('expenseTotal').innerText = `$${data.total_expenses.toLocaleString()}`;
        }

        let recUrl = `${API}/records`;
        if(typeFilter) recUrl += `?type=${typeFilter}`;
        
        const recRes = await fetch(recUrl, { headers });
        const tbody = document.querySelector('#recordsTable tbody');
        tbody.innerHTML = '';
        
        if (recRes.ok) {
            const records = await recRes.json();
            records.forEach(r => {
                const row = `<tr>
                    <td>${new Date(r.date).toLocaleDateString()}</td>
                    <td>${r.category}</td>
                    <td><span class="badge ${r.type}">${r.type}</span></td>
                    <td style="font-weight: 700;">$${r.amount.toLocaleString()}</td>
                </tr>`;
                tbody.innerHTML += row;
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; opacity: 0.5;">Unauthorized Access to detailed records.</td></tr>';
        }

        document.getElementById('adminPanel').classList.toggle('hidden', email !== 'admin@example.com');

    } catch (err) {
        console.error("Fetch Error:", err);
    }
}

async function addRecord(e) {
    e.preventDefault();
    const email = document.getElementById('userSelect').value;
    const body = {
        amount: parseFloat(document.getElementById('amount').value),
        category: document.getElementById('category').value,
        type: document.getElementById('type').value,
        description: document.getElementById('description').value,
        user_id: 1
    };

    const res = await fetch(`${API}/records`, {
        method: 'POST',
        headers: { 'email': email, 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });

    if (res.ok) {
        showToast("Record added successfully!");
        document.getElementById('recordForm').reset();
        fetchData();
    } else {
        const err = await res.json();
        alert(err.detail);
    }
}

function showToast(msg) {
    const t = document.getElementById('toast');
    t.innerText = msg;
    t.style.display = 'block';
    setTimeout(() => t.style.display = 'none', 3000);
}

function switchUser() {
    localStorage.setItem('user', document.getElementById('userSelect').value);
    fetchData();
}

document.addEventListener('DOMContentLoaded', () => {
    const userSelect = document.getElementById('userSelect');
    if (userSelect) {
        userSelect.value = localStorage.getItem('user') || 'admin@example.com';
    }
    fetchData();
});

window.fetchData = fetchData;
window.addRecord = addRecord;
window.switchUser = switchUser;
