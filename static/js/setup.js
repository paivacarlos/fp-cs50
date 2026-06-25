// Client-side interactions for Drag and Drop, image preview and character counter.
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('screenshot');
const previewContainer = document.getElementById('preview-container');
const previewImage = document.getElementById('preview-image');

const contextTextarea = document.getElementById('initial_context');
const charCounter = document.getElementById('char-counter');

// Trigger file selection on click
dropZone.addEventListener('click', () => {
    fileInput.click();
});

// Handle file selection
fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

// Drag and Drop event listeners
['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    }, false);
});

dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 1) {
        showError('Only one screenshot is allowed. Please drag a single file.');
        fileInput.value = '';
        previewContainer.style.display = 'none';
        return;
    }

    fileInput.files = files; // Assign files to file input
    handleFiles(files);
});

function handleFiles(files) {
    if (files.length > 1) {
        showError('Only one screenshot is allowed. Please drag a single file.');
        fileInput.value = '';
        previewContainer.style.display = 'none';
        return;
    }
    if (files.length > 0) {
        const file = files[0];
        if (file.type.startsWith('image/')) {
            hideError();
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewContainer.style.display = 'flex';
            };
            reader.readAsDataURL(file);
        } else {
            showError('Please upload a valid image file (PNG, JPG, JPEG, GIF).');
            fileInput.value = '';
            previewContainer.style.display = 'none';
        }
    }
}

// Character counter for initial context
contextTextarea.addEventListener('input', () => {
    const remaining = 200 - contextTextarea.value.length;
    charCounter.textContent = `${remaining} characters remaining`;
    if (remaining <= 20) {
        charCounter.style.color = '#ef4444'; // Red alert color when low
    } else {
        charCounter.style.color = ''; // Restore standard color
    }
});

// Press Room Q&A Interactive Logic
const setupForm = document.getElementById('setup-form');
const setupContainer = document.getElementById('setup-container');
const pressRoomContainer = document.getElementById('press-room-container');
const questionText = document.getElementById('question-text');
const roundBadge = document.getElementById('round-badge');

const answerForm = document.getElementById('answer-form');
const coachAnswer = document.getElementById('coach_answer');
const answerCharCounter = document.getElementById('answer-char-counter');

const cardTitle = document.querySelector('.header-section h2');
const cardTagline = document.querySelector('.header-section .tagline');
const pageBadge = document.querySelector('.header-section .badge');

let currentConferenceId = null;
let currentRoundNumber = 1;

// Character counter for coach answer
coachAnswer.addEventListener('input', () => {
    const remaining = 300 - coachAnswer.value.length;
    answerCharCounter.textContent = `${remaining} characters remaining`;
    if (remaining <= 20) {
        answerCharCounter.style.color = '#ef4444';
    } else {
        answerCharCounter.style.color = '';
    }
});

// Error Alert Box Helpers
const errorAlert = document.getElementById('error-alert');
const errorAlertText = document.getElementById('error-alert-text');

function showError(message) {
    errorAlertText.textContent = message;
    errorAlert.style.display = 'flex';
    // Scroll smoothly to make error visible
    errorAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError() {
    errorAlert.style.display = 'none';
    errorAlertText.textContent = '';
}

// Intercept form submission to start press conference via API
setupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    const submitBtn = setupForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.classList.add('btn-loading');
    submitBtn.textContent = 'Entering Press Room...';

    const formData = new FormData(setupForm);

    try {
        const response = await fetch('/api/conference/start', {
            method: 'POST',
            body: formData
        });

        if (response.status === 401) {
            window.location.href = '/login';
            return;
        }

        if (!response.ok) {
            let errorMsg = 'Failed to start conference';
            try {
                const errorData = await response.json();
                errorMsg = errorData.error || errorMsg;
            } catch (e) {
                errorMsg = `Server Error (${response.status}): ${response.statusText || 'Internal Server Error'}`;
            }
            throw new Error(errorMsg);
        }

        const data = await response.json();

        // Set session identifiers
        currentConferenceId = data.conference_id;
        currentRoundNumber = data.round_number;

        // Update UI headers
        if (cardTitle) cardTitle.textContent = 'Press Conference';
        if (cardTagline) cardTagline.textContent = 'Answer the journalists questions carefully';
        if (pageBadge) pageBadge.textContent = 'Live Q&A';

        // Load the first question
        questionText.textContent = data.question;
        roundBadge.textContent = `Round ${currentRoundNumber} of 3`;

        // Slide transition
        setupContainer.style.display = 'none';
        pressRoomContainer.style.display = 'block';

    } catch (error) {
        showError(error.message);
        submitBtn.disabled = false;
        submitBtn.classList.remove('btn-loading');
        submitBtn.textContent = 'Take the Stage';
    }
});

// Handle coach answer submission to advance rounds
answerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    const submitBtn = document.getElementById('submit-answer-btn');
    submitBtn.disabled = true;
    submitBtn.classList.add('btn-loading');
    submitBtn.textContent = 'Submitting Answer...';

    try {
        const response = await fetch('/api/conference/answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                conference_id: currentConferenceId,
                answer: coachAnswer.value
            })
        });

        if (response.status === 401) {
            window.location.href = '/login';
            return;
        }

        if (!response.ok) {
            let errorMsg = 'Failed to submit answer';
            try {
                const errorData = await response.json();
                errorMsg = errorData.error || errorMsg;
            } catch (e) {
                errorMsg = `Server Error (${response.status}): ${response.statusText || 'Internal Server Error'}`;
            }
            throw new Error(errorMsg);
        }

        const data = await response.json();

        // Check if final round is complete
        if (data.status === 'complete') {
            submitBtn.textContent = 'Generating Newspaper...';
            // Redirect to the newly generated newspaper view
            window.location.href = `/conference/${currentConferenceId}/newspaper`;
            return;
        }

        // Advance round in the UI
        currentRoundNumber = data.round_number;
        roundBadge.textContent = `Round ${currentRoundNumber} of 3`;
        questionText.textContent = data.question;

        // Clear input box
        coachAnswer.value = '';
        answerCharCounter.textContent = '300 characters remaining';
        answerCharCounter.style.color = '';

        // Re-trigger fade-in animation for question box
        const qBox = document.querySelector('.question-box');
        if (qBox) {
            qBox.style.animation = 'none';
            qBox.offsetHeight; // force reflow
            qBox.style.animation = null;
        }

        submitBtn.disabled = false;
        submitBtn.classList.remove('btn-loading');
        submitBtn.textContent = 'Submit Answer';

    } catch (error) {
        showError(error.message);
        submitBtn.disabled = false;
        submitBtn.classList.remove('btn-loading');
        submitBtn.textContent = 'Submit Answer';
    }
});
