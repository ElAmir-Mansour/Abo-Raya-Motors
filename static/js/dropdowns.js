/**
 * Cascading Dropdowns Logic
 * Handles Make → Model → Trim selection with AJAX
 */

document.addEventListener('DOMContentLoaded', function () {
    const makeSelect = document.getElementById('id_make');
    const modelSelect = document.getElementById('id_model');
    const trimSelect = document.getElementById('id_trim');

    if (!makeSelect || !modelSelect || !trimSelect) {
        console.log('Dropdown elements not found on this page');
        return;
    }

    // Get current language from HTML lang attribute
    const currentLang = document.documentElement.lang || 'ar';

    // 1. Load Models when Make changes
    makeSelect.addEventListener('change', function () {
        const makeId = this.value;

        // Reset dependent dropdowns
        modelSelect.innerHTML = '<option value="">Select Model</option>';
        trimSelect.innerHTML = '<option value="">Select Trim</option>';

        if (!makeId) return;

        // Show loading state
        modelSelect.innerHTML = '<option value="">Loading...</option>';

        // Fetch models for selected make
        fetch(`/${currentLang}/ajax/load-models/?make_id=${makeId}`)
            .then(response => response.json())
            .then(data => {
                modelSelect.innerHTML = '<option value="">Select Model</option>';
                data.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;
                    modelSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error loading models:', error);
                modelSelect.innerHTML = '<option value="">Error loading models</option>';
            });
    });

    // 2. Load Trims when Model changes
    modelSelect.addEventListener('change', function () {
        const modelId = this.value;

        // Reset trim dropdown
        trimSelect.innerHTML = '<option value="">Select Trim</option>';

        if (!modelId) return;

        // Show loading state
        trimSelect.innerHTML = '<option value="">Loading...</option>';

        // Fetch trims for selected model
        fetch(`/${currentLang}/ajax/load-trims/?model_id=${modelId}`)
            .then(response => response.json())
            .then(data => {
                trimSelect.innerHTML = '<option value="">Select Trim</option>';
                data.forEach(trim => {
                    const option = document.createElement('option');
                    option.value = trim.id;
                    // Display detailed info: "2024 - 1.6L Highline (Automatic)"
                    option.textContent = trim.display;
                    // Store additional data as attributes
                    option.dataset.year = trim.year;
                    option.dataset.horsepower = trim.horsepower;
                    option.dataset.fuelConsumption = trim.fuel_consumption;
                    trimSelect.appendChild(option);
                });

                // Trigger change even if it's a preselected value
                trimSelect.dispatchEvent(new Event('change'));
            })
            .catch(error => {
                console.error('Error loading trims:', error);
                trimSelect.innerHTML = '<option value="">Error loading trims</option>';
            });
    });

    // 3. Show trim details when selected (optional enhancement)
    trimSelect.addEventListener('change', function () {
        const selectedOption = this.options[this.selectedIndex];
        if (selectedOption.value) {
            const detailsDiv = document.getElementById('trim-details');
            if (detailsDiv) {
                const year = selectedOption.dataset.year;
                const hp = selectedOption.dataset.horsepower;
                const fuel = selectedOption.dataset.fuelConsumption;

                detailsDiv.innerHTML = `
                    <div class="glass-card-light p-3 mt-3">
                        <h6>Specifications:</h6>
                        <ul class="mb-0">
                            <li>Year: ${year}</li>
                            <li>Horsepower: ${hp} HP</li>
                            <li>Fuel Consumption: ${fuel} L/100km</li>
                        </ul>
                    </div>
                `;
            }
        }
    });
});
