document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const quoteId = this.getAttribute('data-quote-id');
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
            console.log(`Initiating delete for quote_id: ${quoteId}`);

            fetch('/delete-quote/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `quote_id=${quoteId}`
            })
            .then(response => {
                console.log(`Response status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                if (data.status === 'success') {
                    const container = document.querySelector('.container');
                    if (data.new_quote) {
                        // Обновляем цитату
                        const quoteBlock = document.querySelector('blockquote');
                        const likesSpan = document.querySelector(`#likes-count-${quoteId}`);
                        const dislikesSpan = document.querySelector(`#dislikes-count-${quoteId}`);
                        const viewsSpan = document.querySelector(`#views-count-${quoteId}`);
                        const likeButton = document.querySelector(`.like-btn[data-quote-id="${quoteId}"]`);
                        const dislikeButton = document.querySelector(`.dislike-btn[data-quote-id="${quoteId}"]`);
                        const deleteButton = document.querySelector(`.delete-btn[data-quote-id="${quoteId}"]`);

                        quoteBlock.querySelector('p').textContent = data.new_quote.text;
                        quoteBlock.querySelector('.blockquote-footer').textContent = `Источник: ${data.new_quote.source}`;
                        likesSpan.textContent = data.new_quote.likes;
                        likesSpan.id = `likes-count-${data.new_quote.id}`;
                        dislikesSpan.textContent = data.new_quote.dislikes;
                        dislikesSpan.id = `dislikes-count-${data.new_quote.id}`;
                        viewsSpan.textContent = data.new_quote.views;
                        viewsSpan.id = `views-count-${data.new_quote.id}`;
                        likeButton.setAttribute('data-quote-id', data.new_quote.id);
                        likeButton.setAttribute('data-voted', data.new_quote.user_vote);
                        dislikeButton.setAttribute('data-quote-id', data.new_quote.id);
                        dislikeButton.setAttribute('data-voted', data.new_quote.user_vote);
                        deleteButton.setAttribute('data-quote-id', data.new_quote.id);

                        // Обновляем подсветку
                        likeButton.classList.remove('active-vote', 'disabled');
                        dislikeButton.classList.remove('active-vote', 'disabled');
                        if (data.new_quote.user_vote === 'like') {
                            likeButton.classList.add('active-vote', 'disabled');
                        } else if (data.new_quote.user_vote === 'dislike') {
                            dislikeButton.classList.add('active-vote', 'disabled');
                        }
                    } else {
                        // Если цитат нет, обновляем контейнер
                        container.innerHTML = `
                            <h1 class="mb-4">Цитата дня</h1>
                            <a href="/top-quotes/" class="btn btn-info mb-3">Топ-10 лучших цитат</a>
                            <a href="/worst-quotes/" class="btn btn-secondary mb-3">Топ-10 худших цитат</a>
                            <a href="/add/" class="btn btn-primary mb-3">Добавить цитату</a>
                            <p class="text-muted">Цитаты пока не добавлены.</p>
                        `;
                    }
                } else {
                    console.error('Error:', data.message);
                    alert(`Ошибка: ${data.message}`);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                alert('Ошибка при удалении цитаты. Проверьте консоль для подробностей.');
            });
        });
    });
});