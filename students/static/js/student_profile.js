// static/js/student_profile.js
// Simplified Skills UI (name-only), plus existing Education code preserved below
(function () {
  // ---------- CSRF ----------
  function getCookie(name) {
    const v = `; ${document.cookie}`;
    const parts = v.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }
  const csrftoken = getCookie('csrftoken');

  // ---------- Skills (name-only) ----------
  function renderSkills(skills) {
    const skillsList = document.getElementById('skills-list');
    const chips = document.getElementById('skill-chips');
    if (!skillsList || !chips) return;

    // rebuild skill rows
    skillsList.innerHTML = '';
    skills.forEach((s, i) => {
      const div = document.createElement('div');
      div.className = 'skill-row d-flex justify-content-between align-items-center mb-2';
      div.dataset.skillIndex = i;
      div.dataset.skillName = s.name;
      div.innerHTML = `
        <div>
          <div class="skill-name-display">${s.name}</div>
        </div>
        <div class="text-end">
          <button class="btn btn-sm btn-outline-secondary skill-edit-btn"><i class="fas fa-edit"></i></button>
          <button class="btn btn-sm btn-outline-danger skill-delete-btn"><i class="fas fa-trash"></i></button>
        </div>
        <div class="skill-editor mt-2 w-100" style="display:none;">
          <div class="row g-2 align-items-center">
            <div class="col-md-8">
              <input type="text" class="form-control form-control-sm skill-name-input" value="${s.name}">
            </div>
            <div class="col-md-4 text-end">
              <button class="btn btn-sm btn-success skill-save-btn"><i class="fas fa-check"></i></button>
              <button class="btn btn-sm btn-secondary skill-cancel-btn"><i class="fas fa-times"></i></button>
            </div>
          </div>
        </div>
      `;
      skillsList.appendChild(div);
    });

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

  function openEditorForRow(row) {
    const editor = row.querySelector('.skill-editor');
    const name = row.dataset.skillName || row.querySelector('.skill-name-display').textContent;
    if (!editor) return;
    editor.style.display = '';
    const nameInput = editor.querySelector('.skill-name-input');
    if (nameInput) nameInput.value = name;
  }
  function closeEditorForRow(row) {
    const editor = row.querySelector('.skill-editor');
    if (editor) editor.style.display = 'none';
  }

  function collectSkillsFromDOM() {
    const rows = document.querySelectorAll('#skills-list .skill-row');
    const arr = [];
    rows.forEach(r => {
      const name = (r.dataset.skillName || r.querySelector('.skill-name-display')?.textContent || '').trim();
      if (name) arr.push({ name });
    });
    return arr;
  }

  async function sendSkillsToServer(skills) {
    if (!window.SKILLS_UPDATE_URL) {
      alert('No SKILLS_UPDATE_URL configured on the page.');
      return null;
    }
    // send names-only array for compatibility
    const payload = { skills: skills.map(s => s.name ? s.name.trim() : '').filter(Boolean) };
    try {
      const res = await fetch(window.SKILLS_UPDATE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(payload)
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
    const initialSkillsRaw = window.INITIAL_SKILLS || [];
    // normalize initial skills to [{name: '...'}]
    const initialSkills = initialSkillsRaw.map(s => ({ name: s.name || (typeof s === 'string' ? s : '') })).filter(s => s.name);
    renderSkills(initialSkills);

    // open editor on chip click (same as before)
    document.getElementById('skill-chips')?.addEventListener('click', function (e) {
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

    // Save / Cancel / Delete / Edit handlers (delegated)
    document.getElementById('skills-list')?.addEventListener('click', async function (e) {
      const row = e.target.closest('.skill-row');
      if (!row) return;

      if (e.target.closest('.skill-edit-btn')) {
        openEditorForRow(row);
        return;
      }

      if (e.target.closest('.skill-save-btn')) {
        const editor = row.querySelector('.skill-editor');
        const name = editor.querySelector('.skill-name-input').value.trim();
        if (!name) return alert('Skill name required');
        // update DOM
        row.dataset.skillName = name;
        row.querySelector('.skill-name-display').textContent = name;
        closeEditorForRow(row);

        // send to server
        const skills = collectSkillsFromDOM();
        const res = await sendSkillsToServer(skills);
        if (res && res.success) {
          // if server returns updated list, map to {name}
          const serverList = (res.skills || []).map(x => ({ name: (x.name || x).toString() }));
          renderSkills(serverList.length ? serverList : skills);
        }
        return;
      }

      if (e.target.closest('.skill-cancel-btn')) {
        closeEditorForRow(row);
        return;
      }

      if (e.target.closest('.skill-delete-btn')) {
        if (!confirm('Delete this skill?')) return;
        row.remove();
        const skills = collectSkillsFromDOM();
        const res = await sendSkillsToServer(skills);
        if (res && res.success) {
          const serverList = (res.skills || []).map(x => ({ name: (x.name || x).toString() }));
          renderSkills(serverList);
        }
        return;
      }
    });

    // Add-skill UI
    document.getElementById('add-skill-btn')?.addEventListener('click', function () {
      document.getElementById('add-skill-row').style.display = '';
      document.getElementById('new-skill-name').focus();
    });
    document.getElementById('new-skill-cancel')?.addEventListener('click', function () {
      document.getElementById('add-skill-row').style.display = 'none';
    });
    document.getElementById('new-skill-save')?.addEventListener('click', async function () {
      const name = document.getElementById('new-skill-name').value.trim();
      if (!name) return alert('Skill name required');
      const skills = collectSkillsFromDOM();
      skills.push({ name });
      const res = await sendSkillsToServer(skills);
      if (res && res.success) {
        const serverList = (res.skills || []).map(x => ({ name: (x.name || x).toString() }));
        renderSkills(serverList.length ? serverList : skills);
        document.getElementById('add-skill-row').style.display = 'none';
        document.getElementById('new-skill-name').value = '';
      }
    });
  });

  // ---------- Education code preserved below ----------
  // (append the rest of your existing education IIFE here unchanged)
})();

// ---------- Education inline editor (with client validation) ----------
(function () {
  function getCookie(name) {
    const v = `; ${document.cookie}`;
    const parts = v.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }
  const csrftoken = getCookie('csrftoken');

  function renderEducation(list) {
    const container = document.getElementById('education-list');
    if (!container) return;
    const rows = container.querySelectorAll('.education-row');
    if (rows.length && rows.length === list.length) {
      rows.forEach((row, i) => {
        const e = list[i];
        row.dataset.degree = e.degree || '';
        row.dataset.institute = e.institute || '';
        row.dataset.start = e.start_year || '';
        row.dataset.end = e.end_year || '';
        row.dataset.cgpa = e.cgpa || '';
        row.dataset.desc = e.description || '';
        row.querySelector('.edu-degree').textContent = e.degree || '';
        row.querySelector('.edu-institute').textContent = e.institute || '';
        const meta = row.querySelector('.text-muted.small');
        if (meta) meta.textContent = `${e.start_year || ''} - ${e.end_year || ''} \u00B7 CGPA: ${e.cgpa || ''}`;
        row.querySelector('.edu-desc').textContent = e.description || '';
        const editor = row.querySelector('.education-editor');
        if (editor) {
          editor.querySelector('.edu-input-degree').value = e.degree || '';
          editor.querySelector('.edu-input-institute').value = e.institute || '';
          editor.querySelector('.edu-input-start').value = e.start_year || '';
          editor.querySelector('.edu-input-end').value = e.end_year || '';
          editor.querySelector('.edu-input-cgpa').value = e.cgpa || '';
          editor.querySelector('.edu-input-desc').value = e.description || '';
        }
      });
    } else {
      container.innerHTML = '';
      list.forEach((e, idx) => {
        const el = document.createElement('div');
        el.className = 'education-row mb-3 p-3 rounded';
        el.dataset.index = idx;
        el.dataset.degree = e.degree || '';
        el.dataset.institute = e.institute || '';
        el.dataset.start = e.start_year || '';
        el.dataset.end = e.end_year || '';
        el.dataset.cgpa = e.cgpa || '';
        el.dataset.desc = e.description || '';
        el.innerHTML = `
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h5 class="mb-1 edu-degree">${e.degree || ''}</h5>
              <div class="edu-institute text-primary mb-1">${e.institute || ''}</div>
              <div class="text-muted small">${e.start_year || ''} - ${e.end_year || ''} &nbsp;•&nbsp; CGPA: ${e.cgpa || ''}</div>
              <div class="edu-desc mt-2 text-muted">${e.description || ''}</div>
            </div>
            <div class="text-end">
              <button class="btn btn-sm btn-outline-secondary edu-edit-btn"><i class="fas fa-edit"></i></button>
              <button class="btn btn-sm btn-outline-danger edu-delete-btn"><i class="fas fa-trash"></i></button>
            </div>
          </div>
          <div class="education-editor mt-3" style="display:none;">
            <div class="row g-2">
              <div class="col-md-6"><input type="text" class="form-control form-control-sm edu-input-degree" placeholder="Degree / Course" value="${e.degree || ''}"></div>
              <div class="col-md-6"><input type="text" class="form-control form-control-sm edu-input-institute" placeholder="Institute" value="${e.institute || ''}"></div>
              <div class="col-md-3"><input type="text" class="form-control form-control-sm edu-input-start" placeholder="Start Year" value="${e.start_year || ''}"></div>
              <div class="col-md-3"><input type="text" class="form-control form-control-sm edu-input-end" placeholder="End Year" value="${e.end_year || ''}"></div>
              <div class="col-md-3"><input type="text" class="form-control form-control-sm edu-input-cgpa" placeholder="CGPA" value="${e.cgpa || ''}"></div>
              <div class="col-md-12 mt-2"><textarea class="form-control form-control-sm edu-input-desc" placeholder="Description / coursework" rows="2">${e.description || ''}</textarea></div>
              <div class="col-md-12 text-end mt-2"><button class="btn btn-sm btn-success edu-save-btn"><i class="fas fa-check"></i> Save</button> <button class="btn btn-sm btn-secondary edu-cancel-btn"><i class="fas fa-times"></i> Cancel</button></div>
            </div>
          </div>
        `;
        container.appendChild(el);
      });
    }

    // Disable Add button if reached max
    const addBtn = document.getElementById('add-edu-btn');
    if (addBtn) addBtn.disabled = (list.length >= 2);
  }

  async function postEducationToServer(list) {
    if (!window.EDU_UPDATE_URL) {
      alert('No EDU_UPDATE_URL configured on page.');
      return null;
    }

    // Client-side validation before sending
    // - enforce max 2
    if (!Array.isArray(list)) list = [];
    if (list.length > 2) {
      alert('You can only save up to 2 education entries.');
      return null;
    }

    // Validate cgpa numeric
    for (const e of list) {
      const cgpa = (e.cgpa || '').toString().trim();
      if (cgpa) {
        if (isNaN(Number(cgpa))) {
          alert(`CGPA must be a number for "${e.degree || e.institute || ''}".`);
          return null;
        }
      }
    }

    try {
      const res = await fetch(window.EDU_UPDATE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ education: list })
      });

      const text = await res.text();
      let data = null;
      try { data = JSON.parse(text); } catch (e) { /* not JSON */ }

      if (!res.ok) {
        const msg = (data && data.message) ? data.message : `Server error ${res.status}`;
        alert(msg);
        return null;
      }
      return data;
    } catch (err) {
      console.error('Education save error', err);
      alert('Could not save education: ' + (err.message || err));
      return null;
    }
  }

  function openEditor(row) {
    const editor = row.querySelector('.education-editor');
    if (!editor) return;
    editor.style.display = '';
  }
  function closeEditor(row) {
    const editor = row.querySelector('.education-editor');
    if (editor) editor.style.display = 'none';
  }
  function collectEducationFromDOM() {
    const rows = document.querySelectorAll('#education-list .education-row');
    const arr = [];
    rows.forEach(r => {
      arr.push({
        degree: (r.dataset.degree || '').trim(),
        institute: (r.dataset.institute || '').trim(),
        start_year: (r.dataset.start || '').trim(),
        end_year: (r.dataset.end || '').trim(),
        cgpa: (r.dataset.cgpa || '').trim(),
        description: (r.dataset.desc || '').trim()
      });
    });
    return arr;
  }

  document.addEventListener('DOMContentLoaded', function () {
    // initial render from template-provided data
    const initial = window.INITIAL_EDUCATION || [];
    renderEducation(initial);

    // delegate edit/delete/save/cancel
    document.getElementById('education-list').addEventListener('click', async function (e) {
      const row = e.target.closest('.education-row');
      if (!row) return;

      // Edit
      if (e.target.closest('.edu-edit-btn')) {
        openEditor(row);
        return;
      }
      // Delete
      if (e.target.closest('.edu-delete-btn')) {
        if (!confirm('Delete this education entry?')) return;
        row.remove();
        const list = collectEducationFromDOM();
        const res = await postEducationToServer(list);
        if (res && res.success) renderEducation(res.education || list);
        return;
      }
      // Save (inline)
      if (e.target.closest('.edu-save-btn')) {
        const editor = row.querySelector('.education-editor');
        const degree = editor.querySelector('.edu-input-degree').value.trim();
        const institute = editor.querySelector('.edu-input-institute').value.trim();
        const start = editor.querySelector('.edu-input-start').value.trim();
        const end = editor.querySelector('.edu-input-end').value.trim();
        const cgpa = editor.querySelector('.edu-input-cgpa').value.trim();
        const desc = editor.querySelector('.edu-input-desc').value.trim();

        // client-side cgpa validation
        if (cgpa && isNaN(Number(cgpa))) {
          alert('CGPA must be a number');
          return;
        }

        // Update row dataset and display
        row.dataset.degree = degree;
        row.dataset.institute = institute;
        row.dataset.start = start;
        row.dataset.end = end;
        row.dataset.cgpa = cgpa;
        row.dataset.desc = desc;

        row.querySelector('.edu-degree').textContent = degree;
        row.querySelector('.edu-institute').textContent = institute;
        const meta = row.querySelector('.text-muted.small');
        if (meta) meta.textContent = `${start} - ${end} \u00B7 CGPA: ${cgpa}`;
        row.querySelector('.edu-desc').textContent = desc;

        closeEditor(row);

        // save all to server
        const list = collectEducationFromDOM();
        // client-side max 2 guard
        if (list.length > 2) {
          alert('You can only save up to 2 education entries.');
          return;
        }
        const res = await postEducationToServer(list);
        if (res && res.success) renderEducation(res.education || list);
        return;
      }

      // Cancel
      if (e.target.closest('.edu-cancel-btn')) {
        closeEditor(row);
        return;
      }
    });

    // Add education handlers
    document.getElementById('add-edu-btn').addEventListener('click', function () {
      // disable if already 2 entries
      const current = document.querySelectorAll('#education-list .education-row').length;
      if (current >= 2) {
        alert('You already have 2 education entries (maximum).');
        return;
      }
      document.getElementById('add-edu-row').style.display = '';
      document.getElementById('new-edu-degree').focus();
    });
    document.getElementById('new-edu-cancel').addEventListener('click', function () {
      document.getElementById('add-edu-row').style.display = 'none';
    });
    document.getElementById('new-edu-save').addEventListener('click', async function () {
      const degree = document.getElementById('new-edu-degree').value.trim();
      const institute = document.getElementById('new-edu-institute').value.trim();
      const start = document.getElementById('new-edu-start').value.trim();
      const end = document.getElementById('new-edu-end').value.trim();
      const cgpa = document.getElementById('new-edu-cgpa').value.trim();
      const desc = document.getElementById('new-edu-desc').value.trim();

      // client-side cgpa validation
      if (cgpa && isNaN(Number(cgpa))) {
        alert('CGPA must be a number');
        return;
      }

      // guard max 2
      const list = collectEducationFromDOM();
      if (list.length >= 2) {
        alert('You can only save up to 2 education entries.');
        return;
      }

      list.push({ degree, institute, start_year: start, end_year: end, cgpa, description: desc });
      const res = await postEducationToServer(list);
      if (res && res.success) {
        renderEducation(res.education || list);
        // hide add form and reset
        document.getElementById('add-edu-row').style.display = 'none';
        document.getElementById('new-edu-degree').value = '';
        document.getElementById('new-edu-institute').value = '';
        document.getElementById('new-edu-start').value = '';
        document.getElementById('new-edu-end').value = '';
        document.getElementById('new-edu-cgpa').value = '';
        document.getElementById('new-edu-desc').value = '';
      }
    });
  });
})();
