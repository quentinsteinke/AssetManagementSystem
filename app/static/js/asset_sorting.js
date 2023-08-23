
let currentSortColumn = null;
let currentSortDirection = 'asc';

// Add click listeners to the table headers
document.querySelectorAll('thead th').forEach((header, index) => {
    if (index > 0) {  // Exclude the "Select" column
        header.addEventListener('click', function() {
            if (currentSortColumn === header.innerText) {
                // Toggle the sort direction
                currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortDirection = 'asc';
            }
            currentSortColumn = header.innerText;
            const sortParam = getSortParam(currentSortColumn);
            window.location.href = `/view_assets?sort-by=${sortParam}&direction=${currentSortDirection}`;
        });
    }
});

function getSortParam(columnName) {
    switch (columnName) {
        case 'Name':
            return 'name';
        case 'Type':
            return 'type';
        case 'Version':
            return 'version';
        case 'Last Modified Date':
            return 'date';
        case 'Responsible Team Member':
            return 'team_member';
        case 'Status':
            return 'status';
        default:
            return 'name';
    }
}
