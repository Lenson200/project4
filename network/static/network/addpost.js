document.addEventListener('DOMContentLoaded', function() {
    // Function to handle post editing
    function edit(id) {
        const postContent = document.querySelector(`#post-${id}`);
        const editButton = document.querySelector(`#edit-btn-${id}`);
        const originalText = postContent.innerHTML;

        // Create textarea and buttons, initially hidden
        const editBox = document.createElement('textarea');
        editBox.classList.add('form-control', 'mb-2');
        editBox.value = originalText;
        editBox.id = `edit-box-${id}`;
        editBox.style.display = 'none';

        const saveButton = document.createElement('button');
        saveButton.classList.add('btn', 'btn-success', 'mr-2');
        saveButton.textContent = 'Save';
        saveButton.id = `save-btn-${id}`;
        saveButton.style.display = 'none';

        const cancelButton = document.createElement('button');
        cancelButton.classList.add('btn', 'btn-secondary');
        cancelButton.textContent = 'Cancel';
        cancelButton.style.display = 'none';

        // Insert the textarea and buttons into the DOM
        postContent.after(editBox, saveButton, cancelButton);

        // Event listener for "Edit" button click
        editButton.addEventListener('click', () => {
            // Show textarea and buttons, hide the edit button
            editButton.style.display = 'none';
            editBox.style.display = 'block';
            saveButton.style.display = 'inline-block';
            cancelButton.style.display = 'inline-block';
        });

        // Event listener for "Save" button click
        saveButton.addEventListener('click', () => {
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
                // Update post content and hide textarea/buttons
                postContent.innerHTML = editBox.value;
                editButton.style.display = 'block';
                editBox.style.display = 'none';
                saveButton.style.display = 'none';
                cancelButton.style.display = 'none';
            })
            .catch(error => console.log('Error:', error));
        });

        // Event listener for "Cancel" button click
        cancelButton.addEventListener('click', () => {
            postContent.innerHTML = originalText;
            editButton.style.display = 'block';
            editBox.style.display = 'none';
            saveButton.style.display = 'none';
            cancelButton.style.display = 'none';
        });
    }
    
    // Function to handle liking a post
    function like(id) {
        const likeBtn = document.getElementById(`like-btn-${id}`);
        const likeCount = document.getElementById(`like-count-${id}`);

        likeBtn.addEventListener('click', () => {
            const isLiked = likeBtn.getAttribute('data-is-liked') === 'true';

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
    function follow(username){
        const followBtn = document.getElementById(`follow-btn-${username}`);

        followBtn.addEventListener('click', () => {
            const isFollowing = followBtn.textContent.trim() === 'Unfollow';

            fetch(`/profile ${username}/follow/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    followBtn.textContent = isFollowing ? 'Follow' : 'Unfollow';
                } else {
                    console.log('Error:', data.message);
                }
            })
            .catch(error => console.log('Error:', error));
        });
    }
    // Initialize like functionality for each post
    document.querySelectorAll('.like-btn').forEach(likeButton => {
        const postId = likeButton.getAttribute('data-post-id');
        like(postId);
    });
    // Initialize like functionality for each post
    document.querySelectorAll('.follow-btn').forEach(followButton => {
        const username = followButton.getAttribute('data-username');
        follow(username);  // Ensure the correct username is passed
    });
    // Helper function to get the CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
