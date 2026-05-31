// Rotating quotes on login page
const quotes = [
    "Stay organized. Stay focused. Stay productive.",
    "Turn ideas into action. One task at a time.",
    "Master your day, one checkbox at a time.",
    "Organize your thoughts. Execute your dreams.",
    "Success is the sum of small efforts repeated day in and day out."
];

let quoteIndex = 0;
const quoteElement = document.getElementById('rotating-quote');

if (quoteElement) {
    setInterval(() => {
        quoteIndex = (quoteIndex + 1) % quotes.length;
        quoteElement.textContent = quotes[quoteIndex];
    }, 4000); // Change quote every 4 seconds
}

// Toggle password visibility
document.querySelectorAll('.toggle-pw').forEach(btn => {
    btn.addEventListener('click', () => {
        const targetId = btn.dataset.target;
        const input = document.getElementById(targetId);
        if (!input) return;
        input.type = input.type === 'password' ? 'text' : 'password';
        btn.style.opacity = input.type === 'text' ? '1' : '0.5';
    });
});

// Password strength indicator
const pwInput = document.getElementById('password');
const strengthFill = document.getElementById('strengthFill');

if (pwInput && strengthFill) {
    pwInput.addEventListener('input', () => {
        const val = pwInput.value;
        let score = 0;
        if (val.length >= 6) score++;
        if (val.length >= 10) score++;
        if (/[A-Z]/.test(val)) score++;
        if (/[0-9]/.test(val)) score++;
        if (/[^A-Za-z0-9]/.test(val)) score++;

        const pct = (score / 5) * 100;
        strengthFill.style.width = pct + '%';

        const colors = ['#ff4d4d', '#ff4d4d', '#f5a623', '#c8fb4b', '#4caf7d', '#4caf7d'];
        strengthFill.style.background = colors[score] || '#c8fb4b';
    });
}

// Auto-dismiss flash messages after 4 seconds
document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
        el.style.transition = 'opacity 0.4s';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 400);
    }, 4000);
});

// Custom validation error display
function showValidationError(message) {
    // Remove any existing validation error
    const existing = document.getElementById('validationError');
    if (existing) existing.remove();
    
    // Create styled error message matching app theme
    const errorDiv = document.createElement('div');
    errorDiv.id = 'validationError';
    errorDiv.className = 'validation-error';
    errorDiv.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span>${message}</span>
    `;
    
    // Insert after the form
    const form = document.querySelector('.add-task-form');
    form.parentNode.insertBefore(errorDiv, form.nextSibling);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        errorDiv.style.transition = 'opacity 0.3s';
        errorDiv.style.opacity = '0';
        setTimeout(() => errorDiv.remove(), 300);
    }, 4000);
}

// Custom confirmation modal for add todo form
const confirmModal = document.getElementById('confirmModal');
const addTodoForm = document.querySelector('.add-task-form');
let formToSubmit = null;

if (addTodoForm && confirmModal) {
    addTodoForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Custom validation - Check if task title is empty
        const titleInput = document.getElementById('taskTitle');
        const titleValue = titleInput.value.trim();
        
        if (!titleValue) {
            // Show custom validation error
            showValidationError('Task title is required');
            return;
        }
        
        formToSubmit = addTodoForm;
        confirmModal.classList.add('active');
    });

    // Modal button handlers
    confirmModal.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            if (action === 'confirm' && formToSubmit) {
                formToSubmit.submit();
            } else {
                confirmModal.classList.remove('active');
                formToSubmit = null;
            }
        });
    });

    // Close modal on backdrop click
    confirmModal.addEventListener('click', (e) => {
        if (e.target === confirmModal) {
            confirmModal.classList.remove('active');
            formToSubmit = null;
        }
    });

    // Handle escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && confirmModal.classList.contains('active')) {
            confirmModal.classList.remove('active');
            formToSubmit = null;
        }
    });
}
