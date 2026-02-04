// scripts/createArticle.js

$(document).ready(function () {
  lucide.createIcons(); // Initialize Lucide icons

  // Get firm_id from URL
  const urlParams = new URLSearchParams(window.location.search);
  const firm_id = urlParams.get('firm_id');

  // Initialize Quill editor
  const quill = new Quill('#editor-container', {
    theme: 'snow',
    placeholder: 'Write your article here...',
    modules: {
      toolbar: [
        [{ header: [1, 2, 3, false] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ list: 'ordered' }, { list: 'bullet' }],
        ['blockquote', 'code-block'],
        ['link', 'image', 'video'],
        [{ align: [] }],
        ['clean']
      ]
    }
  });

  // Custom image upload
  function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    const token = getAccessToken(); // from auth.js
    return $.ajax({
      url: 'http://127.0.0.1:5000/api/article/media/upload',
      type: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      data: formData,
      processData: false,
      contentType: false
    });
  }

  function uploadVideo(file) {
    const formData = new FormData();
    formData.append('file', file);

    const token = getAccessToken();
    return $.ajax({
      url: 'http://127.0.0.1:5000/api/article/media/upload', // same endpoint, make sure backend accepts video
      type: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      data: formData,
      processData: false,
      contentType: false
    });
  }



  quill.getModule('toolbar').addHandler('image', function () {
    const input = document.createElement('input');
    input.setAttribute('type', 'file');
    input.setAttribute('accept', 'image/*');
    input.click();

    input.onchange = async function () {
      const file = input.files[0];
      if (!file) return;

      try {
        const res = await uploadImage(file);
        if (res.status === 1 && res.data.location) {
          const range = quill.getSelection();
          quill.insertEmbed(range.index, 'image', res.data.location);
        } else {
          Swal.fire('Error', 'Image upload failed', 'error');
        }
      } catch (err) {
        Swal.fire('Error', 'Image upload failed', 'error');
        console.error(err);
      }
    };
  });


  quill.getModule('toolbar').addHandler('video', function () {
    const input = document.createElement('input');
    input.setAttribute('type', 'file');
    input.setAttribute('accept', 'video/mp4,video/webm'); // allow mp4 and webm
    input.click();

    input.onchange = async function () {
      const file = input.files[0];
      if (!file) return;

      try {
        const res = await uploadVideo(file); // new function
        if (res.status === 1 && res.data.location) {
          const range = quill.getSelection();
          quill.insertEmbed(range.index, 'video', res.data.location);
        } else {
          Swal.fire('Error', 'Video upload failed', 'error');
        }
      } catch (err) {
        Swal.fire('Error', 'Video upload failed', 'error');
        console.error(err);
      }
    };
  });


  // Submit Article
  async function submitArticle(status) {
    const title = $('#title').val().trim();
    const category = $('#category').val().split(',').map(c => c.trim()).filter(Boolean);
    const tags = $('#tags').val().split(',').map(t => t.trim()).filter(Boolean);
    const hot_topic = $('#hot_topic').is(':checked');
    const content = quill.root.innerHTML;

    if (!title || !content || content === '<p><br></p>') {
      Swal.fire('Error', 'Title and Content are required!', 'error');
      return;
    }

    try {
      const token = getAccessToken();
      if (!token) {
        redirectToLogin();
        return;
      }

      const response = await $.ajax({
        url: `http://127.0.0.1:5000/api/article/create?firm_id=${firm_id}`,
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        contentType: 'application/json',
        data: JSON.stringify({
          title,
          status,
          content,
          category,
          tags,
          hot_topic
        })
      });

      Swal.fire(
        'Success',
        response.message || `Article ${status === 'DRAFT' ? 'saved as draft' : 'published'}!`,
        'success'
      ).then(() => window.location.href = 'home.html');

    } catch (err) {
      Swal.fire('Error', 'Failed to submit article', 'error');
      console.error(err);
    }
  }

  // Button handlers
  $('#saveDraft').click(() => submitArticle('DRAFT'));
  $('#publish').click(() => submitArticle('PUBLISHED'));
});
