document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const navItems = document.querySelectorAll('.nav-links li');
    const viewSections = document.querySelectorAll('.view-section');
    const pageTitle = document.getElementById('page-title');
    
    const btnAddTransaction = document.getElementById('btn-add-transaction');
    const modalOverlay = document.getElementById('add-modal');
    const modalTitle = document.getElementById('modal-title');
    const closeBtns = document.querySelectorAll('.close-modal');
    const addForm = document.getElementById('add-transaction-form');
    const transactionIdInput = document.getElementById('transaction-id');
    
    const summaryBalance = document.getElementById('summary-balance');
    const summaryIncome = document.getElementById('summary-income');
    const summaryExpense = document.getElementById('summary-expense');
    
    const transactionsBody = document.getElementById('transactions-body');
    const dateInput = document.getElementById('date');
    
    // Set default date to today
    dateInput.valueAsDate = new Date();

    // Chart Instances
    let pieChartInstance = null;
    let barChartInstance = null;

    // --- Navigation Logic ---
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Update active nav state
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Switch view
            const targetTab = item.getAttribute('data-tab');
            viewSections.forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById(`view-${targetTab}`).classList.add('active');
            
            // Update title
            pageTitle.textContent = targetTab.charAt(0).toUpperCase() + targetTab.slice(1);
        });
    });

    // --- Modal Logic ---
    const openModal = (isEdit = false, transactionData = null) => {
        if (isEdit && transactionData) {
            modalTitle.textContent = 'Edit Transaction';
            transactionIdInput.value = transactionData.id;
            
            // Fill form with existing data
            addForm.elements['type'].value = transactionData.type;
            addForm.elements['amount'].value = transactionData.amount;
            addForm.elements['date'].value = transactionData.date;
            addForm.elements['category'].value = transactionData.category;
            addForm.elements['description'].value = transactionData.description || '';
        } else {
            modalTitle.textContent = 'New Transaction';
            transactionIdInput.value = '';
            addForm.reset();
            dateInput.valueAsDate = new Date();
        }
        
        modalOverlay.classList.add('active');
    };

    const closeModal = () => {
        modalOverlay.classList.remove('active');
        addForm.reset();
        transactionIdInput.value = '';
        dateInput.valueAsDate = new Date(); // Reset date
    };

    btnAddTransaction.addEventListener('click', () => openModal(false));
    
    closeBtns.forEach(btn => {
        btn.addEventListener('click', closeModal);
    });

    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });

    // --- API Calls & Data Logic ---
    
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    const API_BASE_URL = 'https://finance-manger.onrender.com';

    const fetchSummary = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/summary`);
            const data = await res.json();
            
            summaryBalance.textContent = formatCurrency(data.balance);
            summaryIncome.textContent = formatCurrency(data.total_income);
            summaryExpense.textContent = formatCurrency(data.total_expense);
            
            renderCharts(data.expenses_by_category);
        } catch (error) {
            console.error('Error fetching summary:', error);
        }
    };

    const fetchTransactions = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/transactions`);
            const data = await res.json();
            
            transactionsBody.innerHTML = '';
            
            if (data.length === 0) {
                transactionsBody.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                            No transactions found. Add one to get started!
                        </td>
                    </tr>
                `;
                return;
            }
            
            data.forEach(item => {
                const tr = document.createElement('tr');
                const isIncome = item.type === 'income';
                const sign = isIncome ? '+' : '-';
                const colorClass = isIncome ? 'text-positive' : 'text-negative';
                
                tr.innerHTML = `
                    <td>${formatDate(item.date)}</td>
                    <td style="font-weight: 500">${item.description || '-'}</td>
                    <td>${item.category}</td>
                    <td><span class="type-badge badge-${item.type}">${item.type}</span></td>
                    <td class="amount-col ${colorClass}">
                        ${sign}${formatCurrency(item.amount)}
                    </td>
                    <td class="actions-col">
                        <div class="table-actions">
                            <button class="action-btn edit-btn" onclick='window.editTransaction(${JSON.stringify(item)})' title="Edit">
                                <span class="material-icons-round">edit</span>
                            </button>
                            <button class="action-btn delete-btn" onclick='window.deleteTransaction("${item.id}")' title="Delete">
                                <span class="material-icons-round">delete</span>
                            </button>
                        </div>
                    </td>
                `;
                transactionsBody.appendChild(tr);
            });
        } catch (error) {
            console.error('Error fetching transactions:', error);
        }
    };

    const renderCharts = (categoryData) => {
        const categories = Object.keys(categoryData);
        const amounts = Object.values(categoryData);
        
        const chartColors = [
            '#4f46e5', '#10b981', '#f59e0b', '#ef4444', 
            '#8b5cf6', '#ec4899', '#06b6d4', '#f97316'
        ];

        // Destroy existing charts if they exist
        if (pieChartInstance) pieChartInstance.destroy();
        if (barChartInstance) barChartInstance.destroy();

        if (categories.length === 0) return; // Don't render empty charts

        // Common options
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.color = '#6b7280';

        // Pie Chart
        const ctxPie = document.getElementById('categoryPieChart').getContext('2d');
        pieChartInstance = new Chart(ctxPie, {
            type: 'doughnut',
            data: {
                labels: categories,
                datasets: [{
                    data: amounts,
                    backgroundColor: chartColors,
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { boxWidth: 12, usePointStyle: true }
                    }
                },
                cutout: '65%'
            }
        });

        // Bar Chart
        const ctxBar = document.getElementById('categoryBarChart').getContext('2d');
        barChartInstance = new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: categories,
                datasets: [{
                    label: 'Amount ($)',
                    data: amounts,
                    backgroundColor: 'rgba(79, 70, 229, 0.8)',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { borderDash: [4, 4], color: '#e5e7eb' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    };

    // --- Form Submission ---
    addForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(addForm);
        const transactionId = formData.get('id');
        const transactionData = {
            type: formData.get('type'),
            amount: parseFloat(formData.get('amount')),
            date: formData.get('date'),
            category: formData.get('category'),
            description: formData.get('description')
        };
        
        const isEdit = !!transactionId;
        const url = isEdit ? `${API_BASE_URL}/api/transactions/${transactionId}` : `${API_BASE_URL}/api/transactions`;
        const method = isEdit ? 'PUT' : 'POST';
        
        try {
            const res = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(transactionData)
            });
            
            if (res.ok) {
                closeModal();
                // Refresh data
                fetchSummary();
                fetchTransactions();
            } else {
                const error = await res.json();
                alert(`Error: ${error.error}`);
            }
        } catch (error) {
            console.error('Error saving transaction:', error);
            alert('Failed to save transaction');
        }
    });

    // Make edit/delete functions globally accessible for inline onclick handlers
    window.editTransaction = (transactionData) => {
        openModal(true, transactionData);
    };

    window.deleteTransaction = async (id) => {
        if (!confirm('Are you sure you want to delete this transaction?')) return;
        
        try {
            const res = await fetch(`${API_BASE_URL}/api/transactions/${id}`, {
                method: 'DELETE'
            });
            
            if (res.ok) {
                fetchSummary();
                fetchTransactions();
            } else {
                const error = await res.json();
                alert(`Error: ${error.error}`);
            }
        } catch (error) {
            console.error('Error deleting transaction:', error);
            alert('Failed to delete transaction');
        }
    };

    // --- Initialize ---
    fetchSummary();
    fetchTransactions();
});
