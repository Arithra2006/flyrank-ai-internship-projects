// ---- AI Career Study Agent form handling ----

const careerForm = document.getElementById('career-form');
const loadingBox = document.getElementById('loading');
const errorBox = document.getElementById('error-box');
const resultBox = document.getElementById('result-box');
const generateBtn = document.getElementById('generate-btn');

// IMPORTANT: When your backend is deployed on Render, replace this with
// your live backend URL, e.g. "https://your-app-name.onrender.com"
// While testing locally, leave it as an empty string (same-origin).
const BACKEND_URL = "";

careerForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  errorBox.classList.add('hidden');
  resultBox.classList.add('hidden');
  loadingBox.classList.remove('hidden');
  generateBtn.disabled = true;

  const payload = {
    name: document.getElementById('name').value.trim(),
    degree: document.getElementById('degree').value.trim(),
    year: document.getElementById('year').value.trim(),
    goal: document.getElementById('goal').value.trim(),
    skills: document.getElementById('skills').value.trim(),
    questions: document.getElementById('questions').value.trim(),
  };

  try {
    const response = await fetch(`${BACKEND_URL}/career-advice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || `Request failed with status ${response.status}`);
    }

    const data = await response.json();
    resultBox.textContent = data.advice;
    resultBox.classList.remove('hidden');
  } catch (err) {
    errorBox.textContent = `Something went wrong: ${err.message}`;
    errorBox.classList.remove('hidden');
  } finally {
    loadingBox.classList.add('hidden');
    generateBtn.disabled = false;
  }
});

// ---- Contact form handling ----
// NOTE: This demo version just confirms locally. To actually receive
// messages by email, you'd need to wire this to a backend email endpoint
// (e.g. using Flask-Mail) or a third-party form service like Formspree.

const contactForm = document.getElementById('contact-form');
const contactStatus = document.getElementById('contact-status');

contactForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  const payload = {
    name: document.getElementById('c-name').value.trim(),
    email: document.getElementById('c-email').value.trim(),
    message: document.getElementById('c-message').value.trim(),
  };

  try {
    const response = await fetch(`${BACKEND_URL}/contact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error('Failed to send message');

    contactStatus.textContent = "Thanks! Your message has been received.";
    contactStatus.classList.remove('hidden');
    contactForm.reset();
  } catch (err) {
    contactStatus.textContent = `Error: ${err.message}`;
    contactStatus.classList.remove('hidden');
  }
});
