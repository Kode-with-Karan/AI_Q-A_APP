import React, { useState } from 'react'

export default function App(){
  const [file, setFile] = useState(null)
  const [uploadResult, setUploadResult] = useState(null)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [asking, setAsking] = useState(false)
  const [uploadedId, setUploadedId] = useState(null)
  const [uploadedText, setUploadedText] = useState('')
  const [showFullText, setShowFullText] = useState(false)

  const upload = async () => {
    if(!file) return
    if(!isSupported(file)){
      setUploadResult({ error: 'Unsupported file type. Please upload PDF or audio/video.' })
      return
    }
    setUploading(true)
    const fd = new FormData()
    fd.append('file', file)
    try {
      const res = await fetch('/api/upload', {method:'POST', body: fd})
      if (!res.ok) {
        const txt = await res.text()
        setUploadResult({ error: txt || `Upload failed: ${res.status}` })
        return
      }
      const j = await res.json().catch(async () => ({ error: await res.text() }))
      setUploadResult(j)
      if (j && j.id) {
        setUploadedId(j.id)
      }
      if (j && j.text) {
        setUploadedText(j.text)
      }
    } catch (err) {
      setUploadResult({ error: String(err) })
    } finally { setUploading(false) }
  }

  const isSupported = (f) => {
    if(!f) return false
    const t = (f.type || '').toLowerCase()
    const name = (f.name || f.filename || '').toLowerCase()
    if(t.startsWith('audio') || t.startsWith('video')) return true
    if(name.endsWith('.pdf')) return true
    return false
  }

  const ask = async () => {
    if(!question) return
    setAsking(true)
    try {
      const body = { question }
      if (uploadedId) body.doc_id = uploadedId
      const res = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)})
      if (!res.ok) {
        const txt = await res.text()
        setAnswer(`Error: ${txt || res.status}`)
        return
      }
      const j = await res.json().catch(async () => ({ answer: await res.text() }))
      setAnswer(j.answer)
    } catch (err) {
      setAnswer(String(err))
    } finally { setAsking(false) }
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <header className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          {/* <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-500 flex items-center justify-center text-white font-bold shadow-lg">AI</div> */}
          <div>
            <h1 className="text-2xl font-extrabold">AI Q&A App</h1>
            <p className="text-sm text-slate-500">Upload content and ask questions — powered by your backend AI.</p>
          </div>
        </div>
        <nav className="text-sm text-slate-600">
          <a className="px-3 py-2 hover:bg-slate-100 rounded-md" href="#features">Features</a>
          <a className="px-3 py-2 hover:bg-slate-100 rounded-md" href="#try">Try</a>
        </nav>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2 bg-white rounded-2xl p-6 shadow">
          <h2 className="text-lg font-semibold mb-2">Ask your AI</h2>
          <p className="text-sm text-slate-500 mb-4">Type a question related to your uploaded content and get concise answers with references.</p>

            <div className="flex gap-3">
            <input
              value={question}
              onChange={e=>setQuestion(e.target.value)}
              placeholder="Ask anything about the uploaded document"
              className="flex-1 rounded-lg border border-slate-200 p-3 shadow-sm focus:ring-2 focus:ring-indigo-300 focus:outline-none"
            />
            <button onClick={ask} disabled={asking} className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg shadow">
              {asking ? 'Asking…' : 'Ask'}
            </button>
          </div>

          <div className="mt-6">
            {answer ? (
              <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
                <h3 className="font-medium mb-2">Answer</h3>
                <div className="prose max-w-none text-slate-700">{answer}</div>
              </div>
            ) : (
              <div className="text-sm text-slate-400">No answer yet — ask a question to get started.</div>
            )}
          </div>
        </section>

        <aside className="bg-white rounded-2xl p-6 shadow flex flex-col gap-4">
          <div>
            <h3 className="font-semibold">Upload</h3>
            <p className="text-sm text-slate-500">Drop a file (PDF, txt, audio) to make it available for querying.</p>
          </div>

          <div>
            <div
              className="border-dashed border-2 border-slate-200 rounded-lg p-4 flex flex-col gap-3"
              onDragOver={(e)=>e.preventDefault()}
              onDrop={(e)=>{ e.preventDefault(); const f = e.dataTransfer.files && e.dataTransfer.files[0]; if(f){ setFile(f); setUploadResult(null) } }}
            >
              <div className="flex items-center gap-3 w-full">
                <input accept="application/pdf,audio/*,video/*" type="file" id="file" onChange={e=>{ setFile(e.target.files[0]); setUploadResult(null) }} className="text-sm flex-1 min-w-0" />
                <button onClick={upload} disabled={uploading || !file || !isSupported(file)} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-md shadow">
                  {uploading ? 'Uploading…' : 'Upload'}
                </button>
              </div>

              <div className="text-xs text-slate-400">Supported: PDF, audio (mp3/wav), video. Or drag & drop a file here.</div>

              {file && (
                <div className="text-sm">
                  <strong>Selected:</strong> {file.name} {isSupported(file) ? (<span className="text-emerald-600">(OK)</span>) : (<span className="text-rose-600">(Unsupported)</span>)}
                </div>
              )}

              {uploadResult && (
                <div className="mt-2 text-sm text-slate-700">
                  {uploadResult.error ? (
                    <div className="text-rose-600">{uploadResult.error}</div>
                  ) : (
                    <div>
                      <div className="flex items-center justify-between">
                        <div><strong>Uploaded:</strong> {uploadResult.filename} <span className="text-slate-400">(id: {uploadResult.id})</span></div>
                        <div className="text-xs text-slate-500">{uploadedId ? 'Ready for chat' : ''}</div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {uploadedText && (
              <div className="mt-3 bg-white p-3 rounded shadow-sm">
                <div className="flex items-start justify-between">
                  <strong>Extracted text preview</strong>
                  <button className="text-xs text-indigo-600" onClick={()=>setShowFullText(s=>!s)}>{showFullText ? 'Show less' : 'Show more'}</button>
                </div>
                <div className="mt-2 text-sm text-slate-700 max-h-40 overflow-auto">
                  {showFullText ? uploadedText : (uploadedText.length > 600 ? uploadedText.slice(0,600) + '…' : uploadedText)}
                </div>
              </div>
            )}
          </div>

          <div className="mt-4 text-xs text-slate-400">Tip: For best results, upload the main document before asking questions.</div>
        </aside>
      </main>

      <footer className="mt-10 text-center text-sm text-slate-500">
        Built with care — connect to your backend at <span className="font-mono">/api</span>
      </footer>
    </div>
  )
}
