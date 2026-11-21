/**
 * visualizer.js - Abstract Syntax Tree & TOC Finite Automata Visualizers
 */

const Visualizer = {
  // AST Visualizer State
  astScale: 1.0,
  astTranslateX: 40,
  astTranslateY: 40,
  isAstPanning: false,
  astPanStart: { x: 0, y: 0 },
  currentAstData: null,

  // DFA Visualizer State
  currentDfa: null,
  activeDfaState: null,

  init() {
    this.initAstPanZoom();
    this.initDfaEvents();
  },

  // ---------------- AST VISUALIZATION ----------------

  initAstPanZoom() {
    const container = document.getElementById('astVisualContainer');
    const svg = document.getElementById('astSvgCanvas');

    container.addEventListener('mousedown', (e) => {
      if (e.target.closest('.ast-node-group')) return;
      this.isAstPanning = true;
      this.astPanStart = { x: e.clientX - this.astTranslateX, y: e.clientY - this.astTranslateY };
      container.style.cursor = 'grabbing';
    });

    window.addEventListener('mousemove', (e) => {
      if (!this.isAstPanning) return;
      this.astTranslateX = e.clientX - this.astPanStart.x;
      this.astTranslateY = e.clientY - this.astPanStart.y;
      this.updateAstTransform();
    });

    window.addEventListener('mouseup', () => {
      this.isAstPanning = false;
      container.style.cursor = 'grab';
    });

    container.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
      this.astScale = Math.min(Math.max(0.3, this.astScale * zoomFactor), 2.5);
      this.updateAstTransform();
    });

    document.getElementById('btnZoomIn').addEventListener('click', () => {
      this.astScale = Math.min(2.5, this.astScale * 1.2);
      this.updateAstTransform();
    });

    document.getElementById('btnZoomOut').addEventListener('click', () => {
      this.astScale = Math.max(0.3, this.astScale * 0.8);
      this.updateAstTransform();
    });

    document.getElementById('btnResetZoom').addEventListener('click', () => {
      this.astScale = 1.0;
      this.astTranslateX = 40;
      this.astTranslateY = 40;
      this.updateAstTransform();
    });

    document.getElementById('btnToggleAstJson').addEventListener('click', () => {
      const jsonView = document.getElementById('astJsonView');
      const isVisible = jsonView.style.display !== 'none';
      jsonView.style.display = isVisible ? 'none' : 'block';
      document.getElementById('btnToggleAstJson').textContent = isVisible ? 'JSON View' : 'Tree View';
    });
  },

  updateAstTransform() {
    const g = document.getElementById('astRootGroup');
    if (g) {
      g.setAttribute('transform', `translate(${this.astTranslateX}, ${this.astTranslateY}) scale(${this.astScale})`);
    }
  },

  renderAST(astNode) {
    this.currentAstData = astNode;
    const svg = document.getElementById('astSvgCanvas');
    const pre = document.getElementById('astJsonPre');
    pre.textContent = JSON.stringify(astNode, null, 2);

    if (!astNode) {
      svg.innerHTML = '<text x="40" y="50" fill="#6E7681" font-size="14">No AST to display.</text>';
      return;
    }

    // 1. Calculate layout positions
    const nodeWidth = 140;
    const nodeHeight = 36;
    const horizontalGap = 24;
    const verticalGap = 70;

    let nextX = 0;
    const assignPositions = (node, depth = 0) => {
      const children = node.children || [];
      if (children.length === 0) {
        node._x = nextX;
        node._y = depth * verticalGap;
        nextX += nodeWidth + horizontalGap;
        return;
      }
      for (const child of children) {
        assignPositions(child, depth + 1);
      }
      const firstChild = children[0];
      const lastChild = children[children.length - 1];
      node._x = (firstChild._x + lastChild._x) / 2;
      node._y = depth * verticalGap;
    };

    assignPositions(astNode);

    // 2. Render SVG elements
    svg.innerHTML = `
      <defs>
        <marker id="astArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 8 5 L 0 9 z" fill="#4B5563" />
        </marker>
      </defs>
      <g id="astRootGroup"></g>
    `;

    const rootGroup = document.getElementById('astRootGroup');

    // Draw links
    const drawLinks = (node) => {
      const children = node.children || [];
      for (const child of children) {
        const startX = node._x + nodeWidth / 2;
        const startY = node._y + nodeHeight;
        const endX = child._x + nodeWidth / 2;
        const endY = child._y;

        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const midY = (startY + endY) / 2;
        const d = `M ${startX} ${startY} C ${startX} ${midY}, ${endX} ${midY}, ${endX} ${endY}`;
        path.setAttribute('d', d);
        path.setAttribute('stroke', '#374151');
        path.setAttribute('stroke-width', '1.8');
        path.setAttribute('fill', 'none');
        path.setAttribute('marker-end', 'url(#astArrow)');
        rootGroup.appendChild(path);

        drawLinks(child);
      }
    };
    drawLinks(astNode);

    // Draw nodes
    const drawNodes = (node) => {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('class', 'ast-node-group');
      g.setAttribute('transform', `translate(${node._x}, ${node._y})`);
      g.style.cursor = 'pointer';

      const colorMap = {
        Program: '#3B82F6',
        Declaration: '#06B6D4',
        Assignment: '#0EA5E9',
        Statement: '#6366F1',
        ControlFlow: '#8B5CF6',
        Condition: '#EC4899',
        Block: '#64748B',
        Operator: '#F59E0B',
        Literal: '#10B981',
        Variable: '#38BDF8',
        Bound: '#A855F7'
      };

      const strokeColor = colorMap[node.category] || '#3B82F6';

      // Rect
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('width', nodeWidth);
      rect.setAttribute('height', nodeHeight);
      rect.setAttribute('rx', '6');
      rect.setAttribute('fill', '#161B22');
      rect.setAttribute('stroke', strokeColor);
      rect.setAttribute('stroke-width', '1.6');
      g.appendChild(rect);

      // Label text
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', nodeWidth / 2);
      text.setAttribute('y', nodeHeight / 2 + 4);
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('fill', '#F3F4F6');
      text.setAttribute('font-family', 'Fira Code, monospace');
      text.setAttribute('font-size', '11.5px');
      text.setAttribute('font-weight', '500');

      let labelText = node.label || node.type;
      if (labelText.length > 17) labelText = labelText.substring(0, 15) + '..';
      text.textContent = labelText;
      g.appendChild(text);

      // Click to inspect
      g.addEventListener('click', (e) => {
        e.stopPropagation();
        this.inspectAstNode(node);
      });

      rootGroup.appendChild(g);

      const children = node.children || [];
      for (const child of children) {
        drawNodes(child);
      }
    };
    drawNodes(astNode);

    this.updateAstTransform();
  },

  inspectAstNode(node) {
    const detailsContainer = document.getElementById('astNodeDetails');
    const copy = { ...node };
    delete copy._x;
    delete copy._y;

    let html = `<div style="margin-bottom: 4px;"><strong>Node Type:</strong> <span style="color: #60A5FA;">${node.type}</span></div>`;
    if (node.category) html += `<div><strong>Category:</strong> ${node.category}</div>`;
    if (node.line) html += `<div><strong>Source Location:</strong> Line ${node.line}, Col ${node.column || 1}</div>`;
    if (node.name) html += `<div><strong>Identifier:</strong> <span style="color: #FCD34D;">${node.name}</span></div>`;
    if (node.value !== undefined) html += `<div><strong>Value:</strong> <span style="color: #34D399;">${node.value}</span> (${node.val_type})</div>`;
    if (node.op) html += `<div><strong>Operator:</strong> <span style="color: #F472B6;">${node.op}</span></div>`;
    html += `<div><strong>Sub-tree Nodes:</strong> ${(node.children || []).length} direct children</div>`;

    detailsContainer.innerHTML = html;
  },

  // ---------------- AUTOMATA VISUALIZATION ----------------

  initDfaEvents() {
    const selector = document.getElementById('dfaSelector');
    selector.addEventListener('change', () => this.loadSelectedDfa(selector.value));

    const btnTest = document.getElementById('btnRunDfaTest');
    btnTest.addEventListener('click', () => this.runDfaSimulation());

    const inputTest = document.getElementById('dfaTestInput');
    inputTest.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.runDfaSimulation();
    });
  },

  async loadSelectedDfa(dfaId = 'identifier') {
    try {
      const res = await API.getAutomata();
      const dfas = res.automata || [];
      this.currentDfa = dfas.find(d => d.id === dfaId || d.id === `${dfaId}_dfa`) || dfas[0];
      if (this.currentDfa) {
        this.renderDfaGraph(this.currentDfa);
        this.renderDfaFormalTuple(this.currentDfa);
        this.renderDfaTransitionTable(this.currentDfa);
      }
    } catch (err) {
      console.error('Failed to load DFA:', err);
    }
  },

  renderDfaFormalTuple(dfa) {
    const container = document.getElementById('dfaFormalDetails');
    const t = dfa.formal_tuple;
    container.innerHTML = `
      <div><strong>Q (States):</strong> { ${t.Q.join(', ')} }</div>
      <div><strong>Σ (Alphabet):</strong> { ${t.Sigma.join(', ')} }</div>
      <div><strong>q₀ (Start State):</strong> ${t.q0}</div>
      <div><strong>F (Accepting States):</strong> { ${t.F.join(', ')} }</div>
      <div style="margin-top: 4px; color: #9CA3AF;">${dfa.description}</div>
    `;
  },

  renderDfaGraph(dfa, activeState = null) {
    const svg = document.getElementById('dfaSvgCanvas');
    const positions = dfa.layout_positions || {};
    const edges = (dfa.transitions && dfa.transitions.edges) || [];
    const acceptStates = new Set(dfa.accept_states || []);

    let edgesSvg = '';
    for (const edge of edges) {
      const fromPos = positions[edge.from];
      const toPos = positions[edge.to];
      if (!fromPos || !toPos) continue;

      if (edge.from === edge.to) {
        // Self-loop
        const x = fromPos.x;
        const y = fromPos.y - 24;
        edgesSvg += `
          <path d="M ${x - 12} ${y} A 16 16 0 1 1 ${x + 12} ${y}" fill="none" stroke="#4B5563" stroke-width="1.8" marker-end="url(#dfaArrow)"/>
          <text x="${x}" y="${y - 18}" fill="#9CA3AF" font-family="Fira Code, monospace" font-size="10" text-anchor="middle">${edge.label}</text>
        `;
      } else {
        // Directed edge
        const dx = toPos.x - fromPos.x;
        const dy = toPos.y - fromPos.y;
        const angle = Math.atan2(dy, dx);
        const radius = 24;
        const startX = fromPos.x + radius * Math.cos(angle);
        const startY = fromPos.y + radius * Math.sin(angle);
        const endX = toPos.x - (radius + 6) * Math.cos(angle);
        const endY = toPos.y - (radius + 6) * Math.sin(angle);

        const midX = (startX + endX) / 2;
        const midY = (startY + endY) / 2 - 8;

        edgesSvg += `
          <line x1="${startX}" y1="${startY}" x2="${endX}" y2="${endY}" stroke="#4B5563" stroke-width="1.8" marker-end="url(#dfaArrow)"/>
          <text x="${midX}" y="${midY}" fill="#9CA3AF" font-family="Fira Code, monospace" font-size="10.5" text-anchor="middle">${edge.label}</text>
        `;
      }
    }

    let statesSvg = '';
    for (const stateId of dfa.states) {
      const pos = positions[stateId] || { x: 100, y: 100 };
      const isStart = stateId === dfa.start_state;
      const isAccept = acceptStates.has(stateId);
      const isActive = stateId === activeState;

      let stateFill = '#161B22';
      let stateStroke = isAccept ? '#22C55E' : '#3B82F6';
      let strokeWidth = '2';

      if (isActive) {
        stateFill = isAccept ? 'rgba(34, 197, 94, 0.25)' : 'rgba(59, 130, 246, 0.25)';
        stateStroke = isAccept ? '#4ADE80' : '#60A5FA';
        strokeWidth = '3.5';
      }

      let startArrow = '';
      if (isStart) {
        startArrow = `
          <line x1="${pos.x - 45}" y1="${pos.y}" x2="${pos.x - 26}" y2="${pos.y}" stroke="#60A5FA" stroke-width="2" marker-end="url(#dfaArrowStart)"/>
          <text x="${pos.x - 52}" y="${pos.y + 4}" fill="#60A5FA" font-size="10" font-family="Fira Code" text-anchor="end">start</text>
        `;
      }

      let doubleRing = '';
      if (isAccept) {
        doubleRing = `<circle cx="${pos.x}" cy="${pos.y}" r="28" fill="none" stroke="${stateStroke}" stroke-width="1.5" stroke-dasharray="3,2"/>`;
      }

      const label = (dfa.state_labels && dfa.state_labels[stateId]) || stateId;

      statesSvg += `
        ${startArrow}
        ${doubleRing}
        <circle cx="${pos.x}" cy="${pos.y}" r="24" fill="${stateFill}" stroke="${stateStroke}" stroke-width="${strokeWidth}"/>
        <text x="${pos.x}" y="${pos.y + 4}" fill="#E5E7EB" font-family="Fira Code, monospace" font-size="11" font-weight="600" text-anchor="middle">${stateId}</text>
        <text x="${pos.x}" y="${pos.y + 42}" fill="#9CA3AF" font-family="Inter, sans-serif" font-size="10" text-anchor="middle">${label}</text>
      `;
    }

    svg.innerHTML = `
      <defs>
        <marker id="dfaArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 0 1 L 8 5 L 0 9 z" fill="#4B5563" />
        </marker>
        <marker id="dfaArrowStart" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 0 1 L 8 5 L 0 9 z" fill="#60A5FA" />
        </marker>
      </defs>
      ${edgesSvg}
      ${statesSvg}
    `;
  },

  renderDfaTransitionTable(dfa) {
    const container = document.getElementById('transitionTableContainer');
    const table = dfa.transition_table || {};
    const states = Object.keys(table);
    if (states.length === 0) {
      container.innerHTML = '<p class="empty-state">No transition table available.</p>';
      return;
    }

    const alphabetSymbols = Object.keys(table[states[0]] || {});

    let html = `
      <table class="data-table">
        <thead>
          <tr>
            <th>Current State (q)</th>
            ${alphabetSymbols.map(sym => `<th>Input: ${sym}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
    `;

    for (const state of states) {
      const isStart = state === dfa.start_state;
      const isAccept = (dfa.accept_states || []).includes(state);
      const prefix = isStart ? '→ ' : (isAccept ? '* ' : '');

      html += `<tr><td><strong>${prefix}${state}</strong></td>`;
      for (const sym of alphabetSymbols) {
        const nextState = table[state][sym] || '-';
        html += `<td>${nextState}</td>`;
      }
      html += '</tr>';
    }

    html += '</tbody></table>';
    container.innerHTML = html;
  },

  async runDfaSimulation() {
    const inputStr = document.getElementById('dfaTestInput').value;
    const dfaId = document.getElementById('dfaSelector').value;
    const simHeader = document.getElementById('simHeader');
    const simSteps = document.getElementById('simStepsList');

    simHeader.innerHTML = '<span style="color: #60A5FA;">Simulating DFA state transitions...</span>';
    simSteps.innerHTML = '';

    try {
      const res = await API.testAutomata(dfaId, inputStr);
      const result = res.result;

      let idx = 0;
      const runStep = () => {
        if (idx < result.steps.length) {
          const step = result.steps[idx];
          this.renderDfaGraph(this.currentDfa, step.to_state);

          const stepElem = document.createElement('div');
          const isFinal = idx === result.steps.length - 1;
          const statusClass = isFinal ? (result.accepted ? 'accepted' : 'trapped') : '';
          stepElem.className = `sim-step-item ${statusClass}`;
          stepElem.innerHTML = `
            <strong>Step ${step.step}:</strong> 
            <span>Read '${step.char}'</span> 
            <span>→ State: <strong>${step.to_state}</strong></span>
            <span style="color: #9CA3AF;">(${step.action})</span>
          `;
          simSteps.appendChild(stepElem);
          simSteps.scrollTop = simSteps.scrollHeight;

          idx++;
          setTimeout(runStep, 350);
        } else {
          // Final summary
          if (result.accepted) {
            simHeader.innerHTML = `
              <span style="color: #22C55E; font-weight: 700;">✓ ACCEPTED</span>: 
              String '${result.input}' successfully recognized as token <strong>${result.token_produced}</strong> in state <strong>${result.final_state}</strong>.
            `;
          } else {
            simHeader.innerHTML = `
              <span style="color: #EF4444; font-weight: 700;">✗ REJECTED</span>: 
              String '${result.input}' failed in state <strong>${result.final_state}</strong> (Not in F).
            `;
          }
        }
      };

      runStep();

    } catch (err) {
      simHeader.innerHTML = `<span style="color: #EF4444;">Simulation error: ${err.message}</span>`;
    }
  }
};
