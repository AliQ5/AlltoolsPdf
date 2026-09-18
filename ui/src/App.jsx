import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileImage, Image as ImageIcon, FileMinus, RefreshCw,
  FileText, FileSpreadsheet, Presentation, ChevronRight,
  ChevronLeft, Upload, CheckCircle, AlertCircle, Loader,
  Scissors, Crop, Maximize, RotateCw, Settings, FilePlus2, 
  Split, Trash2, Key, Unlock, Palette, Layers, Grid
} from 'lucide-react';

const CATEGORIES = [
  {
    id: 'video',
    label: 'Video Tools',
    tools: [
      { id: 'cropVideo', title: 'Crop Video', desc: 'Crop video area', icon: Crop, inputs: ['x1', 'y1', 'x2', 'y2'] },
      { id: 'trimVideo', title: 'Trim Video', desc: 'Cut video duration', icon: Scissors, inputs: ['start_sec', 'end_sec'] },
    ]
  },
  {
    id: 'img',
    label: 'Image Tools',
    tools: [
      { id: 'gifMaker', title: 'GIF Maker', desc: 'Create GIF from images', icon: ImageIcon, multiFile: true, inputs: ['duration'] },
      { id: 'resizeImg', title: 'Resize Image', desc: 'Change dimensions', icon: Maximize, inputs: ['width', 'height'] },
      { id: 'cropImg', title: 'Crop Image', desc: 'Crop image area', icon: Crop, inputs: ['left', 'top', 'right', 'bottom'] },
      { id: 'rotateImg', title: 'Rotate Image', desc: 'Rotate in degrees', icon: RotateCw, inputs: ['degrees'] },
      { id: 'flipImg', title: 'Flip Image', desc: 'Flip horizontal/vertical', icon: RefreshCw, inputs: ['direction (horizontal/vertical)'] },
      { id: 'enlargeImg', title: 'Image Enlarger', desc: 'Scale image size', icon: Maximize, inputs: ['scale (e.g. 2.0)'] },
      { id: 'convertImg', title: 'Convert Image', desc: 'Change format', icon: RefreshCw, inputs: ['format'] },
    ]
  },
  {
    id: 'pdf',
    label: 'PDF Tools',
    tools: [
      { id: 'mergePdf', title: 'PDF Merge', desc: 'Combine PDFs', icon: FilePlus2, multiFile: true },
      { id: 'splitPdf', title: 'PDF Split', desc: 'Split into pages', icon: Split, folderOut: true },
      { id: 'flattenPdf', title: 'Flatten PDF', desc: 'Flatten form fields', icon: Layers },
      { id: 'resizePdf', title: 'Resize PDF', desc: 'Resize page dimensions', icon: Maximize, inputs: ['width_pt', 'height_pt'] },
      { id: 'unlockPdf', title: 'Unlock PDF', desc: 'Remove password', icon: Unlock, inputs: ['password'] },
      { id: 'protectPdf', title: 'Protect PDF', desc: 'Add password', icon: Key, inputs: ['password'] },
      { id: 'rotatePdf', title: 'Rotate PDF', desc: 'Rotate pages', icon: RotateCw, inputs: ['degrees'] },
      { id: 'cropPdf', title: 'Crop PDF', desc: 'Crop page margins', icon: Crop, inputs: ['left_pct', 'top_pct', 'right_pct', 'bottom_pct'] },
      { id: 'organizePdf', title: 'Organize PDF', desc: 'Reorder pages', icon: Grid, inputs: ['page_order (e.g. 1,3,2)'] },
      { id: 'removePages', title: 'PDF Page Remover', desc: 'Remove pages', icon: Trash2, inputs: ['pages_to_remove (e.g. 1,4)'] },
      { id: 'extractPages', title: 'Extract Pages', desc: 'Extract specific pages', icon: FileMinus, inputs: ['page_ranges (e.g. 1-3,5)'] },
      { id: 'extractImgPdf', title: 'Extract Images', desc: 'Extract images from PDF', icon: ImageIcon, folderOut: true },
      { id: 'img2pdf', title: 'Image to PDF', desc: 'Convert images to PDF', icon: FileImage, multiFile: true },
      { id: 'pdf2img', title: 'PDF to Image', desc: 'Convert PDF to PNGs', icon: ImageIcon, folderOut: true },
      { id: 'compress', title: 'Compress PDF', desc: 'Reduce file size', icon: FileMinus },
    ]
  },
  {
    id: 'office2pdf',
    label: 'Office → PDF',
    tools: [
      { id: 'word2pdf', title: 'Word to PDF', desc: 'Convert .docx to PDF', icon: FileText },
      { id: 'excel2pdf', title: 'Excel to PDF', desc: 'Convert .xlsx to PDF', icon: FileSpreadsheet },
      { id: 'ppt2pdf', title: 'PPT to PDF', desc: 'Convert .pptx to PDF', icon: Presentation },
    ]
  },
  {
    id: 'pdf2office',
    label: 'PDF → Office',
    tools: [
      { id: 'pdf2word', title: 'PDF to Word', desc: 'Convert PDF to .docx', icon: FileText },
      { id: 'pdf2excel', title: 'PDF to Excel', desc: 'Convert PDF to .xlsx', icon: FileSpreadsheet },
      { id: 'pdf2ppt', title: 'PDF to PPT', desc: 'Convert PDF to .pptx', icon: Presentation },
    ]
  },
];

