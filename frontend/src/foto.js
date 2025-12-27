const API_URL = 'http://localhost:8000';

let stream = null;
let currentImage = null;
let userLocation = null;
let userLatitude = null;
let userLongitude = null;
let userCity = null;

// Get user location on page load
window.addEventListener('DOMContentLoaded', () => {
    getUserLocation();
    setupEventListeners();
});

function setupEventListeners() {
    // Upload area click
    document.getElementById('uploadArea').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });

    // File input change
    document.getElementById('fileInput').addEventListener('change', handleFileSelect);

    // Drag and drop
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleFile(file);
        }
    });

    // Capture button
    document.getElementById('captureBtn').addEventListener('click', capturePhoto);

    // Analyze button
    document.getElementById('analyzeBtn').addEventListener('click', analyzePhoto);

    // Retake button
    document.getElementById('retakeBtn').addEventListener('click', retakePhoto);

    // Submit button
    document.getElementById('submitBtn').addEventListener('click', submitContribution);
}

function getUserLocation() {
    const locationInfo = document.getElementById('locationInfo');
    const locationText = document.getElementById('locationText');

    if ('geolocation' in navigator) {
        locationInfo.style.display = 'block';

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                // Store coordinates globally
                userLatitude = lat;
                userLongitude = lon;

                // Try to get city name from coordinates (using a free API)
                try {
                    const response = await fetch(
                        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&accept-language=pt-BR`
                    );
                    const data = await response.json();

                    const city = data.address.city || data.address.town || data.address.village;
                    const state = data.address.state;
                    const suburb = data.address.suburb || data.address.neighbourhood;

                    // Store city for geocoding
                    userCity = city;

                    if (suburb && city) {
                        userLocation = `${city} - ${suburb}`;
                    } else if (city && state) {
                        userLocation = `${city} - ${state}`;
                    } else {
                        userLocation = city || 'Localização detectada';
                    }

                    locationText.textContent = `Localização: ${userLocation}`;
                } catch (error) {
                    userLocation = 'Localização detectada';
                    userCity = 'Brasil';
                    locationText.textContent = `Localização detectada (${lat.toFixed(2)}, ${lon.toFixed(2)})`;
                }
            },
            (error) => {
                locationText.textContent = 'Localização não disponível (permissão negada)';
                console.error('Geolocation error:', error);
            }
        );
    }
}

async function geocodeStoreAddress(storeName, city) {
    try {
        const query = `${storeName}, ${city || 'Brasil'}`;
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1&accept-language=pt-BR`
        );
        const data = await response.json();

        if (data && data.length > 0) {
            return {
                latitude: parseFloat(data[0].lat),
                longitude: parseFloat(data[0].lon),
                display_name: data[0].display_name
            };
        }
        return null;
    } catch (error) {
        console.error('Erro ao geocodificar:', error);
        return null;
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    // Validate file
    if (!file.type.startsWith('image/')) {
        showError('Por favor, selecione uma imagem.');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showError('Imagem muito grande. Máximo 10MB.');
        return;
    }

    // Store file
    currentImage = file;

    // Preview image
    const reader = new FileReader();
    reader.onload = (e) => {
        const imagePreview = document.getElementById('imagePreview');
        imagePreview.src = e.target.result;
        imagePreview.classList.add('show');

        // Show analyze button
        document.getElementById('buttonGroup').style.display = 'flex';
        document.getElementById('analyzeBtn').style.display = 'block';
        document.getElementById('retakeBtn').style.display = 'block';

        // Hide upload area
        document.getElementById('uploadArea').style.display = 'none';
    };
    reader.readAsDataURL(file);
}

function retakePhoto() {
    // Reset everything
    currentImage = null;
    document.getElementById('imagePreview').classList.remove('show');
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('buttonGroup').style.display = 'none';
    document.getElementById('resultBox').classList.remove('show');
    document.getElementById('successMessage').classList.remove('show');
    document.getElementById('errorMessage').classList.remove('show');
    document.getElementById('fileInput').value = '';
}

async function analyzePhoto() {
    if (!currentImage) {
        showError('Nenhuma foto selecionada.');
        return;
    }

    // Show loading
    document.getElementById('loading').classList.add('show');
    document.getElementById('resultBox').classList.remove('show');
    document.getElementById('errorMessage').classList.remove('show');

    // Disable button
    document.getElementById('analyzeBtn').disabled = true;

    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', currentImage);

        // Send to API
        const response = await fetch(`${API_URL}/api/extrair-preco-foto`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!result.sucesso) {
            showError(result.erro || 'Não foi possível processar a imagem.');
            document.getElementById('loading').classList.remove('show');
            document.getElementById('analyzeBtn').disabled = false;
            return;
        }

        // Show results
        displayResults(result);

    } catch (error) {
        console.error('Erro:', error);
        showError('Erro ao processar imagem. Verifique se o servidor está rodando.');
    } finally {
        document.getElementById('loading').classList.remove('show');
        document.getElementById('analyzeBtn').disabled = false;
    }
}

function displayResults(result) {
    // Show result box
    document.getElementById('resultBox').classList.add('show');

    // Display price
    document.getElementById('extractedPrice').textContent = `R$ ${result.preco.toFixed(2)}`;

    // Display product if found
    if (result.produto_nome) {
        document.getElementById('productBox').style.display = 'block';
        document.getElementById('extractedProduct').textContent = result.produto_nome;
    }

    // Display brand if found
    if (result.marca) {
        document.getElementById('brandBox').style.display = 'block';
        document.getElementById('extractedBrand').textContent = result.marca;
    }

    // Store extracted data
    window.extractedData = result;

    // Scroll to results
    document.getElementById('resultBox').scrollIntoView({ behavior: 'smooth' });
}

async function submitContribution() {
    const supermercado = document.getElementById('supermercadoInput').value.trim();

    if (!supermercado) {
        showError('Por favor, informe o supermercado.');
        return;
    }

    if (!window.extractedData) {
        showError('Nenhum dado extraído. Analise a foto primeiro.');
        return;
    }

    // Show loading
    document.getElementById('loading').classList.add('show');
    document.getElementById('submitBtn').disabled = true;
    document.getElementById('submitBtn').textContent = '🔍 Buscando localização...';

    // Try to geocode store address
    let storeLocation = null;
    if (supermercado && userCity) {
        storeLocation = await geocodeStoreAddress(supermercado, userCity);
        if (storeLocation) {
            console.log('✓ Localização da loja:', storeLocation.display_name);
        }
    }

    document.getElementById('submitBtn').textContent = '⏳ Enviando...';

    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', currentImage);
        formData.append('supermercado', supermercado);

        if (userLocation) {
            formData.append('localizacao', userLocation);
        }

        // Send store coordinates (or user location as fallback)
        if (storeLocation) {
            formData.append('latitude', storeLocation.latitude);
            formData.append('longitude', storeLocation.longitude);
        } else if (userLatitude && userLongitude) {
            formData.append('latitude', userLatitude);
            formData.append('longitude', userLongitude);
        }

        const observacao = document.getElementById('observacaoInput').value.trim();
        if (observacao) {
            formData.append('observacao', observacao);
        }

        // Send to API
        const response = await fetch(`${API_URL}/api/contribuir-com-foto`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.sucesso) {
            // Show success
            document.getElementById('successMessage').classList.add('show');
            document.getElementById('resultBox').classList.remove('show');

            // Scroll to success
            document.getElementById('successMessage').scrollIntoView({ behavior: 'smooth' });

            // Reset after 3 seconds
            setTimeout(() => {
                window.location.href = '/contribuicoes.html';
            }, 2000);

        } else {
            showError(result.erro || 'Erro ao enviar contribuição.');
        }

    } catch (error) {
        console.error('Erro:', error);
        showError('Erro ao enviar contribuição. Tente novamente.');
    } finally {
        document.getElementById('loading').classList.remove('show');
        document.getElementById('submitBtn').disabled = false;
    }
}

