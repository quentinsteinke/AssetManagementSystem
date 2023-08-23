
let currentSortColumn = null;
let currentSortDirection = 'asc';

// Add click listeners to all table headers with the data-sort-column attribute
document.querySelectorAll('th[data-sort-column]').forEach(header => {
    header.addEventListener('click', function() {
        if (currentSortColumn === header.getAttribute('data-sort-column')) {
            // Toggle the sort direction
            currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            currentSortDirection = 'asc';
            currentSortColumn = header.getAttribute('data-sort-column');
        }

        const currentPath = window.location.pathname;
        window.location.href = `${currentPath}?sort-by=${currentSortColumn}&direction=${currentSortDirection}`;
    });
});
