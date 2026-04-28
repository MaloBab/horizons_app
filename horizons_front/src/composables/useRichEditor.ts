import { ref, reactive } from 'vue'
import type { Ref } from 'vue'

const HISTORY_LIMIT = 50

export function useRichEditor(editorRef: Ref<HTMLElement | null>) {
  const st = reactive({
    bold: false, italic: false, underline: false,
    strike: false, ul: false, ol: false,
  })

  const history: string[] = []
  const future:  string[] = []
  let skipHistory  = false
  let pendingColor: string | null = null
  let savedRange:   Range | null  = null
  let emitFn: ((html: string) => void) | null = null

  const activeColor = ref('#e2e8f0')

  // ── Histoire ──────────────────────────────────────────────────────────────
  const snapshot = () => {
    if (!editorRef.value || skipHistory) return
    const html = editorRef.value.innerHTML
    if (history[history.length - 1] === html) return
    history.push(html)
    if (history.length > HISTORY_LIMIT) history.shift()
    future.length = 0
  }

  const notifyChange = () => {
    snapshot()
    if (editorRef.value) emitFn?.(editorRef.value.innerHTML)
  }

  const undo = () => {
    if (history.length < 2 || !editorRef.value) return
    future.push(history.pop()!)
    skipHistory = true
    editorRef.value.innerHTML = history[history.length - 1] ?? ''
    skipHistory = false
    emitFn?.(editorRef.value.innerHTML)
  }

  const redo = () => {
    if (!future.length || !editorRef.value) return
    const next = future.pop()!
    history.push(next)
    skipHistory = true
    editorRef.value.innerHTML = next
    skipHistory = false
    emitFn?.(editorRef.value.innerHTML)
  }

  // ── Sélection ─────────────────────────────────────────────────────────────
  const ensureSelectionInEditor = () => {
    if (!editorRef.value) return
    const sel = window.getSelection()

    // Si le curseur est déjà dans l'éditeur, rien à faire
    if (
      sel && sel.rangeCount > 0 &&
      editorRef.value.contains(sel.getRangeAt(0).commonAncestorContainer)
    ) return

    // Sinon place le curseur à la fin du contenu
    const range = document.createRange()
    range.selectNodeContents(editorRef.value)
    range.collapse(false)
    sel?.removeAllRanges()
    sel?.addRange(range)
  }

  // ── Inline ────────────────────────────────────────────────────────────────
  const isWrappedBy = (tag: string): boolean => {
    const sel = window.getSelection()
    if (!sel || sel.rangeCount === 0 || sel.isCollapsed) return false
    let node: Node | null = sel.getRangeAt(0).commonAncestorContainer
    while (node && node !== editorRef.value) {
      if ((node as Element).tagName?.toLowerCase() === tag) return true
      node = node.parentNode
    }
    return false
  }

  const toggleInline = (tag: string) => {
    editorRef.value?.focus()
    const sel = window.getSelection()
    if (!sel || sel.rangeCount === 0 || sel.isCollapsed) return
    const range = sel.getRangeAt(0)

    if (isWrappedBy(tag)) {
      let node: Node | null = range.commonAncestorContainer
      while (node && (node as Element).tagName?.toLowerCase() !== tag) node = node.parentNode
      if (node) {
        const parent = node.parentNode!
        while (node.firstChild) parent.insertBefore(node.firstChild, node)
        parent.removeChild(node)
      }
    } else {
      const cmdMap: Record<string, string> = {
        strong: 'bold', em: 'italic', u: 'underline', s: 'strikeThrough',
      }
      const cmd = cmdMap[tag]
      if (cmd) {
        document.execCommand(cmd)
      } else {
        const el = document.createElement(tag)
        try {
          range.surroundContents(el)
        } catch {
          const frag = range.extractContents()
          el.appendChild(frag)
          range.insertNode(el)
        }
      }
    }
    notifyChange(); refreshState()
  }

  // ── Couleur ───────────────────────────────────────────────────────────────
  const saveSelection = () => {
    const sel = window.getSelection()
    if (sel && sel.rangeCount > 0) savedRange = sel.getRangeAt(0).cloneRange()
  }

  const applyColor = (color: string) => {
    activeColor.value = color
    const range = savedRange ?? (() => {
      const s = window.getSelection()
      return (s && s.rangeCount > 0) ? s.getRangeAt(0) : null
    })()
    if (!range || range.collapsed) { pendingColor = color; return }
    const sel = window.getSelection()
    sel?.removeAllRanges()
    sel?.addRange(range)
    document.execCommand('styleWithCSS', false, 'true')
    document.execCommand('foreColor', false, color)
    pendingColor = null
    notifyChange(); refreshState()
  }

  const onColorPickerClose = () => {
    const sel = window.getSelection()
    if (savedRange) {
      try {
        sel?.removeAllRanges()
        sel?.addRange(savedRange)
      } catch (_) {}
    }
    savedRange = null
  }

  // ── Taille ────────────────────────────────────────────────────────────────
  const applyFontSize = (em: string) => {
    editorRef.value?.focus()
    const sel = window.getSelection()
    if (!sel || sel.rangeCount === 0 || sel.isCollapsed) return
    const range = sel.getRangeAt(0)
    const frag = range.extractContents()
    frag.querySelectorAll<HTMLElement>('*').forEach(el => { el.style.fontSize = '' })
    const span = document.createElement('span')
    span.style.fontSize = em
    span.appendChild(frag)
    range.insertNode(span)
    notifyChange()
  }

  // ── Blocs ─────────────────────────────────────────────────────────────────
  const setBlock = (tag: string) => {
    editorRef.value?.focus()
    ensureSelectionInEditor()
    document.execCommand('formatBlock', false, tag)
    notifyChange(); refreshState()
  }

  // ── Listes ────────────────────────────────────────────────────────────────
  const toggleList = (type: 'ul' | 'ol') => {
    editorRef.value?.focus()
    ensureSelectionInEditor()
    document.execCommand(type === 'ul' ? 'insertUnorderedList' : 'insertOrderedList')
    notifyChange(); refreshState()
  }

  // ── Tableau ───────────────────────────────────────────────────────────────
  const insertTable = (rows: number, cols: number, header: boolean) => {
    editorRef.value?.focus()
    const cellStyle = 'border:1px solid rgba(255,255,255,.15);padding:10px 12px;min-width:80px'
    const table = document.createElement('table')
    table.style.cssText = 'border-collapse:collapse;width:100%;margin:10px 0'
    const tbody = table.createTBody()
    for (let r = 0; r < (header ? rows + 1 : rows); r++) {
      const tr = tbody.insertRow()
      for (let c = 0; c < cols; c++) {
        if (r === 0 && header) {
          const th = document.createElement('th')
          th.textContent = `En-tête ${c + 1}`
          th.setAttribute('style', `${cellStyle};background:rgba(255,255,255,.06);font-weight:600`)
          tr.appendChild(th)
        } else {
          const td = tr.insertCell()
          td.setAttribute('style', cellStyle)
          td.innerHTML = '&nbsp;'
        }
      }
    }
    const sel = window.getSelection()
    if (sel && sel.rangeCount > 0) {
      const range = sel.getRangeAt(0)
      range.collapse(false)
      range.insertNode(table)
      const p = document.createElement('p')
      p.innerHTML = '<br>'
      table.after(p)
    }
    notifyChange()
  }

  // ── Effacer la mise en forme ──────────────────────────────────────────────
  const clearFormat = () => {
    editorRef.value?.focus()
    const sel = window.getSelection()
    if (!sel || sel.rangeCount === 0 || sel.isCollapsed) return
    const range = sel.getRangeAt(0)
    const frag = range.extractContents()
    frag.querySelectorAll<HTMLElement>('*').forEach(el => el.removeAttribute('style'))
    ;['b', 'strong', 'i', 'em', 'u', 's', 'strike', 'span'].forEach(tag => {
      frag.querySelectorAll(tag).forEach(el => {
        const parent = el.parentNode; if (!parent) return
        while (el.firstChild) parent.insertBefore(el.firstChild, el)
        parent.removeChild(el)
      })
    })
    ;['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].forEach(tag => {
      frag.querySelectorAll(tag).forEach(el => {
        const p = document.createElement('p')
        while (el.firstChild) p.appendChild(el.firstChild)
        el.parentNode?.replaceChild(p, el)
      })
    })
    range.insertNode(frag)
    sel.removeAllRanges()
    notifyChange(); refreshState()
  }

  // ── État boutons ──────────────────────────────────────────────────────────
  const rgbToHex = (rgb: string) => {
    const m = rgb.match(/\d+/g)
    if (!m || m.length < 3) return activeColor.value
    return '#' + m.slice(0, 3).map(n => (+n).toString(16).padStart(2, '0')).join('')
  }

  const refreshState = () => {
    const sel = window.getSelection()
    if (!sel || sel.rangeCount === 0) return
    let node: Node | null = sel.getRangeAt(0).commonAncestorContainer
    const tags = new Set<string>()
    let detectedColor = ''
    while (node && node !== editorRef.value) {
      if (node.nodeType === Node.ELEMENT_NODE) {
        const el = node as HTMLElement
        tags.add(el.tagName.toLowerCase())
        if (!detectedColor && el.style?.color) detectedColor = el.style.color
      }
      node = node.parentNode
    }
    if (!detectedColor) {
      const container = sel.getRangeAt(0).commonAncestorContainer
      const parent = container.nodeType === Node.TEXT_NODE
        ? container.parentElement
        : container as HTMLElement
      if (parent?.style?.color) detectedColor = parent.style.color
    }
    st.bold      = tags.has('strong') || tags.has('b')
    st.italic    = tags.has('em')     || tags.has('i')
    st.underline = tags.has('u')
    st.strike    = tags.has('s')      || tags.has('strike')
    st.ul        = tags.has('ul')
    st.ol        = tags.has('ol')
    if (detectedColor) activeColor.value = rgbToHex(detectedColor)
  }

  // ── Keyboard ──────────────────────────────────────────────────────────────
  const onKeydown = (e: KeyboardEvent) => {
    if (pendingColor && e.key.length === 1 && !e.ctrlKey && !e.metaKey) {
      e.preventDefault()
      const sel = window.getSelection()
      if (sel && sel.rangeCount > 0) {
        const range = sel.getRangeAt(0)
        range.deleteContents()
        const span = document.createElement('span')
        span.style.color = pendingColor
        span.textContent = e.key
        range.insertNode(span)
        range.setStartAfter(span)
        range.collapse(true)
        sel.removeAllRanges()
        sel.addRange(range)
        pendingColor = null
        notifyChange()
      }
      return
    }

    if (e.key === 'Tab') {
      e.preventDefault()
      const sel = window.getSelection()
      if (!sel || sel.rangeCount === 0) return
      if (st.ul || st.ol) {
        document.execCommand(e.shiftKey ? 'outdent' : 'indent')
        notifyChange(); refreshState()
        return
      }
      const range = sel.getRangeAt(0)
      range.deleteContents()
      const tab = document.createTextNode('\u00a0\u00a0\u00a0\u00a0')
      range.insertNode(tab)
      range.setStartAfter(tab)
      range.collapse(true)
      sel.removeAllRanges()
      sel.addRange(range)
      notifyChange()
    }

    if (e.ctrlKey || e.metaKey) {
      if (e.key === 'z') { e.preventDefault(); undo() }
      if (e.key === 'y') { e.preventDefault(); redo() }
      if (e.key === 'b') { e.preventDefault(); toggleInline('strong') }
      if (e.key === 'i') { e.preventDefault(); toggleInline('em') }
      if (e.key === 'u') { e.preventDefault(); toggleInline('u') }
    }
  }

  const onInput = () => notifyChange()

  const init = (initialHtml: string, fn: (html: string) => void) => {
    emitFn = fn
    if (editorRef.value) {
      editorRef.value.innerHTML = initialHtml || ''
      snapshot()
    }
  }

  return {
    st, activeColor,
    init, onInput, onKeydown, refreshState,
    undo, redo,
    toggleInline, toggleList, setBlock,
    applyColor, applyFontSize, saveSelection, onColorPickerClose,
    insertTable, clearFormat,
  }
}