export default function App() {
  const [activeCat, setActiveCat] = useState('pdf');
  const [activeTool, setActiveTool] = useState(null);
  const [inputs, setInputs] = useState({});
  const [toast, setToast] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const api = window.pywebview?.api;

  const showToast = (type, msg) => {
    setToast({ type, msg });
    setTimeout(() => setToast(null), 3500);
  };

  const call = async (fn, ...args) => {
    if (!api) { showToast('error', 'Not running inside app.'); return; }
    showToast('loading', 'Working…');
    try {
      const res = await fn(...args);
      if (res?.success === false) showToast('error', res.msg);
      else showToast('success', res?.msg || 'Done!');
    } catch (e) {
      showToast('error', String(e));
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    // In pywebview, we cannot easily read absolute file paths from HTML5 drag and drop directly due to browser security.
    // However, some versions of pywebview allow e.dataTransfer.files[0].path. 
    // If that's unavailable, we'll prompt the user to use the button.
    const files = Array.from(e.dataTransfer.files);
    if (!files.length) return;
    
    const filePaths = files.map(f => f.path || f.name).filter(Boolean);
    if (!filePaths[0] || filePaths[0] === files[0].name) {
      // `.path` is undefined (browser security), we can't do D&D.
      showToast('error', 'Drag & drop not fully supported in this renderer. Please click the button to select files.');
      return;
    }
    
    // If we have full paths, execute
    if (activeTool) {
      executeTool(filePaths);
    } else {
      showToast('error', 'Please select a tool first before dropping files.');
    }
  };

  const runWithDialog = async () => {
    if (!api) { showToast('error', 'Not running inside app.'); return; }
    
    let paths = [];
    if (activeTool.multiFile) {
      paths = await api.select_files(['*.*']);
    } else {
      const p = await api.select_file('*.*');
      if (p) paths = [p];
    }
    
    if (paths && paths.length > 0) {
      executeTool(paths);
    }
  };

  const executeTool = async (filePaths) => {
    if (!api) return;
    
    let folder = null;
    if (activeTool.folderOut) {
      folder = await api.select_folder();
      if (!folder) return;
    }

    const pathArgs = activeTool.multiFile ? [filePaths] : [filePaths[0]];
    const extraArgs = (activeTool.inputs || []).map(inp => inputs[inp]);
    
    if (folder) extraArgs.push(folder);

    switch (activeTool.id) {
      case 'cropVideo': call(api.run_crop_video, ...pathArgs, ...extraArgs); break;
      case 'trimVideo': call(api.run_trim_video, ...pathArgs, ...extraArgs); break;
      case 'gifMaker': call(api.run_make_gif, ...pathArgs, ...extraArgs); break;
      case 'resizeImg': call(api.run_resize_image, ...pathArgs, ...extraArgs); break;
      case 'cropImg': call(api.run_crop_image, ...pathArgs, ...extraArgs); break;
      case 'rotateImg': call(api.run_rotate_image, ...pathArgs, ...extraArgs); break;
      case 'flipImg': call(api.run_flip_image, ...pathArgs, ...extraArgs); break;
      case 'enlargeImg': call(api.run_enlarge_image, ...pathArgs, ...extraArgs); break;
      case 'convertImg': call(api.run_img_convert, ...pathArgs, ...extraArgs); break;
      
      case 'mergePdf': call(api.run_merge_pdfs, ...pathArgs); break;
      case 'splitPdf': call(api.run_split_pdf, ...pathArgs, folder); break;
      case 'flattenPdf': call(api.run_flatten_pdf, ...pathArgs); break;
      case 'resizePdf': call(api.run_resize_pdf, ...pathArgs, ...extraArgs); break;
      case 'unlockPdf': call(api.run_unlock_pdf, ...pathArgs, ...extraArgs); break;
      case 'protectPdf': call(api.run_protect_pdf, ...pathArgs, ...extraArgs); break;
      case 'rotatePdf': call(api.run_rotate_pdf, ...pathArgs, ...extraArgs); break;
      case 'cropPdf': call(api.run_crop_pdf, ...pathArgs, ...extraArgs); break;
      case 'organizePdf': call(api.run_organize_pdf, ...pathArgs, ...extraArgs); break;
      case 'removePages': call(api.run_remove_pages, ...pathArgs, ...extraArgs); break;
      case 'extractPages': call(api.run_extract_pages, ...pathArgs, ...extraArgs); break;
      case 'extractImgPdf': call(api.run_extract_images_from_pdf, ...pathArgs, folder); break;
      case 'img2pdf': call(api.run_img_to_pdf, ...pathArgs); break;
      case 'pdf2img': call(api.run_pdf_to_img, ...pathArgs, folder); break;
      case 'compress': call(api.run_compress_pdf, ...pathArgs); break;
      
      case 'word2pdf': call(api.run_word_to_pdf, ...pathArgs); break;
      case 'excel2pdf': call(api.run_excel_to_pdf, ...pathArgs); break;
      case 'ppt2pdf': call(api.run_ppt_to_pdf, ...pathArgs); break;
      case 'pdf2word': call(api.run_pdf_to_word, ...pathArgs); break;
      case 'pdf2excel': call(api.run_pdf_to_excel, ...pathArgs); break;
      case 'pdf2ppt': call(api.run_pdf_to_ppt, ...pathArgs); break;
      default: break;
    }
  };

  const currentCat = CATEGORIES.find(c => c.id === activeCat);

  return (
    <div 
      className="app-shell"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {isDragging && (
        <div className="drag-overlay">
          <div className="drag-content">
            <Upload size={48} />
            <h2>Drop files here</h2>
            <p>Will process using {activeTool ? activeTool.title : 'selected tool'}</p>
          </div>
        </div>
      )}

      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-dot" />
          <span className="brand-name">AllTools</span>
        </div>
        <nav className="sidebar-nav">
          {CATEGORIES.map(cat => (
            <button
              key={cat.id}
              className={`nav-item ${activeCat === cat.id ? 'active' : ''}`}
              onClick={() => { setActiveCat(cat.id); setActiveTool(null); }}
            >
              {cat.label}
            </button>
          ))}
        </nav>
        <div style={{ marginTop: 'auto', padding: '1rem', fontSize: '0.75rem', color: '#64748b', textAlign: 'center' }}>
          Built by Ali Qureshi
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="main-area">
        {/* Toast */}
        <AnimatePresence>
          {toast && (
            <motion.div
              initial={{ opacity: 0, y: -12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              className={`toast toast-${toast.type}`}
            >
              {toast.type === 'loading' && <Loader className="toast-icon spin" size={15} />}
              {toast.type === 'success' && <CheckCircle className="toast-icon" size={15} />}
              {toast.type === 'error' && <AlertCircle className="toast-icon" size={15} />}
              <span>{toast.msg}</span>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence mode="wait">
          {!activeTool ? (
            <motion.div key={activeCat} className="content">
              <div className="content-header">
                <h1 className="content-title">{currentCat.label}</h1>
                <p className="content-sub">{currentCat.tools.length} tools available</p>
              </div>
              <div className="tool-grid">
                {currentCat.tools.map((tool, i) => (
                  <motion.button
                    key={tool.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.02 }}
                    className="tool-card"
                    onClick={() => setActiveTool(tool)}
                  >
                    <div className="tool-card-icon"><tool.icon size={22} /></div>
                    <div className="tool-card-body">
                      <p className="tool-card-title">{tool.title}</p>
                      <p className="tool-card-desc">{tool.desc}</p>
                    </div>
                    <ChevronRight size={16} className="tool-card-arrow" />
                  </motion.button>
                ))}
              </div>
            </motion.div>
          ) : (
            <motion.div key={activeTool.id} className="content">
              <button className="back-btn" onClick={() => setActiveTool(null)}>
                <ChevronLeft size={16} /> Back
              </button>

              <div className="detail-card">
                <div className="detail-icon"><activeTool.icon size={28} /></div>
                <h2 className="detail-title">{activeTool.title}</h2>
                <p className="detail-desc">{activeTool.desc}</p>

                {activeTool.inputs && (
                  <div className="inputs-grid">
                    {activeTool.inputs.map(inp => (
                      <div key={inp} className="input-group">
                        <label>{inp}</label>
                        <input 
                          type="text" 
                          placeholder={inp}
                          onChange={(e) => setInputs(prev => ({...prev, [inp]: e.target.value}))}
                        />
                      </div>
                    ))}
                  </div>
                )}

                <div className="drag-box" onClick={runWithDialog}>
                  <Upload size={32} style={{marginBottom: 10}} />
                  <p>Click to browse or Drag & Drop file(s) here</p>
                  <small>{activeTool.multiFile ? 'Multiple files allowed' : 'Single file allowed'}</small>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
