function toggleDropdown(assetId) {
    console.log("Toggling for asset", assetId);
    var content = document.getElementById('dropdown-' + assetId);
    if (content.style.maxHeight === '0px' || content.style.maxHeight === '') {
        content.style.maxHeight = '200px'; // or a larger value if the content might be bigger
        content.style.opacity = '1';
    } else {
        content.style.maxHeight = '0px';
        content.style.opacity = '0';
    }
}
