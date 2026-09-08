let token = '';
let currentWorkspaceId = null;
let currentBoardId = null;

async function login() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);

  try {
    const res = await fetch('/auth/login', { method: 'POST', body: formData });
    const data = await res.json();

    if (res.ok) {
      token = data.access_token;
      document.getElementById('auth-section').classList.add('hidden');
      document.getElementById('app-dashboard').classList.remove('hidden');
      document.getElementById('user-badge').innerText = `Active: ${email}`;
      document.getElementById('user-badge').style.color = '#3fb950';

      await loadWorkspaces();
    } else {
      document.getElementById('status').innerText = 'Authentication failed.';
    }
  } catch (err) {
    document.getElementById('status').innerText = 'Server error.';
  }
}

async function loadWorkspaces() {
  const res = await fetch('/workspaces/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const workspaces = await res.json();

  const select = document.getElementById('workspace-select');
  select.innerHTML = '<option value="">-- Select Workspace --</option>';

  workspaces.forEach(ws => {
    select.innerHTML += `<option value="${ws.id}">${ws.title}</option>`;
  });

  if (workspaces.length > 0) {
    select.value = workspaces[0].id;
    onWorkspaceChange();
  }
}

async function createWorkspace() {
  const title = prompt('Enter Workspace Title:');
  if (!title) return;

  const res = await fetch('/workspaces/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ title: title, description: 'Created via Web UI' })
  });

  if (res.ok) {
    await loadWorkspaces();
  } else {
    alert('Failed to create workspace.');
  }
}

async function onWorkspaceChange() {
  const wsId = document.getElementById('workspace-select').value;
  if (!wsId) return;
  currentWorkspaceId = wsId;

  const res = await fetch('/workspaces/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const workspaces = await res.json();
  const activeWs = workspaces.find(w => w.id == wsId);

  const boardSelect = document.getElementById('board-select');
  boardSelect.innerHTML = '<option value="">-- Select Board --</option>';

  if (activeWs && activeWs.boards && activeWs.boards.length > 0) {
    activeWs.boards.forEach(b => {
      boardSelect.innerHTML += `<option value="${b.id}">${b.title}</option>`;
    });
    boardSelect.value = activeWs.boards[0].id;
    currentBoardId = activeWs.boards[0].id;
    renderBoardTasks(activeWs.boards[0].tasks || []);
  } else {
    clearColumns();
  }
}

async function createBoard() {
  if (!currentWorkspaceId) {
    alert('Please select or create a Workspace first.');
    return;
  }
  const title = prompt('Enter Board Title:');
  if (!title) return;

  const res = await fetch('/boards/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ title: title, workspace_id: parseInt(currentWorkspaceId) })
  });

  if (res.ok) {
    await onWorkspaceChange();
  } else {
    alert('Failed to create board.');
  }
}

async function createNewTask() {
  const title = document.getElementById('new-task-title').value;
  const priority = document.getElementById('new-task-priority').value;
  const boardSelect = document.getElementById('board-select');

  if (!title || !boardSelect.value) {
    alert('Please fill task title and select a Board.');
    return;
  }

  const res = await fetch('/tasks/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      title: title,
      description: 'Task from UI',
      status: 'TODO',
      priority: priority,
      board_id: parseInt(boardSelect.value)
    })
  });

  if (res.ok) {
    document.getElementById('new-task-title').value = '';
    await onWorkspaceChange();
  }
}

async function updateTaskStatus(taskId, newStatus) {
  const res = await fetch(`/tasks/${taskId}/status?new_status=${newStatus}`, {
    method: 'PATCH',
    headers: { 'Authorization': `Bearer ${token}` }
  });

  if (res.ok) {
    await onWorkspaceChange();
  } else {
    alert('Failed to update status.');
  }
}

function renderBoardTasks(tasks) {
  clearColumns();
  tasks.forEach(t => {
    const card = `
      <div class="card task-card">
        <p class="task-title">${t.title}</p>
        <span class="badge ${t.priority}">${t.priority}</span>
        <div class="task-actions">
          ${t.status !== 'TODO' ? `<button class="status-btn" data-task-id="${t.id}" data-new-status="TODO"> TODO</button>` : ''}
          ${t.status !== 'IN_PROGRESS' ? `<button class="status-btn status-btn-progress" data-task-id="${t.id}" data-new-status="IN PROGRESS">IN PROGRESS</button>` : ''}
          ${t.status !== 'DONE' ? `<button class="status-btn status-btn-done" data-task-id="${t.id}" data-new-status="DONE">DONE </button>` : ''}
        </div>
      </div>
    `;
    if (t.status === 'TODO') document.getElementById('todo-tasks').innerHTML += card;
    if (t.status === 'IN_PROGRESS') document.getElementById('inprogress-tasks').innerHTML += card;
    if (t.status === 'DONE') document.getElementById('done-tasks').innerHTML += card;
  });

  attachStatusButtonListeners();
}

function attachStatusButtonListeners() {
  document.querySelectorAll('.status-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const taskId = this.dataset.taskId;
      const newStatus = this.dataset.newStatus;
      updateTaskStatus(taskId, newStatus);
    });
  });
}

function clearColumns() {
  document.getElementById('todo-tasks').innerHTML = '';
  document.getElementById('inprogress-tasks').innerHTML = '';
  document.getElementById('done-tasks').innerHTML = '';
}

document.getElementById('login-btn').addEventListener('click', login);
document.getElementById('new-workspace-btn').addEventListener('click', createWorkspace);
document.getElementById('new-board-btn').addEventListener('click', createBoard);
document.getElementById('new-task-btn').addEventListener('click', createNewTask);
document.getElementById('workspace-select').addEventListener('change', onWorkspaceChange);