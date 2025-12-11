// static/js/student_profile.js
// Inline-edit skills UI for Student Profile
(function () {
  // ---------- CSRF ----------
  function getCookie(name) {
    const v = `; ${document.cookie}`;
    const parts = v.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }
  const csrftoken = getCookie('csrftoken');

  // ---------- Rendering ----------
  function renderSkills(skills) {
    const skillsList = document.getElementById('skills-list');
    const chips = document.getElementById('skill-chips');

    // update rows (if exist) or create fallback rows
    const rows = skillsList.querySelectorAll('.skill-row');
    if (rows.length && rows.length === skills.length) {
      rows.forEach((row, i) => {
        const s = skills[i];
        row.dataset.skillName = s.name;
        row.dataset.skillPercent = s.percent;
        row.querySelector('.skill-name-display').textContent = s.name;
        row.querySelector('.skill-percent-display').textContent = s.percent + '%';
        const fill = row.querySelector('.progress-fill');
        if (fill) fill.style.width = s.percent + '%';
        const range = row.querySelector('.skill-range-input');
        if (range) range.value = s.percent;
        const rangeVal = row.querySelector('.skill-range-value');
        if (rangeVal) rangeVal.textContent = s.percent;
        const nameInput = row.querySelector('.skill-name-input');
        if (nameInput) nameInput.value = s.name;
      });
    } else {
      // Not same count: rebuild skill rows (simple)
      skillsList.innerHTML = '';
      skills.forEach((s, i) => {
        const div = document.createElement('div');
        div.className = 'skill-row';
        div.dataset.skillIndex = i;
        div.dataset.skillName = s.name;
        div.dataset.skillPercent = s.percent;
        div.innerHTML = `
          <div class="progress-label d-flex justify-content-between">
            <span class="skill-name-display">${s.name}</span>
            <span class="skill-percent-display">${s.percent}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width:${s.percent}%"></div>
          </div>
          <div class="skill-editor mt-2" style="display:none;">
            <div class="row g-2 align-items-center">
              <div class="col-md-5">
                <input type="text" class="form-control form-control-sm skill-name-input" value="${s.name}">
              </div>
              <div class="col-md-5">
                <input type="range" min="0" max="100" class="form-range skill-range-input" value="${s.percent}">
                <div class="small text-muted">Percentage: <span class="skill-range-value">${s.percent}</span>%</div>
              </div>
              <div class="col-md-2 text-end">
                <button class="btn btn-sm btn-success skill-save-btn"><i class="fas fa-check"></i></button>
                <button class="btn btn-sm btn-secondary skill-cancel-btn"><i class="fas fa-times"></i></button>
                <button class="btn btn-sm btn-danger skill-delete-btn" title="Delete"><i class="fas fa-trash"></i></button>
              </div>
            </div>
          </div>
        `;
        skillsList.appendChild(div);
      });
    }

    // rebuild chips
    chips.innerHTML = '';
    skills.forEach(s => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-outline-primary btn-sm skill-chip me-2 mb-2';
      btn.dataset.skill = s.name;
      btn.textContent = s.name;
      chips.appendChild(btn);
    });
  }

  // ---------- DOM helpers ----------
  function openEditorForRow(row) {
    const editor = row.querySelector('.skill-editor');
    const name = row.dataset.skillName || row.querySelector('.skill-name-display').textContent;
    const percent = parseInt(row.dataset.skillPercent || 0);
    editor.style.display = '';
    const nameInput = editor.querySelector('.skill-name-input');
    const range = editor.querySelector('.skill-range-input');
    const rangeVal = editor.querySelector('.skill-range-value');
    if (nameInput) nameInput.value = name;
    if (range) { range.value = percent; range.oninput = () => { rangeVal.textContent = range.value; }; }
    if (rangeVal) rangeVal.textContent = percent;
  }
  function closeEditorForRow(row) {
    const editor = row.querySelector('.skill-editor');
    if (editor) editor.style.display = 'none';
  }
  function collectSkillsFromDOM() {
    const rows = document.querySelectorAll('#skills-list .skill-row');
    const arr = [];
    rows.forEach(r => {
      const name = r.dataset.skillName || r.querySelector('.skill-name-display')?.textContent.trim();
      const percent = parseInt(r.dataset.skillPercent || r.querySelector('.skill-percent-display')?.textContent.replace('%','')) || 0;
      if (name) arr.push({ name, percent });
    });
    return arr;
  }

  // ---------- Server communication ----------
  async function sendSkillsToServer(skills) {
    if (!window.SKILLS_UPDATE_URL) {
      alert('No SKILLS_UPDATE_URL configured on the page.');
      return null;
    }
    try {
      const res = await fetch(window.SKILLS_UPDATE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ skills: skills })
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error('Server error: ' + res.status + ' - ' + text);
      }
      const data = await res.json();
      return data;
    } catch (err) {
      console.error('Save skills error', err);
      alert('Could not save skills: ' + (err.message || err));
      return null;
    }
  }

  // ---------- Initialization ----------
  document.addEventListener('DOMContentLoaded', function () {
    // read initial skills passed from template (json_script)
    const initialSkills = window.INITIAL_SKILLS || [];
    renderSkills(initialSkills);

    // open editor on chip click
    document.getElementById('skill-chips').addEventListener('click', function (e) {
      const btn = e.target.closest('.skill-chip');
      if (!btn) return;
      const skillName = btn.dataset.skill;
      const rows = document.querySelectorAll('#skills-list .skill-row');
      for (let i=0;i<rows.length;i++) {
        const row = rows[i];
        if ((row.dataset.skillName || row.querySelector('.skill-name-display').textContent).trim() === skillName) {
          openEditorForRow(row);
          row.scrollIntoView({behavior:'smooth', block:'center'});
          break;
        }
      }
    });

    // Save / Cancel / Delete handlers (delegated)
    document.getElementById('skills-list').addEventListener('click', async function (e) {
      const row = e.target.closest('.skill-row');
      if (!row) return;

      if (e.target.closest('.skill-save-btn')) {
        const editor = row.querySelector('.skill-editor');
        const name = editor.querySelector('.skill-name-input').value.trim();
        const percent = parseInt(editor.querySelector('.skill-range-input').value || 0);
        // update DOM
        row.dataset.skillName = name;
        row.dataset.skillPercent = percent;
        row.querySelector('.skill-name-display').textContent = name;
        row.querySelector('.skill-percent-display').textContent = percent + '%';
        const fill = row.querySelector('.progress-fill'); if (fill) fill.style.width = percent + '%';
        closeEditorForRow(row);

        // send to server
        const skills = collectSkillsFromDOM();
        const res = await sendSkillsToServer(skills);
        if (res && res.success) {
          // if server returns updated list, use it
          if (res.skills) renderSkills(res.skills);
        }
      }

      if (e.target.closest('.skill-cancel-btn')) {
        closeEditorForRow(row);
      }

      if (e.target.closest('.skill-delete-btn')) {
        if (!confirm('Delete this skill?')) return;
        row.remove();
        const skills = collectSkillsFromDOM();
        const res = await sendSkillsToServer(skills);
        if (res && res.success && res.skills) renderSkills(res.skills);
      }
    });

    // Add-skill UI
    document.getElementById('add-skill-btn').addEventListener('click', function () {
      document.getElementById('add-skill-row').style.display = '';
      document.getElementById('new-skill-name').focus();
    });
    document.getElementById('new-skill-cancel').addEventListener('click', function () {
      document.getElementById('add-skill-row').style.display = 'none';
    });
    const newRange = document.getElementById('new-skill-range');
    if (newRange) {
      newRange.oninput = function () {
        document.getElementById('new-skill-range-value').textContent = this.value;
      };
    }
    document.getElementById('new-skill-save').addEventListener('click', async function () {
      const name = document.getElementById('new-skill-name').value.trim();
      const percent = parseInt(document.getElementById('new-skill-range').value || 0);
      if (!name) return alert('Skill name required');
      const skills = collectSkillsFromDOM();
      skills.push({ name, percent });
      const res = await sendSkillsToServer(skills);
      if (res && res.success) {
        renderSkills(res.skills || skills);
        document.getElementById('add-skill-row').style.display = 'none';
        document.getElementById('new-skill-name').value = '';
        document.getElementById('new-skill-range').value = 70;
        document.getElementById('new-skill-range-value').textContent = 70;
      }
    });
  });
})();
