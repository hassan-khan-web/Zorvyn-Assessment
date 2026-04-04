const API = window.location.origin;
let currentPage = 1;
let currentRecordTotal = 0;
const pageSize = 10;
let deleteRecordId = null;

async function fetchData(page = 1) {
    const userSelect = document.getElementById('userSelect');
    const email = userSelect?.value || localStorage.getItem('user') || 'admin@example.com';
    const headers = { 'email': email, 'Content-Type': 'application/json' };
    
    currentPage = page;
    const typeFilter = document.getElementById('typeFilter').value;
    const categoryFilter = document.getElementById('categoryFilter').value;
    const startDate = document.getElementById('startDateFilter').value;
    const endDate = document.getElementById('endDateFilter').value;

    try {
        const summaryRes = await fetch(`${API}/dashboard/summary`, { headers });
        if (summaryRes.ok) {
            const data = await summaryRes.json();
            document.getElementById('balance').innerText = `$${data.net_balance.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            document.getElementById('incomeTotal').innerText = `$${data.total_income.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            document.getElementById('expenseTotal').innerText = `$${data.total_expenses.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            
            if (data.category_breakdown) {
                displayCategoryBreakdown(data.category_breakdown);
            }
        }

        const trendsRes = await fetch(`${API}/dashboard/trends`, { headers });
        if (trendsRes.ok) {
            const trends = await trendsRes.json();
            displayTrends(trends);
        }

        let recUrl = `${API}/records?limit=${pageSize}&skip=${(page - 1) * pageSize}`;
        if (typeFilter) recUrl += `&type=${typeFilter}`;
        if (categoryFilter) recUrl += `&category=${encodeURIComponent(categoryFilter)}`;
        if (startDate) recUrl += `&start_date=${startDate}T00:00:00`;
        if (endDate) recUrl += `&end_date=${endDate}T23:59:59`;
        
        const recRes = await fetch(recUrl, { headers });
        const tbody = document.querySelector('#recordsTable tbody');
        tbody.innerHTML = '';
        
        if (recRes.ok) {
            const response = await recRes.json();
            const records = response.items || [];
            currentRecordTotal = response.total || 0;
            
            records.forEach(r => {
                const row = `<tr>
                    <td>${new Date(r.date).toLocaleDateString()}</td>
                    <td>${r.category}</td>
                    <td>${r.description || '-'}</td>
                    <td><span class="badge ${r.type}">${r.type}</span></td>
                    <td style="font-weight: 700;">$${r.amount.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                    <td style="text-align: center; ${email !== 'admin@example.com' ? 'display:none;' : ''}">
                        <button class="action-btn edit-btn" onclick="openEditModal(${r.id}, ${r.amount}, '${r.category}', '${r.type}', '${r.description || ''}')">Edit</button>
                        <button class="action-btn delete-btn" onclick="openDeleteModal(${r.id}, '${r.category}')">Delete</button>
                    </td>
                </tr>`;
                tbody.innerHTML += row;
            });
            
            if (records.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; opacity: 0.5;">No records found.</td></tr>';
            }

            updatePagination(page);
        } else if (recRes.status === 403) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; opacity: 0.5;">unauthorized - Analyst+ role required to view records.</td></tr>';
        }

        const adminEmail = email === 'admin@example.com';
        document.getElementById('adminPanel').classList.toggle('hidden', !adminEmail);
        document.getElementById('userManagementPanel').classList.toggle('hidden', !adminEmail);
        
        if (adminEmail) {
            fetchUsers(headers);
        }

    } catch (err) {
        console.error("Fetch Error:", err);
        showToast("Error loading data: " + err.message);
    }
}

function updatePagination(page) {
    const totalPages = Math.ceil(currentRecordTotal / pageSize);
    document.getElementById('pageInfo').innerText = `Page ${page} of ${totalPages}`;
    document.getElementById('prevBtn').disabled = page <= 1;
    document.getElementById('nextBtn').disabled = page >= totalPages;
    document.getElementById('prevBtn').style.opacity = page <= 1 ? '0.5' : '1';
    document.getElementById('nextBtn').style.opacity = page >= totalPages ? '0.5' : '1';
}

function displayCategoryBreakdown(categories) {
    const container = document.getElementById('categoryBreakdown');
    container.innerHTML = '';
    categories.forEach(cat => {
        const card = document.createElement('div');
        card.className = 'category-card';
        card.innerHTML = `
            <h4>${cat.category}</h4>
            <div class="net">$${cat.net.toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
            <div class="income-exp">
                <span class="income">+$${cat.income.toLocaleString('en-US', {minimumFractionDigits: 2})}</span> / 
                <span class="expense">-$${cat.expense.toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
            </div>
        `;
        container.appendChild(card);
    });
}

function displayTrends(trendsResponse) {
    const container = document.getElementById('trendsData');
    container.innerHTML = '';
    
    const trends = trendsResponse.monthly_trends || [];
    if (trends.length === 0) {
        container.innerHTML = '<p style="opacity: 0.5;">No trend data available.</p>';
        return;
    }
    
    trends.forEach(trend => {
        const item = document.createElement('div');
        item.className = 'trend-item';
        item.innerHTML = `
            <div>
                <h4>${trend.month}</h4>
            </div>
            <div class="values">
                <div>
                    <div class="income">+$${trend.income.toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
                    <div class="expense">-$${trend.expense.toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
                </div>
            </div>
        `;
        container.appendChild(item);
    });
}

function openEditModal(id, amount, category, type, description) {
    document.getElementById('recordId').value = id;
    document.getElementById('editAmount').value = amount;
    document.getElementById('editCategory').value = category;
    document.getElementById('editType').value = type;
    document.getElementById('editDescription').value = description;
    document.getElementById('editModal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
}

async function updateRecord(e) {
    e.preventDefault();
    const email = document.getElementById('userSelect').value;
    const recordId = document.getElementById('recordId').value;
    
    const body = {
        amount: parseFloat(document.getElementById('editAmount').value),
        category: document.getElementById('editCategory').value,
        type: document.getElementById('editType').value,
        description: document.getElementById('editDescription').value,
    };

    const res = await fetch(`${API}/records/${recordId}`, {
        method: 'PATCH',
        headers: { 'email': email, 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });

    if (res.ok) {
        showToast("Record updated successfully!");
        closeEditModal();
        fetchData(currentPage);
    } else {
        const err = await res.json();
        showToast("Error: " + (err.detail || 'Update failed'));
    }
}

function openDeleteModal(id, category) {
    deleteRecordId = id;
    document.getElementById('deleteMessage').innerText = `Delete record from "${category}"?`;
    document.getElementById('deleteModal').classList.remove('hidden');
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.add('hidden');
    deleteRecordId = null;
}

async function confirmDelete() {
    const email = document.getElementById('userSelect').value;
    
    const res = await fetch(`${API}/records/${deleteRecordId}`, {
        method: 'DELETE',
        headers: { 'email': email, 'Content-Type': 'application/json' }
    });

    if (res.ok) {
        showToast("Record deleted successfully!");
        closeDeleteModal();
        fetchData(currentPage);
    } else {
        const err = await res.json();
        showToast("Error: " + (err.detail || 'Delete failed'));
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
        fetchData(1);
    } else {
        const err = await res.json();
        showToast("Error: " + (err.detail || 'Creation failed'));
    }
}

async function fetchUsers(headers) {
    const res = await fetch(`${API}/users`, { headers });
    if (res.ok) {
        const response = await res.json();
        const users = response.items || [];
        displayUsers(users, headers);
    }
}

function displayUsers(users, headers) {
    const container = document.getElementById('usersList');
    container.innerHTML = '<h3 style="margin-bottom: 16px; opacity: 0.7;">Existing Users</h3>';
    users.forEach(user => {
        const userDiv = document.createElement('div');
        userDiv.style.cssText = 'background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;';
        userDiv.innerHTML = `
            <div>
                <div style="font-weight: 600;">${user.email}</div>
                <div style="font-size: 0.8rem; opacity: 0.6;">${user.role.toUpperCase()} ${user.is_active ? '' : '(Inactive)'}</div>
            </div>
            <button class="action-btn delete-btn" onclick="deleteUser(${user.id})" style="margin: 0;">Delete</button>
        `;
        container.appendChild(userDiv);
    });
}

async function addUser(e) {
    e.preventDefault();
    const email = document.getElementById('userSelect').value;
    const body = {
        email: document.getElementById('userEmail').value,
        role: document.getElementById('userRole').value,
        is_active: true
    };

    const res = await fetch(`${API}/users`, {
        method: 'POST',
        headers: { 'email': email, 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });

    if (res.ok) {
        showToast("User created successfully!");
        document.getElementById('userForm').reset();
        fetchData(1);
    } else {
        const err = await res.json();
        showToast("Error: " + (err.detail || 'User creation failed'));
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    const email = document.getElementById('userSelect').value;
    const res = await fetch(`${API}/users/${userId}`, {
        method: 'DELETE',
        headers: { 'email': email, 'Content-Type': 'application/json' }
    });

    if (res.ok) {
        showToast("User deleted successfully!");
        fetchData(1);
    } else {
        const err = await res.json();
        showToast("Error: " + (err.detail || 'Delete failed'));
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
    fetchData(1);
}

document.addEventListener('DOMContentLoaded', () => {
    const userSelect = document.getElementById('userSelect');
    if (userSelect) {
        userSelect.value = localStorage.getItem('user') || 'admin@example.com';
    }
    fetchData(1);
});
