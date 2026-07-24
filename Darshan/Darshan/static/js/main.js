/**
 * Main Application Script & Global Handlers
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Handle Quiz Generator Form Submission (AJAX with Loading Spinner)
    const generateForm = document.getElementById('generate-quiz-form');
    if (generateForm) {
        generateForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const topicInput = document.getElementById('topic-input');
            const numQuestionsSelect = document.getElementById('num-questions-select');
            const difficultySelect = document.getElementById('difficulty-select');
            const submitBtn = document.getElementById('btn-generate');
            const alertBox = document.getElementById('form-alert-box');

            const topic = topicInput ? topicInput.value.strip ? topicInput.value.strip() : topicInput.value.trim() : '';
            const numQuestions = numQuestionsSelect ? parseInt(numQuestionsSelect.value) : 20;
            const difficulty = difficultySelect ? difficultySelect.value : 'Medium';

            // Client-side Validation
            if (!topic) {
                showAlert(alertBox, 'Please enter a valid quiz topic.', 'danger');
                return;
            }
            if (isNaN(numQuestions) || numQuestions < 5 || numQuestions > 50) {
                showAlert(alertBox, 'Number of questions must be between 5 and 50.', 'warning');
                return;
            }

            // Show Loading State
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>AI is crafting your quiz...';
            if (alertBox) alertBox.classList.add('d-none');

            try {
                const response = await fetch('/generate-quiz', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        topic: topic,
                        num_questions: numQuestions,
                        difficulty: difficulty
                    })
                });

                const data = await response.json();
                if (data.success && data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    showAlert(alertBox, data.error || 'Failed to generate quiz.', 'danger');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-magic me-2"></i>Generate Quiz';
                }
            } catch (err) {
                console.error('Quiz Generation Error:', err);
                showAlert(alertBox, 'A network error occurred. Please try again.', 'danger');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-magic me-2"></i>Generate Quiz';
            }
        });
    }

    // 2. Share Score Button (Web Share API fallback to Copy Link)
    const btnShareScore = document.getElementById('btn-share-score');
    if (btnShareScore) {
        btnShareScore.addEventListener('click', () => {
            const scoreText = btnShareScore.getAttribute('data-score-text') || 'I scored on AI Quiz Generator!';
            if (navigator.share) {
                navigator.share({
                    title: 'AI Quiz Score',
                    text: scoreText,
                    url: window.location.href
                }).catch(() => {});
            } else {
                navigator.clipboard.writeText(window.location.href + '\n' + scoreText).then(() => {
                    alert('Score link copied to clipboard!');
                }).catch(() => {
                    alert('Copy link: ' + window.location.href);
                });
            }
        });
    }

    // 3. Print / PDF Export Button
    const btnPrintPdf = document.getElementById('btn-print-pdf');
    if (btnPrintPdf) {
        btnPrintPdf.addEventListener('click', () => {
            window.print();
        });
    }
});

function showAlert(alertContainer, message, type = 'danger') {
    if (!alertContainer) return;
    alertContainer.className = `alert alert-${type} shadow-sm border-0 fade show mt-3`;
    alertContainer.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-2"></i>${message}`;
    alertContainer.classList.remove('d-none');
}
