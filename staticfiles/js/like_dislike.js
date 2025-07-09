document.addEventListener('DOMContentLoaded', function() {
    console.log('like_dislike.js loaded');

    // Функция для получения CSRF-токена из cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const likeButtons = document.querySelectorAll('.like-btn');
    const dislikeButtons = document.querySelectorAll('.dislike-btn');
    const csrfToken = getCookie('csrftoken');

    if (!csrfToken) {
        console.error('CSRF token not found in cookies');
        alert('Ошибка: CSRF-токен не найден');
        return;
    }
    console.log('CSRF token:', csrfToken);

    function updateButtonStyles(button, action, voted) {
        console.log(`Updating button: ${action}, voted: ${voted}`);
        button.classList.remove('active-vote', 'disabled');
        if (action === voted) {
            button.classList.add('active-vote', 'disabled');
        }
        button.setAttribute('data-voted', action === voted ? action : '');
    }

    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const quoteId = this.getAttribute('data-quote-id');
            const action = this.getAttribute('data-action');
            console.log(`Sending like request for quote_id: ${quoteId}`);
            fetch('/like-dislike/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `quote_id=${quoteId}&action=${action}`
            })
            .then(response => {
                console.log(`Like response status: ${response.status}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Like response data:', data);
                if (data.status === 'success') {
                    const likesSpan = document.querySelector(`#likes-count-${quoteId}`);
                    const dislikesSpan = document.querySelector(`#dislikes-count-${quoteId}`);
                    likesSpan.textContent = data.likes;
                    dislikesSpan.textContent = data.dislikes;
                    updateButtonStyles(button, 'like', data.voted_action);
                    const otherButton = document.querySelector(`.dislike-btn[data-quote-id="${quoteId}"]`);
                    updateButtonStyles(otherButton, 'dislike', data.voted_action);
                } else {
                    console.error('Like error:', data.message);
                    alert(`Ошибка: ${data.message}`);
                }
            })
            .catch(error => {
                console.error('Like fetch error:', error);
                alert('Ошибка при голосовании: ' + error.message);
            });
        });
    });

    dislikeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const quoteId = this.getAttribute('data-quote-id');
            const action = this.getAttribute('data-action');
            console.log(`Sending dislike request for quote_id: ${quoteId}`);
            fetch('/like-dislike/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `quote_id=${quoteId}&action=${action}`
            })
            .then(response => {
                console.log(`Dislike response status: ${response.status}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Dislike response data:', data);
                if (data.status === 'success') {
                    const likesSpan = document.querySelector(`#likes-count-${quoteId}`);
                    const dislikesSpan = document.querySelector(`#dislikes-count-${quoteId}`);
                    likesSpan.textContent = data.likes;
                    dislikesSpan.textContent = data.dislikes;
                    updateButtonStyles(button, 'dislike', data.voted_action);
                    const otherButton = document.querySelector(`.like-btn[data-quote-id="${quoteId}"]`);
                    updateButtonStyles(otherButton, 'like', data.voted_action);
                } else {
                    console.error('Dislike error:', data.message);
                    alert(`Ошибка: ${data.message}`);
                }
            })
            .catch(error => {
                console.error('Dislike fetch error:', error);
                alert('Ошибка при голосовании: ' + error.message);
            });
        });
    });
});