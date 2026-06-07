function editTransaction(id, date, description, amount) {
    document.getElementById('tx-date').value = date;
    document.getElementById('tx-description').value = description;
    document.getElementById('tx-amount').value = amount;
    
    let form = document.getElementById('tx-date').closest('form');
    let idInput = form.querySelector('input[name="tx_id"]');
    if (!idInput) {
        idInput = document.createElement('input');
        idInput.type = 'hidden';
        idInput.name = 'tx_id';
        form.appendChild(idInput);
    }
    idInput.value = id;
    
    let btn = form.querySelector('button[type="submit"]');
    btn.innerHTML = '💾 עדכון';
    btn.classList.add('btn-warning');
    btn.classList.remove('btn-primary');
    
    window.scrollTo({ top: form.offsetTop - 50, behavior: 'smooth' });
}

function editRecurring(id, day, description, amount) {
    document.getElementById('rec-day').value = day;
    document.getElementById('rec-description').value = description;
    document.getElementById('rec-amount').value = amount;
    
    let form = document.getElementById('rec-day').closest('form');
    let idInput = form.querySelector('input[name="rec_id"]');
    if (!idInput) {
        idInput = document.createElement('input');
        idInput.type = 'hidden';
        idInput.name = 'rec_id';
        form.appendChild(idInput);
    }
    idInput.value = id;
    
    let btn = form.querySelector('button[type="submit"]');
    btn.innerHTML = '💾 עדכון';
    btn.classList.add('btn-warning');
    btn.classList.remove('btn-primary');
    
    window.scrollTo({ top: form.offsetTop - 50, behavior: 'smooth' });
}
