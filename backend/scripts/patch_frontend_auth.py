from pathlib import Path
p = Path('..\\frontend\\index.html')
text = p.read_text(encoding='utf-8')
if 'function requireAuth' not in text:
    text = text.replace(
        '    let authToken = null;\n    let userId = null;\n\n    function showPage(pageId) {',
        '    let authToken = null;\n    let userId = null;\n    let loginPromptShown = false;\n\n    function requireAuth() {\n      if (!authToken || !userId) {\n        if (!loginPromptShown) {\n          loginPromptShown = true;\n          const tokenEl = document.getElementById(\'token\');\n          if (tokenEl) tokenEl.textContent = \'Please log in to continue.\';\n        }\n        return false;\n      }\n      loginPromptShown = false;\n      return true;\n    }\n\n    function handleUnauthenticated() {\n      authToken = null;\n      userId = null;\n      loginPromptShown = false;\n      const tokenEl = document.getElementById(\'token\');\n      if (tokenEl) tokenEl.textContent = \'Session expired. Please log in again.\';\n      return false;\n    }\n\n    function showPage(pageId) {'
    )

text = text.replace("if (!authToken || !userId) return alert('Login first');", 'if (!requireAuth()) return;')
text = text.replace("if (!authToken || !userId) return alert('login first');", 'if (!requireAuth()) return;')

text = text.replace(
    '  const profile = await res.json();\n      if (res.ok) {\n        userId = profile.id;\n        updateProfileUI(profile);\n      }',
    '  if (res.status === 401) {\n        return handleUnauthenticated();\n      }\n      const profile = await res.json();\n      if (res.ok) {\n        userId = profile.id;\n        updateProfileUI(profile);\n      }'
)

text = text.replace(
    '      if (pageId === \'dashboard\') refreshDashboard();',
    '      if (pageId === \'dashboard\') { if (authToken && userId) { refreshDashboard(); } else { const tokenEl = document.getElementById(\'token\'); if (tokenEl) tokenEl.textContent = \'Please log in to load dashboard.\'; } }'
)

p.write_text(text, encoding='utf-8')
print('updated index.html')
