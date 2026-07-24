/**
 * Interactive Quiz Engine Controller
 * Features 30s per-question timer, auto-save, question jump modal, progress bar, audio alerts, and full-screen mode.
 */

class QuizEngine {
    constructor(quizData, options = {}) {
        this.quizId = quizData.id;
        this.topic = quizData.topic;
        this.questions = quizData.questions || [];
        this.totalQuestions = this.questions.length;
        this.currentIndex = 0;

        // Config & Timer settings
        this.timerSecondsPerQuestion = options.timerSeconds || 30;
        this.timeRemaining = this.timerSecondsPerQuestion;
        this.timerInterval = null;

        // Local Storage State Key
        this.storageKey = `ai_quiz_state_${this.quizId}`;
        this.userAnswers = this.loadSavedAnswers();

        // Shuffling
        this.randomizeQuestions = options.randomizeQuestions || false;
        this.randomizeOptions = options.randomizeOptions || false;

        if (this.randomizeQuestions) {
            this.shuffleArray(this.questions);
        }

        this.initDOM();
        this.bindEvents();
        this.loadQuestion(this.currentIndex);
        this.startTimer();
    }

    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }

    loadSavedAnswers() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            return saved ? JSON.parse(saved) : {};
        } catch (e) {
            return {};
        }
    }

    saveAnswer(qId, selectedOption) {
        this.userAnswers[qId] = selectedOption;
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.userAnswers));
        } catch (e) {}
    }

    clearSavedState() {
        try {
            localStorage.removeItem(this.storageKey);
        } catch (e) {}
    }

    initDOM() {
        this.elements = {
            questionNumber: document.getElementById('q-number'),
            totalQuestions: document.getElementById('q-total'),
            questionText: document.getElementById('q-text'),
            optionsContainer: document.getElementById('q-options-container'),
            timerDisplay: document.getElementById('timer-count'),
            timerWidget: document.getElementById('timer-widget'),
            progressBar: document.getElementById('quiz-progress-bar'),
            btnPrev: document.getElementById('btn-prev-q'),
            btnNext: document.getElementById('btn-next-q'),
            btnSubmit: document.getElementById('btn-submit-quiz'),
            btnFullscreen: document.getElementById('btn-fullscreen'),
            soundToggleBtn: document.getElementById('btn-sound-toggle'),
            jumpModalGrid: document.getElementById('jump-modal-grid')
        };

        if (this.elements.totalQuestions) {
            this.elements.totalQuestions.textContent = this.totalQuestions;
        }

        // Render Jump Modal Grid
        this.renderJumpGrid();
    }

    bindEvents() {
        if (this.elements.btnPrev) {
            this.elements.btnPrev.addEventListener('click', () => this.navigate(-1));
        }
        if (this.elements.btnNext) {
            this.elements.btnNext.addEventListener('click', () => this.navigate(1));
        }
        if (this.elements.btnSubmit) {
            this.elements.btnSubmit.addEventListener('click', () => this.confirmAndSubmit());
        }
        if (this.elements.btnFullscreen) {
            this.elements.btnFullscreen.addEventListener('click', () => this.toggleFullscreen());
        }
        if (this.elements.soundToggleBtn) {
            this.elements.soundToggleBtn.addEventListener('click', () => {
                const muted = SoundFx.toggleMute();
                this.elements.soundToggleBtn.innerHTML = muted 
                    ? '<i class="bi bi-volume-mute-fill fs-5 text-muted"></i>' 
                    : '<i class="bi bi-volume-up-fill fs-5 text-primary"></i>';
            });
        }
    }

    loadQuestion(index) {
        if (index < 0 || index >= this.totalQuestions) return;

        this.currentIndex = index;
        const q = this.questions[index];

        // Reset timer for every new question
        this.resetTimer();

        // Update Question text & counter
        if (this.elements.questionNumber) {
            this.elements.questionNumber.textContent = index + 1;
        }
        if (this.elements.questionText) {
            this.elements.questionText.textContent = q.question;
        }

        // Render Options
        if (this.elements.optionsContainer) {
            this.elements.optionsContainer.innerHTML = '';
            
            let optionsToDisplay = [...q.options];
            if (this.randomizeOptions) {
                this.shuffleArray(optionsToDisplay);
            }

            const prefixes = ['A', 'B', 'C', 'D'];
            optionsToDisplay.forEach((optionText, idx) => {
                const prefix = prefixes[idx] || (idx + 1);
                const isSelected = (this.userAnswers[q.id] === optionText);

                const card = document.createElement('div');
                card.className = `option-card ${isSelected ? 'selected' : ''}`;
                card.setAttribute('data-option', optionText);

                card.innerHTML = `
                    <div class="option-badge">${prefix}</div>
                    <div class="option-text flex-grow-1 font-weight-500">${this.escapeHtml(optionText)}</div>
                    ${isSelected ? '<i class="bi bi-check-circle-fill text-primary fs-5"></i>' : ''}
                `;

                card.addEventListener('click', () => {
                    SoundFx.playSelect();
                    this.selectOption(q.id, optionText, card);
                });

                this.elements.optionsContainer.appendChild(card);
            });
        }

        // Update Navigation Controls & Progress
        this.updateProgress();
        this.updateJumpGridActiveState();
    }

    selectOption(qId, optionText, cardElement) {
        // Toggle or set answer
        this.saveAnswer(qId, optionText);

        // Update UI styling
        const allCards = this.elements.optionsContainer.querySelectorAll('.option-card');
        allCards.forEach(c => {
            c.classList.remove('selected');
            const icon = c.querySelector('.bi-check-circle-fill');
            if (icon) icon.remove();
        });

        cardElement.classList.add('selected');
        cardElement.insertAdjacentHTML('beforeend', '<i class="bi bi-check-circle-fill text-primary fs-5"></i>');

        this.renderJumpGrid();
    }

    navigate(direction) {
        const targetIndex = this.currentIndex + direction;
        if (targetIndex >= 0 && targetIndex < this.totalQuestions) {
            this.loadQuestion(targetIndex);
        }
    }

    startTimer() {
        this.stopTimer();
        this.timerInterval = setInterval(() => {
            this.timeRemaining--;

            if (this.elements.timerDisplay) {
                this.elements.timerDisplay.textContent = this.timeRemaining;
            }

            // Audio ticks & warnings
            if (this.timeRemaining <= 5 && this.timeRemaining > 0) {
                if (this.elements.timerWidget) {
                    this.elements.timerWidget.classList.add('warning');
                }
                SoundFx.playTimerWarning();
            } else {
                if (this.elements.timerWidget) {
                    this.elements.timerWidget.classList.remove('warning');
                }
            }

            // Time expired auto-advance requirement
            if (this.timeRemaining <= 0) {
                this.handleTimeExpired();
            }
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    resetTimer() {
        this.stopTimer();
        this.timeRemaining = this.timerSecondsPerQuestion;
        if (this.elements.timerDisplay) {
            this.elements.timerDisplay.textContent = this.timeRemaining;
        }
        if (this.elements.timerWidget) {
            this.elements.timerWidget.classList.remove('warning');
        }
        this.startTimer();
    }

    handleTimeExpired() {
        SoundFx.playTimerWarning();

        // If not on last question, automatically move to next question
        if (this.currentIndex < this.totalQuestions - 1) {
            this.navigate(1);
        } else {
            // Reached end, automatically submit quiz
            this.submitQuiz();
        }
    }

    updateProgress() {
        const percent = ((this.currentIndex + 1) / this.totalQuestions) * 100;
        if (this.elements.progressBar) {
            this.elements.progressBar.style.width = `${percent}%`;
        }

        // Update Prev / Next / Submit button visibility
        if (this.elements.btnPrev) {
            this.elements.btnPrev.disabled = (this.currentIndex === 0);
        }
        if (this.elements.btnNext) {
            if (this.currentIndex === this.totalQuestions - 1) {
                this.elements.btnNext.classList.add('d-none');
                if (this.elements.btnSubmit) this.elements.btnSubmit.classList.remove('d-none');
            } else {
                this.elements.btnNext.classList.remove('d-none');
                if (this.elements.btnSubmit) this.elements.btnSubmit.classList.add('d-none');
            }
        }
    }

    renderJumpGrid() {
        if (!this.elements.jumpModalGrid) return;
        this.elements.jumpModalGrid.innerHTML = '';

        this.questions.forEach((q, idx) => {
            const isAnswered = Boolean(this.userAnswers[q.id]);
            const isCurrent = (idx === this.currentIndex);

            const btn = document.createElement('button');
            btn.className = `btn btn-sm m-1 ${isCurrent ? 'btn-primary' : isAnswered ? 'btn-success' : 'btn-outline-secondary'}`;
            btn.style.width = '42px';
            btn.style.height = '42px';
            btn.textContent = idx + 1;

            btn.addEventListener('click', () => {
                this.loadQuestion(idx);
                // Close modal if using Bootstrap modal
                const modalEl = document.getElementById('jumpQuestionsModal');
                if (modalEl && window.bootstrap) {
                    const modal = window.bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }
            });

            this.elements.jumpModalGrid.appendChild(btn);
        });
    }

    updateJumpGridActiveState() {
        this.renderJumpGrid();
    }

    confirmAndSubmit() {
        const answeredCount = Object.keys(this.userAnswers).length;
        const unanswered = this.totalQuestions - answeredCount;

        let confirmMsg = 'Are you ready to submit your quiz answers?';
        if (unanswered > 0) {
            confirmMsg = `You have ${unanswered} unanswered question(s). Are you sure you want to submit now?`;
        }

        if (confirm(confirmMsg)) {
            this.submitQuiz();
        }
    }

    async submitQuiz() {
        this.stopTimer();

        // UI loading state
        if (this.elements.btnSubmit) {
            this.elements.btnSubmit.disabled = true;
            this.elements.btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';
        }

        try {
            const response = await fetch('/submit-quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    quiz_id: this.quizId,
                    answers: this.userAnswers
                })
            });

            const result = await response.json();
            if (result.success && result.redirect_url) {
                this.clearSavedState();
                SoundFx.playSuccess();
                window.location.href = result.redirect_url;
            } else {
                alert(result.error || 'Submission failed. Please try again.');
                if (this.elements.btnSubmit) {
                    this.elements.btnSubmit.disabled = false;
                    this.elements.btnSubmit.innerHTML = 'Submit Quiz';
                }
            }
        } catch (e) {
            console.error('Submit Quiz Error:', e);
            alert('Network error submitting quiz. Please check connection and try again.');
            if (this.elements.btnSubmit) {
                this.elements.btnSubmit.disabled = false;
                this.elements.btnSubmit.innerHTML = 'Submit Quiz';
            }
        }
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.log('Error attempting to enable full-screen mode:', err);
            });
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }

    escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}
