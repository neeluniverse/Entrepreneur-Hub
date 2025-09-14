// Like functionality
document.querySelectorAll('.like-btn').forEach(button => {
    button.addEventListener('click', function() {
        const postId = this.dataset.postId;
        fetch(`/like_post/${postId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                const likeText = this.querySelector('.like-text');
                const likeCount = this.querySelector('.like-count');
                likeText.textContent = data.liked ? 'Unlike' : 'Like';
                likeCount.textContent = data.likes_count;
            });
    });
});

// Comment functionality
document.querySelectorAll('.comment-btn').forEach(button => {
    button.addEventListener('click', function() {
        const postId = this.dataset.postId;
        const textarea = document.querySelector(`.comment-input[data-post-id="${postId}"]`);
        const content = textarea.value.trim();
        
        if (content) {
            fetch(`/comment_post/${postId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: content })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    const commentsDiv = this.closest('.collapse').querySelector('.comments');
                    const newComment = document.createElement('div');
                    newComment.className = 'd-flex mb-2';
                    newComment.innerHTML = `
                        <img src="${currentUserAvatar}" class="rounded-circle me-2" width="30" height="30">
                        <div class="bg-light p-2 rounded">
                            <strong>${currentUserName}</strong>
                            <p class="mb-0">${data.comment.content}</p>
                            <small class="text-muted">${data.comment.created_at}</small>
                        </div>
                    `;
                    commentsDiv.appendChild(newComment);
                    textarea.value = '';
                }
            });
        }
    });
});