function showError(message) {
    const errorBox = document.getElementById('errorMessage');
    errorBox.textContent = `❌ ${message}`;
    errorBox.classList.add('show');

    // Hide after 5 seconds
    setTimeout(() => {
        errorBox.classList.remove('show');
    }, 5000);
}

// Camera functions (for future use with getUserMedia)
async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' } // Use back camera on mobile
        });

        const video = document.getElementById('video');
        video.srcObject = stream;

        document.getElementById('cameraPreview').classList.add('show');
        document.getElementById('uploadArea').style.display = 'none';
        document.getElementById('buttonGroup').style.display = 'flex';
        document.getElementById('captureBtn').style.display = 'block';

    } catch (error) {
        console.error('Camera error:', error);
        showError('Não foi possível acessar a câmera.');
    }
}

function capturePhoto() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');

    // Set canvas size to video size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    context.drawImage(video, 0, 0);

    // Convert canvas to blob
    canvas.toBlob((blob) => {
        currentImage = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' });

        // Show preview
        const imagePreview = document.getElementById('imagePreview');
        imagePreview.src = canvas.toDataURL('image/jpeg');
        imagePreview.classList.add('show');

        // Hide camera, show preview
        document.getElementById('cameraPreview').classList.remove('show');
        document.getElementById('captureBtn').style.display = 'none';
        document.getElementById('analyzeBtn').style.display = 'block';
        document.getElementById('retakeBtn').style.display = 'block';

        // Stop camera
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    }, 'image/jpeg');
}
