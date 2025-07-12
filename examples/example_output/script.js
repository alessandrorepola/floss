
// PyFault HTML Report JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Add interactive features
    console.log('PyFault report loaded');
    
    // Add sorting functionality to tables
    const tables = document.querySelectorAll('.ranking-table');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => sortTable(table, index));
        });
    });
});

function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aVal = a.cells[column].textContent.trim();
        const bVal = b.cells[column].textContent.trim();
        
        // Try to parse as numbers
        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return bNum - aNum; // Descending for numbers
        }
        
        return aVal.localeCompare(bVal);
    });
    
    rows.forEach(row => tbody.appendChild(row));
}
        