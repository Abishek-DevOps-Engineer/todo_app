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

// Custom confirmation modal for add todo form
const confirmModal = document.getElementById('confirmModal');
const addTodoForm = document.querySelector('.add-task-form');
let formToSubmit = null;

if (addTodoForm && confirmModal) {
    addTodoForm.addEventListener('submit', (e) => {
        e.preventDefault();
        formToSubmit = addTodoForm;
        confirmModal.classList.add('active');
    });

    // Modal button handlers
    confirmModal.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            if (action === 'confirm' && formToSubmit) {
                formToSubmit.removeEventListener('submit', handleFormSubmit);
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
