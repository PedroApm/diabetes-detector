// =========================================================
// Diabetes Detector – Client Logic
// =========================================================

const FUNCTION_URL = 'https://diabetes-predict-506965761765.us-east4.run.app';

// --- DOM references --------------------------------------
const form = document.getElementById('predict-form');
const btnText = document.querySelector('.btn-text');
const btnLoader = document.querySelector('.btn-loader');
const btnPredict = document.getElementById('btn-predict');
const resultDiv = document.getElementById('result');

// Field IDs in the same order the Cloud Function expects
const FIELDS = [
  'pregnancies',
  'glucose',
  'blood_pressure',
  'skin_thickness',
  'insulin',
  'bmi',
  'diabetes_pedigree',
  'age',
];

// --- Helpers ---------------------------------------------

/** Show the loading spinner inside the button. */
function setLoading(loading) {
  btnPredict.disabled = loading;
  btnText.textContent = loading ? 'Procesando…' : 'Predecir';
  btnLoader.classList.toggle('hidden', !loading);
}

/** Display the prediction result. */
function showResult(label, probability) {
  const isPositive = label === 'No diabético';
  resultDiv.className = `result ${isPositive ? 'positive' : 'negative'}`;
  resultDiv.innerHTML = `
    <div class="result-label">${label}</div>
    <div class="result-probability">Probabilidad: ${probability}%</div>
  `;
}

/** Display an error message. */
function showError(message) {
  resultDiv.className = 'result error';
  resultDiv.innerHTML = `<div class="result-label">⚠ Error</div>
    <div class="result-probability">${message}</div>`;
}

// --- Form submit -----------------------------------------
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Build payload from form fields
  const payload = {};
  for (const field of FIELDS) {
    const input = document.getElementById(field);
    payload[field] = parseFloat(input.value);
  }

  setLoading(true);
  resultDiv.classList.add('hidden');

  try {
    const response = await fetch(FUNCTION_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      showError(data.error || `Error del servidor (${response.status})`);
      return;
    }

    showResult(data.label, data.probability);
  } catch (err) {
    showError('No se pudo conectar con el servidor. Verifica la URL de la función.');
  } finally {
    setLoading(false);
  }
});
