/**
 * editor.js - Custom CodeSnap Code Editor with Syntax Highlighting and Line Numbers
 */

class CodeEditor {
  constructor(editorElemId, gutterElemId, highlightElemId) {
    this.editor = document.getElementById(editorElemId);
    this.gutter = document.getElementById(gutterElemId);
    this.highlight = document.getElementById(highlightElemId);
    this.cursorPosElem = document.getElementById('cursorPos');
    this.charCountElem = document.getElementById('charCount');
    this.lineCountElem = document.getElementById('lineCount');

    this.keywords = new Set([
      'START', 'STOP', 'LET', 'PRINT', 'IF', 'ELSE', 'WHILE', 'FOR',
      'TO', 'STEP', 'END', 'TRUE', 'FALSE', 'AND', 'OR', 'NOT'
    ]);

    this.init();
  }

  init() {
    this.editor.addEventListener('input', () => this.onInput());
    this.editor.addEventListener('scroll', () => this.syncScroll());
    this.editor.addEventListener('keydown', (e) => this.onKeyDown(e));
    this.editor.addEventListener('keyup', () => this.updateCursorStatus());
    this.editor.addEventListener('click', () => this.updateCursorStatus());

    this.onInput();
  }

  getValue() {
    return this.editor.value;
  }

  setValue(code) {
    this.editor.value = code;
    this.onInput();
  }

  onInput() {
    const text = this.editor.value;
    this.updateLineNumbers(text);
    this.renderHighlighting(text);
    this.updateCursorStatus();
    this.syncScroll();
  }

  syncScroll() {
    this.gutter.scrollTop = this.editor.scrollTop;
    const highlightDisplay = document.getElementById('highlightDisplay');
    if (highlightDisplay) {
      highlightDisplay.scrollTop = this.editor.scrollTop;
      highlightDisplay.scrollLeft = this.editor.scrollLeft;
    }
  }

  updateLineNumbers(text) {
    const lines = text.split('\n');
    const count = lines.length;
    let numbersHtml = '';
    for (let i = 1; i <= count; i++) {
      numbersHtml += `${i}<br>`;
    }
    this.gutter.innerHTML = numbersHtml;
    if (this.lineCountElem) this.lineCountElem.textContent = `${count} lines`;
    if (this.charCountElem) this.charCountElem.textContent = `${text.length} characters`;
  }

  updateCursorStatus() {
    const pos = this.editor.selectionStart;
    const text = this.editor.value.substring(0, pos);
    const lines = text.split('\n');
    const currentLine = lines.length;
    const currentCol = lines[lines.length - 1].length + 1;
    if (this.cursorPosElem) {
      this.cursorPosElem.textContent = `Ln ${currentLine}, Col ${currentCol}`;
    }
  }

  onKeyDown(e) {
    // 1. Tab key handling: insert 4 spaces
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = this.editor.selectionStart;
      const end = this.editor.selectionEnd;
      const spaces = '    ';
      this.editor.value = this.editor.value.substring(0, start) + spaces + this.editor.value.substring(end);
      this.editor.selectionStart = this.editor.selectionEnd = start + 4;
      this.onInput();
      return;
    }

    // 2. Enter key handling: auto-indent
    if (e.key === 'Enter') {
      const pos = this.editor.selectionStart;
      const textBefore = this.editor.value.substring(0, pos);
      const lines = textBefore.split('\n');
      const currentLineText = lines[lines.length - 1];

      // Match leading whitespace
      const matchIndent = currentLineText.match(/^(\s*)/);
      let indent = matchIndent ? matchIndent[1] : '';

      // Check if current line starts a block requiring indentation increase
      const trimmed = currentLineText.trim();
      if (
        trimmed.startsWith('START') ||
        trimmed.startsWith('IF') ||
        trimmed.startsWith('WHILE') ||
        trimmed.startsWith('FOR') ||
        trimmed.startsWith('ELSE')
      ) {
        indent += '    ';
      }

      // If pressing enter right before 'END' or 'STOP' or 'ELSE', reduce indent if applicable
      e.preventDefault();
      const textAfter = this.editor.value.substring(pos);
      const insertion = '\n' + indent;
      this.editor.value = textBefore + insertion + textAfter;
      this.editor.selectionStart = this.editor.selectionEnd = pos + insertion.length;
      this.onInput();
    }
  }

  renderHighlighting(source) {
    const escaped = this.escapeHtml(source);
    // Regex tokenizer for CodeSnap syntax highlighting
    const tokenRegex = /(#.*$)|("(?:[^"\\]|\\.)*")|(\b(?:START|STOP|LET|PRINT|IF|ELSE|WHILE|FOR|TO|STEP|END|AND|OR|NOT)\b)|(\b(?:TRUE|FALSE)\b)|(\b\d+(?:\.\d+)?\b)|(==|!=|<=|>=|[+\-*\/%<>=])|(\b[a-zA-Z_]\w*\b)/gm;

    const highlighted = escaped.replace(tokenRegex, (match, comment, string, keyword, boolean, number, operator, identifier) => {
      if (comment) return `<span class="tok-comm">${comment}</span>`;
      if (string) return `<span class="tok-str">${string}</span>`;
      if (keyword) return `<span class="tok-kw">${keyword}</span>`;
      if (boolean) return `<span class="tok-bool">${boolean}</span>`;
      if (number) return `<span class="tok-num">${number}</span>`;
      if (operator) return `<span class="tok-op">${operator}</span>`;
      if (identifier) return `<span class="tok-ident">${identifier}</span>`;
      return match;
    });

    this.highlight.innerHTML = highlighted + '\n';
  }

  escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  formatCode() {
    const lines = this.editor.value.split('\n');
    let indentLevel = 0;
    const formatted = [];

    for (let rawLine of lines) {
      let line = rawLine.trim();
      if (!line) {
        formatted.push('');
        continue;
      }

      // Decrease indent before printing closing keywords
      if (line.startsWith('STOP') || line.startsWith('END') || line.startsWith('ELSE')) {
        indentLevel = Math.max(0, indentLevel - 1);
      }

      const indentStr = '    '.repeat(indentLevel);
      formatted.push(indentStr + line);

      // Increase indent after block opening keywords
      if (
        line.startsWith('START') ||
        line.startsWith('IF') ||
        line.startsWith('WHILE') ||
        line.startsWith('FOR') ||
        line.startsWith('ELSE')
      ) {
        indentLevel++;
      }
    }

    this.setValue(formatted.join('\n'));
  }
}
