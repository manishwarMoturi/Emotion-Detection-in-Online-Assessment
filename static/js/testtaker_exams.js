// Modal functionality
function openModal() {
    document.getElementById('createExamModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('createExamModal').style.display = 'none';
    document.getElementById('createExamForm').reset();
    document.getElementById('mcqQuestionsContainer').innerHTML = '';
    questionCount = 0;
}

window.onclick = function(event) {
    const modal = document.getElementById('createExamModal');
    if (event.target === modal) {
        closeModal();
    }
};

async function fetchExams() {
    try {
        const response = await fetch('/api/testtaker/exams', { credentials: 'include' });
        if (!response.ok) {
            if (response.status === 401) {
                alert('Authentication required. Please log in.');
                window.location.href = '/';
                return;
            } else if (response.status === 403) {
                alert('Unauthorized access.');
                return;
            } else {
                alert('Failed to fetch exams: ' + response.statusText);
                return;
            }
        }
        const data = await response.json();
        if (data.status === 'success') {
            populateExamsTable(data.exams);
        } else {
            alert('Failed to fetch exams: ' + data.message);
        }
    } catch (error) {
        alert('Error fetching exams: ' + error);
    }
}

function populateExamsTable(exams) {
    const tbody = document.querySelector('#examsTable tbody');
    tbody.innerHTML = '';
    exams.forEach(exam => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${exam._id}</td>
            <td>${exam.title}</td>
            <td>${new Date(exam.date).toLocaleDateString()}</td>
            <td>${exam.duration}</td>
            <td>${exam.registered_students || 0}/${exam.max_participants || 0}</td>
            <td><span class="status-badge status-${exam.status.toLowerCase()}">${exam.status}</span></td>
            <td>
                <a href="/testtaker/exams/${exam._id}/attempt" class="action-icon" title="Attempt Exam">▶️</a>
                <span class="action-icon" onclick="editExam('${exam._id}')">✏️</span>
                <span class="action-icon" onclick="deleteExam('${exam._id}')">🗑️</span>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

let questionCount = 0;
function addMCQQuestion() {
    questionCount++;
    const container = document.getElementById('mcqQuestionsContainer');
    const questionDiv = document.createElement('div');
    questionDiv.classList.add('form-group');
    questionDiv.id = `question-${questionCount}`;
    questionDiv.innerHTML = `
        <label>Question ID: ${questionCount}</label>
        <input type="hidden" name="questions[${questionCount}][id]" value="${questionCount}" />
        <label for="questionText${questionCount}">Question Text</label>
        <textarea id="questionText${questionCount}" name="questions[${questionCount}][text]" rows="3" required></textarea>
        <label>Options</label>
        <input type="text" name="questions[${questionCount}][options][]" placeholder="Option 1" required />
        <input type="text" name="questions[${questionCount}][options][]" placeholder="Option 2" required />
        <input type="text" name="questions[${questionCount}][options][]" placeholder="Option 3" required />
        <input type="text" name="questions[${questionCount}][options][]" placeholder="Option 4" required />
        <label for="correctOption${questionCount}">Correct Option (1-4)</label>
        <input type="number" id="correctOption${questionCount}" name="questions[${questionCount}][correct]" min="1" max="4" required />
        <label for="difficulty${questionCount}">Difficulty Level</label>
        <select id="difficulty${questionCount}" name="questions[${questionCount}][difficulty]" required>
            <option value="" disabled selected>Select difficulty</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
        </select>
        <button type="button" onclick="removeMCQQuestion(${questionCount})" class="action-btn secondary-btn" style="margin-top: 0.5rem;">Remove Question</button>
        <hr />
    `;
    container.appendChild(questionDiv);
}

function removeMCQQuestion(id) {
    const questionDiv = document.getElementById(`question-${id}`);
    if (questionDiv) {
        questionDiv.remove();
    }
}

document.getElementById('createExamForm').addEventListener('submit', createExamSubmitHandler);

function createExamSubmitHandler(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const examData = {};
    formData.forEach((value, key) => {
        if (key.startsWith('questions')) {
            const match = key.match(/questions\[(\d+)\]\[(\w+)\](\[\])?/);
            if (match) {
                const qIndex = match[1];
                const qKey = match[2];
                if (!examData.questions) examData.questions = {};
                if (!examData.questions[qIndex]) examData.questions[qIndex] = { options: [] };
                if (qKey === 'options') {
                    examData.questions[qIndex].options.push(value);
                } else {
                    examData.questions[qIndex][qKey] = value;
                }
            }
        } else {
            examData[key] = value;
        }
    });
    if (examData.questions) {
        examData.questions = Object.values(examData.questions);
    }
    fetch('/api/testtaker/exams', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(examData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Exam created successfully');
            closeModal();
            fetchExams();
        } else {
            alert('Failed to create exam: ' + data.message);
        }
    })
    .catch(error => {
        alert('Error creating exam: ' + error);
    });
}

// Placeholder functions for editExam, submitExamUpdate, deleteExam, and export button can be added similarly.

fetchExams();
