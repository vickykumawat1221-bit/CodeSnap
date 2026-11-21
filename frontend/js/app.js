/**
 * app.js - Main Application Controller for CodeSnap IDE
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Code Editor
  const editor = new CodeEditor('codeEditor', 'lineGutter', 'highlightCode');

  // 2. Initialize Visualizers (AST and Automata)
  Visualizer.init();

  // State
  let samplePrograms = [];
  let defaultCode = `START
# Welcome to CodeSnap Mini Programming Language!
# CSE Theory of Computation Mini-Project

LET name = "Vikash"
LET age = 21
LET marks = 89.5
LET passed = TRUE

PRINT "Student Name:"
PRINT name
PRINT "Age:"
PRINT age
PRINT "Score:"
PRINT marks

IF age >= 18 AND marks >= 40
    PRINT "Status: Qualified & Passed!"
ELSE
    PRINT "Status: Not Qualified"
END

STOP`;

  editor.setValue(defaultCode);

  // 3. Tab Switching in Inspector Pane
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.classList.add('active');

      if (targetId === 'tabAutomata' && !Visualizer.currentDfa) {
        Visualizer.loadSelectedDfa('identifier');
      }
    });
  });

  // 4. Load Sample Programs
  async function loadSamples() {
    try {
      const res = await API.getExamples();
      samplePrograms = res.examples || [];

      const selectElem = document.getElementById('exampleSelect');
      const listElem = document.getElementById('examplesList');

      selectElem.innerHTML = '<option value="">-- Load Sample Program --</option>';
      listElem.innerHTML = '';

      samplePrograms.forEach((ex, idx) => {
        // Dropdown option
        const opt = document.createElement('option');
        opt.value = ex.id;
        opt.textContent = ex.title;
        selectElem.appendChild(opt);

        // Sidebar button
        const btn = document.createElement('button');
        btn.className = 'example-item-btn';
        btn.innerHTML = `<span style="opacity: 0.6;">#${idx + 1}</span> <span>${ex.title}</span>`;
        btn.addEventListener('click', () => loadSpecificExample(ex.id));
        listElem.appendChild(btn);
      });
    } catch (err) {
      console.warn('Could not load sample programs from server:', err);
    }
  }

  function loadSpecificExample(id) {
    const ex = samplePrograms.find(p => p.id === id);
    if (!ex) return;

    editor.setValue(ex.code);
    const selectElem = document.getElementById('exampleSelect');
    if (selectElem) selectElem.value = id;

    // Highlight active in sidebar
    document.querySelectorAll('.example-item-btn').forEach(btn => {
      btn.classList.toggle('active', btn.textContent.includes(ex.title));
    });

    logConsole(`[System] Loaded sample program: "${ex.title}"`, 'system');
  }

  const selectElem = document.getElementById('exampleSelect');
  selectElem.addEventListener('change', (e) => {
    if (e.target.value) loadSpecificExample(e.target.value);
  });

  // 5. Execution Pipeline (Run)
  async function handleRun() {
    const code = editor.getValue();
    const btnRun = document.getElementById('btnRun');
    const compStatus = document.getElementById('compilationStatus');

    btnRun.disabled = true;
    btnRun.innerHTML = '<span>Running...</span>';
    compStatus.textContent = 'Executing...';
    compStatus.className = 'tag-status';

    resetPhasesStatus();

    try {
      const res = await API.run(code);
      updateInspectionResults(res);

      if (res.success) {
        compStatus.textContent = 'Success';
        compStatus.className = 'tag-status success';
        updatePhasesSuccess();
      } else {
        compStatus.textContent = res.phase_failed || 'Error';
        compStatus.className = 'tag-status error';
        markPhaseFailed(res.phase_failed);
      }
    } catch (err) {
      logConsole(`Execution request failed: ${err.message}`, 'error');
      compStatus.textContent = 'Server Error';
      compStatus.className = 'tag-status error';
    } finally {
      btnRun.disabled = false;
      btnRun.innerHTML = `
        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        <span>Run</span>
        <kbd>Ctrl+↵</kbd>
      `;
    }
  }

  // 6. Compilation Pipeline (Compile Only)
  async function handleCompile() {
    const code = editor.getValue();
    const btnCompile = document.getElementById('btnCompile');
    const compStatus = document.getElementById('compilationStatus');

    btnCompile.disabled = true;
    btnCompile.innerHTML = '<span>Compiling...</span>';
    compStatus.textContent = 'Compiling...';
    compStatus.className = 'tag-status';

    resetPhasesStatus();

    try {
      const res = await API.compile(code);
      updateInspectionResults(res, false);

      if (res.success) {
        compStatus.textContent = 'Compiled';
        compStatus.className = 'tag-status success';
        setPhaseStatus('statusLex', 'PASSED', 'passed');
        setPhaseStatus('statusParse', 'PASSED', 'passed');
        setPhaseStatus('statusSemantic', 'PASSED', 'passed');
        logConsole(`[Compiler] Program compiled successfully in ${res.total_time_ms} ms. Ready to Run.`, 'success');
      } else {
        compStatus.textContent = res.phase_failed || 'Compile Error';
        compStatus.className = 'tag-status error';
        markPhaseFailed(res.phase_failed);
      }
    } catch (err) {
      logConsole(`Compilation request failed: ${err.message}`, 'error');
      compStatus.textContent = 'Error';
      compStatus.className = 'tag-status error';
    } finally {
      btnCompile.disabled = false;
      btnCompile.innerHTML = `
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
        </svg>
        <span>Compile</span>
      `;
    }
  }

  // 7. Update UI from Compilation / Run Result
  function updateInspectionResults(data, isRun = true) {
    // A. Terminal Output
    if (isRun) {
      const consoleBox = document.getElementById('consoleOutput');
      consoleBox.innerHTML = '';

      if (data.output && data.output.length > 0) {
        data.output.forEach(line => {
          logConsole(line, 'out');
        });
      }

      const execTime = document.getElementById('execTimeBadge');
      const stepCount = document.getElementById('stepCountBadge');
      if (execTime) execTime.textContent = `Time: ${data.execution_time_ms || 0} ms`;
      if (stepCount) stepCount.textContent = `Steps: ${data.step_count || 0}`;

      if (data.errors && data.errors.length > 0) {
        data.errors.forEach(err => {
          logConsole(`${err.category}: ${err.message} (Line ${err.line || '?'}, Col ${err.column || '?'})`, 'error');
          if (err.suggestion) {
            logConsole(`  ↳ Suggestion: ${err.suggestion}`, 'system');
          }
        });
      } else {
        logConsole(`[Execution Finished in ${data.execution_time_ms} ms]`, 'success');
      }
    }

    // B. Tokens Table
    const tokens = data.tokens || [];
    renderTokensTable(tokens);
    document.getElementById('tokenCountBadge').textContent = tokens.length;

    // C. AST Tree
    if (data.ast) {
      Visualizer.renderAST(data.ast);
    }

    // D. Symbol Table / Variables
    const symbols = data.symbols || data.variables || [];
    renderSymbolTable(symbols);
    document.getElementById('symbolCountBadge').textContent = symbols.length;

    // E. Error Explorer
    const errors = data.errors || [];
    renderErrorCards(errors);
    document.getElementById('errorCountBadge').textContent = errors.length;

    // Automatically switch to errors tab if errors occurred and not on console
    if (errors.length > 0 && !isRun) {
      switchTab('tabErrors');
    }
  }

  function logConsole(message, type = 'out') {
    const consoleBox = document.getElementById('consoleOutput');
    const line = document.createElement('div');
    line.className = `terminal-line ${type}`;
    line.textContent = message;
    consoleBox.appendChild(line);
    consoleBox.scrollTop = consoleBox.scrollHeight;
  }

  function renderTokensTable(tokens) {
    const tbody = document.getElementById('tokenTableBody');
    if (tokens.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No tokens found.</td></tr>';
      return;
    }

    let rows = '';
    tokens.forEach((t, i) => {
      const displayLexeme = t.lexeme === '\n' ? '\\n' : t.lexeme;
      rows += `
        <tr>
          <td><span style="color: #6E7681;">${i + 1}</span></td>
          <td><strong style="color: #79C0FF;">${escapeHtml(displayLexeme)}</strong></td>
          <td><span class="badge">${t.name || t.type}</span></td>
          <td>${t.line}:${t.column}</td>
          <td style="color: #9CA3AF; font-size: 0.72rem;">${escapeHtml(t.pattern_desc || '-')}</td>
        </tr>
      `;
    });
    tbody.innerHTML = rows;
  }

  function renderSymbolTable(symbols) {
    const tbody = document.getElementById('symbolTableBody');
    if (symbols.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No declared variables in symbol table.</td></tr>';
      return;
    }

    let rows = '';
    symbols.forEach(sym => {
      rows += `
        <tr>
          <td><strong style="color: #FCD34D;">${sym.name}</strong></td>
          <td><span class="badge" style="color: #93C5FD;">${sym.type}</span></td>
          <td><span style="color: #86EFAC;">${sym.value !== undefined ? sym.value : 'unassigned'}</span></td>
          <td>${sym.line || 1}</td>
          <td>${sym.scope || 'Global'}</td>
        </tr>
      `;
    });
    tbody.innerHTML = rows;
  }

  function renderErrorCards(errors) {
    const container = document.getElementById('errorCardsContainer');
    if (errors.length === 0) {
      container.innerHTML = `
        <div class="clean-state">
          <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="#22C55E" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
          <p>No compilation or runtime errors. Code is clean!</p>
        </div>
      `;
      return;
    }

    let cards = '';
    errors.forEach(err => {
      cards += `
        <div class="error-card">
          <div class="error-header">
            <span class="error-category">${err.category}</span>
            <span class="error-loc-badge">Line ${err.line || '?'}, Col ${err.column || '?'}</span>
          </div>
          <div class="error-msg">${escapeHtml(err.message)}</div>
          ${err.suggestion ? `<div class="error-suggestion">💡 <strong>Suggestion:</strong> ${escapeHtml(err.suggestion)}</div>` : ''}
        </div>
      `;
    });
    container.innerHTML = cards;
  }

  function resetPhasesStatus() {
    setPhaseStatus('statusLex', '-', '');
    setPhaseStatus('statusParse', '-', '');
    setPhaseStatus('statusSemantic', '-', '');
    setPhaseStatus('statusExec', '-', '');
  }

  function updatePhasesSuccess() {
    setPhaseStatus('statusLex', 'PASSED', 'passed');
    setPhaseStatus('statusParse', 'PASSED', 'passed');
    setPhaseStatus('statusSemantic', 'PASSED', 'passed');
    setPhaseStatus('statusExec', 'PASSED', 'passed');
  }

  function markPhaseFailed(phaseName) {
    if (phaseName === 'Lexical Analysis') {
      setPhaseStatus('statusLex', 'FAILED', 'failed');
    } else if (phaseName === 'Syntax Analysis') {
      setPhaseStatus('statusLex', 'PASSED', 'passed');
      setPhaseStatus('statusParse', 'FAILED', 'failed');
    } else if (phaseName === 'Semantic Analysis') {
      setPhaseStatus('statusLex', 'PASSED', 'passed');
      setPhaseStatus('statusParse', 'PASSED', 'passed');
      setPhaseStatus('statusSemantic', 'FAILED', 'failed');
    } else if (phaseName === 'Runtime Execution') {
      setPhaseStatus('statusLex', 'PASSED', 'passed');
      setPhaseStatus('statusParse', 'PASSED', 'passed');
      setPhaseStatus('statusSemantic', 'PASSED', 'passed');
      setPhaseStatus('statusExec', 'FAILED', 'failed');
    }
  }

  function setPhaseStatus(elemId, text, className) {
    const el = document.getElementById(elemId);
    if (el) {
      el.textContent = text;
      el.className = `phase-status ${className}`;
    }
  }

  function switchTab(tabId) {
    tabButtons.forEach(b => {
      if (b.getAttribute('data-tab') === tabId) b.click();
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // 8. Event Listeners
  document.getElementById('btnRun').addEventListener('click', handleRun);
  document.getElementById('btnCompile').addEventListener('click', handleCompile);
  document.getElementById('btnClear').addEventListener('click', () => {
    document.getElementById('consoleOutput').innerHTML = '<div class="terminal-text-dim">Console cleared.</div>';
  });
  document.getElementById('btnReset').addEventListener('click', () => {
    editor.setValue(defaultCode);
    logConsole('[System] Reset editor to default code.', 'system');
  });

  document.getElementById('btnFormat').addEventListener('click', () => {
    editor.formatCode();
  });

  document.getElementById('btnCopyCode').addEventListener('click', () => {
    navigator.clipboard.writeText(editor.getValue()).then(() => {
      const btn = document.getElementById('btnCopyCode');
      btn.textContent = 'Copied!';
      setTimeout(() => btn.textContent = 'Copy', 1500);
    });
  });

  // Automata Studio Nav Button
  document.getElementById('btnOpenAutomata').addEventListener('click', () => {
    switchTab('tabAutomata');
  });

  // Docs Modal Toggle
  const docsModal = document.getElementById('docsModal');
  document.getElementById('btnDocsModal').addEventListener('click', () => {
    docsModal.style.display = 'flex';
  });
  document.getElementById('btnCloseDocs').addEventListener('click', () => {
    docsModal.style.display = 'none';
  });
  docsModal.addEventListener('click', (e) => {
    if (e.target === docsModal) docsModal.style.display = 'none';
  });

  // Keyboard shortcut: Ctrl+Enter or Cmd+Enter to Run
  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleRun();
    }
  });

  // Token Filter
  document.getElementById('tokenFilter').addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase();
    const rows = document.querySelectorAll('#tokenTableBody tr');
    rows.forEach(r => {
      r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  });

  // Initialize
  loadSamples();
  API.checkHealth().then(() => {
    logConsole('[System] Connected to CodeSnap Compiler backend.', 'system');
  }).catch(() => {
    logConsole('[System] Offline / Local sandbox mode active.', 'system');
  });
});
