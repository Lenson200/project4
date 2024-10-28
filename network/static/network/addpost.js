document.addEventListener('DOMContentLoaded', function() {
    function edit(id) {
        var editBox = document.querySelector(`#new-post-text${id}`);
        var editBtn = document.querySelector(`#new-post-send${id}`);

        editBox.style.display = 'block';
        editBtn.style.display = 'block';

        editBtn.addEventListener('click', () => {
            fetch(`/edit/${id}`, {
                method: 'POST',
                body: JSON.stringify({
                    post: editBox.value
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                editBox.style.display = 'none';
                editBtn.style.display = 'none';
                document.querySelector(`#post-${id}`).innerHTML = editBox.value;
            })
            .catch(error => console.log('Error:', error));
        });

        editBox.value = "";
    }

    function like(id) {
        var likeBtn = document.getElementById(`like-btn-${id}`);
        var likeCount = document.getElementById(`like-count-${id}`);

        likeBtn.addEventListener('click', () => {
            var isLiked = likeBtn.getAttribute('data-is-liked') === 'true';

            fetch(`/like/${id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    like: !isLiked
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(post => {
                likeCount.innerHTML = post.likes;
                likeBtn.setAttribute('data-is-liked', !isLiked);
                likeBtn.innerHTML = !isLiked ? '<i class="fas fa-heart" style="color:red;"></i>' : '<i class="far fa-heart"></i>';
            })
            .catch(error => console.log('Error:', error));
        });
    }

    document.querySelectorAll('.edit').forEach(editButton => {
        const postId = editButton.getAttribute('data-post-id');
        edit(postId);
    });

    document.querySelectorAll('.like-btn').forEach(likeButton => {
        const postId = likeButton.getAttribute('data-post-id');
        like(postId);
    });
});
