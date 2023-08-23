
# Implementing Sorting in Flask Routes

To implement sorting functionality for tables in any Flask route, follow the steps below:

## 1. Frontend (Template) Adjustments:

### Table Headers:
For every table column you want to make sortable, adjust the table headers in your HTML:

```html
<th data-sort-column="ColumnName">Header Name</th>
```

### Link the Universal Sorting JavaScript:

Ensure the `universal_sorting.js` script is linked in the template:

```html
<script src="/static/js/universal_sorting.js"></script>
```

## 2. Backend (Route) Adjustments:

For each Flask route that serves a table you want to sort:

```python
from flask import request

@app.route('/your_route')
def your_route_function():
    
    # Extract the sorting parameters
    sort_by = request.args.get('sort-by', default='DefaultColumnName')
    direction = request.args.get('direction', default='asc')
    
    # Define a mapping between sort-by values and actual database column names
    sort_column_mapping = {
        'frontendValue1': 'DatabaseColumnName1',
        'frontendValue2': 'DatabaseColumnName2',
        # ... add more as needed
    }

    # Use the mapping to get the actual database column
    order_by_column = sort_column_mapping.get(sort_by, 'DefaultColumnName')
    
    # Adjust the SQL query to include the ORDER BY clause
    data = cursor.execute(f'SELECT * FROM TableName ORDER BY {order_by_column} {direction}').fetchall()
    
    # Render the template with the sorted data
    return render_template('your_template.html', data=data)
```

**Note**:
- Replace placeholders (`your_route`, `your_route_function`, `TableName`, etc.) with appropriate values for your application.
- Always ensure your SQL queries are safe. Using Python's formatted strings directly with SQL queries can lead to vulnerabilities. Prefer parameterized queries to prevent SQL injection.

## 3. General Considerations:

- **CSS Styling**: To make table headers appear clickable and interactive, ensure they have styles indicating interactivity (hover effects, pointer cursor, etc.).
- **Caching**: Browsers cache JS files. If you update your JS, remember to hard refresh the page or clear the browser's cache to see the changes.

By following this blueprint, you can implement sorting functionality for tables in any Flask route.
