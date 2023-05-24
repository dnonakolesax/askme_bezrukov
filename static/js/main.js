function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

$(".like-q").on('click', function (ev) {
    var elId = "q-rate-" + $(this).data('id');
    var el = document.getElementById(elId);
    const request = new Request(
        'http://127.0.0.1/vote_question/', {
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },
        method: 'POST',
        body: 'question_id=' + $(this).data('id') + '&is_like=' + $(this).data('like')
    }
    );
    fetch(request).then(
        response_raw => response_raw.json().then(
            response_json => el.innerText = el.textContent = el.innerHTML = response_json.new_rating,
        ),  
    );
  
});

$(".like-a").on('click', function (ev) {
    var elId = "a-rate-" + $(this).data('id');
    var el = document.getElementById(elId);
    var urateId = "u-rate-" + $(this).data('id');
    var urateEl = document.getElementById(urateId);
    const request = new Request(
        'http://127.0.0.1/vote_answer/', {
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },
        method: 'POST',
        body: 'answer_id=' + $(this).data('id') + '&is_like=' + $(this).data('like')
    }
    );
    fetch(request).then(
        response_raw => response_raw.json().then(
            response_json => el.innerText = el.textContent = el.innerHTML = response_json.new_rating,
            response_json => urateEl.innerText = urateEl.textContent = urateEl.innerHTML = response_json.user_rating
        )
    );
});


$(".ver-a").on('click', function (ev) {
    var elId = "verif-" + $(this).data('id');
    var el = document.getElementById(elId);
    if ($(this).prop('checked')) {
        var is_right = true;
    } else {
        var is_right = false;
    }
    const request = new Request(
        'http://127.0.0.1/verify_answer/', {
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },
        method: 'POST',
        body: 'answer_id=' + $(this).data('id') + '&is_right=' + is_right
    }
    );
});

$(".like-forbidden").on('click', function (ev) {
    alert('Нельзя оценивать свои же вопросы!')
});

$(".like-aforbid").on('click', function (ev) {
    alert('Нельзя оценивать свои же ответы!')
});