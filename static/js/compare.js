document.addEventListener('DOMContentLoaded', function () {
    const compareBar = document.getElementById('compare-bar');
    const compareCount = document.getElementById('compare-count');
    const compareBtn = document.getElementById('compare-btn');
    const MAX_CARS = 3;

    function updateCompareUI() {
        const storedIds = JSON.parse(localStorage.getItem('compareIds') || '[]');

        // Update checkbuttons on the page
        document.querySelectorAll('.compare-checkbox').forEach(cb => {
            cb.checked = storedIds.includes(cb.dataset.id);
        });

        // Update floating bar
        if (storedIds.length > 0) {
            compareBar.classList.remove('d-none');
            compareCount.textContent = storedIds.length;
        } else {
            compareBar.classList.add('d-none');
        }
    }

    function toggleCompare(id) {
        let storedIds = JSON.parse(localStorage.getItem('compareIds') || '[]');

        if (storedIds.includes(id)) {
            storedIds = storedIds.filter(itemId => itemId !== id);
        } else {
            if (storedIds.length >= MAX_CARS) {
                alert(`You can only compare up to ${MAX_CARS} cars.`);
                return;
            }
            storedIds.push(id);
        }

        localStorage.setItem('compareIds', JSON.stringify(storedIds));
        updateCompareUI();
    }

    // Event Delegation for "Add to Compare" checkboxes/buttons
    document.body.addEventListener('change', function (e) {
        if (e.target.classList.contains('compare-checkbox')) {
            toggleCompare(e.target.dataset.id);
        }
    });

    // Handle "Compare" button click
    if (compareBtn) {
        compareBtn.addEventListener('click', function () {
            const storedIds = JSON.parse(localStorage.getItem('compareIds') || '[]');
            if (storedIds.length < 2) {
                alert('Please select at least 2 cars to compare.');
                return;
            }
            window.location.href = `/compare/?ids=${storedIds.join(',')}`;
        });
    }

    // Initialize
    updateCompareUI();
});
