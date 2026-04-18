/**
 * Authentication Check
 * Redirects to login if not authenticated
 */

const API_URL = 'http://localhost:8001';

function checkAuthentication() {
    const session = localStorage.getItem('session_id');

    if (!session) {
        window.location.href = '../index.html';
        return;
    }

    fetch(`${API_URL}/auth/check?session=${session}`)
        .then(response => response.json())
        .then(data => {
            if (!data.authenticated) {
                localStorage.removeItem('session_id');
                window.location.href = '../index.html';
            }
        })
        .catch(error => {
            console.error('Auth check failed:', error);
            localStorage.removeItem('session_id');
            window.location.href = '../index.html';
        });
}

// Run on page load
checkAuthentication();
