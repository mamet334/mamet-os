<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { open } from '@tauri-apps/plugin-dialog';
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';

  // Config Marked for Markdown
  marked.setOptions({
    breaks: true,
    gfm: true
  });

  // State untuk kolom aktif (kini untuk memilih panel mana yang tampil)
  let activeColumn = $state("kolom2");
  
  // SVG Icons
  const svgSearch = `<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>`;
  const svgBot = `<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>`;
  const svgCode = `<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`;
  const svgSettings = `<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>`;
  const svgFolder = `<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-1.22-1.8A2 2 0 0 0 7.53 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>`;

  // Konfigurasi Kolom
  const columns = [
    { id: "kolom1", label: "Pencarian Cepat", icon: svgSearch, desc: "RAG & Dokumen" },
    { id: "kolom2", label: "Asisten Pribadi", icon: svgBot, desc: "User Memory & Sub-Agent" },
    { id: "kolom3", label: "Engineer", icon: svgCode, desc: "Self-Maintenance" },
  ];

  // State percakapan per kolom
  let messages = $state<Record<string, any[]>>({
    kolom1: [],
    kolom2: [],
    kolom3: []
  });

  // State input per kolom
  let inputs = $state<Record<string, string>>({
    kolom1: "",
    kolom2: "",
    kolom3: ""
  });

  // State loading per kolom
  let loadings = $state<Record<string, boolean>>({
    kolom1: false,
    kolom2: false,
    kolom3: false
  });

  let uploading = $state(false);
  let apiKeyInput = $state("");
  let selectedAgent = $state<string | null>(null);
  let projectContextPath = $state<string | null>(null);

  // State untuk Dashboard (Settings)
  let budgetData = $state<any>(null);
  let backupsData = $state<any[]>([]);
  let loadingDashboard = $state(false);

  let userEmail = $state("default");

  let chatContainers: Record<string, HTMLElement> = {};

  async function scrollToBottom(colId: string) {
    await tick();
    if (chatContainers[colId]) {
      chatContainers[colId].scrollTop = chatContainers[colId].scrollHeight;
    }
  }

  async function loadHistory() {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/history/${userEmail}`);
      if (res.ok) {
        const historyData = await res.json();
        messages.kolom1 = historyData.kolom1 || [];
        messages.kolom2 = historyData.kolom2 || [];
        messages.kolom3 = historyData.kolom3 || [];
        
        scrollToBottom("kolom1");
        scrollToBottom("kolom2");
        scrollToBottom("kolom3");
      }
    } catch (e) {
      console.log("Histori chat kosong atau server mati.");
    }
  }

  onMount(async () => {
    userEmail = localStorage.getItem("mamet_user_email") || "default";
    await loadHistory();
  });

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
    alert("✅ Teks berhasil disalin!");
  }

  async function handleSend(columnId: string, customText?: string) {
    const textToSend = customText !== undefined ? customText : inputs[columnId];
    if (!textToSend.trim() || loadings[columnId]) return;

    // Tambah pesan user ke UI
    messages[columnId] = [...messages[columnId], { role: "user", content: textToSend }];
    scrollToBottom(columnId);
    if (customText === undefined) {
      inputs[columnId] = "";
    }
    
    loadings[columnId] = true;

    try {
      const res = await fetch("http://127.0.0.1:8000/api/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: localStorage.getItem("mamet_user_email") || "andreanastasya798@gmail.com",
          column: columnId,
          message: textToSend,
          agent: columnId === "kolom2" ? selectedAgent : null,
          project_context: columnId === "kolom2" ? projectContextPath : null
        }),
      });
      
      const data = await res.json();
      
      // Matikan flag requires_approval di pesan sebelumnya jika ini persetujuan
      if (customText && (customText.startsWith("setujui") || customText.startsWith("tolak"))) {
        const msgs = messages[columnId];
        if (msgs.length > 1) {
          msgs[msgs.length - 2].requires_approval = false;
        }
      }

      messages[columnId] = [...messages[columnId], { 
        role: "system", 
        content: data.response,
        requires_approval: data.requires_approval,
        approval_details: data.approval_details
      }];
    } catch (e) {
      messages[columnId] = [...messages[columnId], { role: "system", content: "❌ Gagal terhubung ke Kernel MAMET OS." }];
    } finally {
      loadings[columnId] = false;
      scrollToBottom(columnId);
    }
  }

  async function clearChat(columnId: string) {
    if (!confirm(`Yakin ingin menghapus riwayat obrolan di ${columnId}?`)) return;
    
    // Hapus di UI
    messages[columnId] = [];
    
    // Hapus di Backend
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/history/${userEmail}/${columnId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        console.log(`Riwayat ${columnId} berhasil dihapus dari database.`);
      }
    } catch (e) {
      console.error("Gagal menghapus riwayat di backend.", e);
    }
  }

  let activeDrawerMenu = $state<string | null>(null);
  let availableDrawers = $state<string[]>([]);

  async function openDrawerMenu(columnId: string) {
    if (activeDrawerMenu === columnId) {
      activeDrawerMenu = null;
      return;
    }
    
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/drawer/list/${userEmail}/${columnId}`);
      if (res.ok) {
        const data = await res.json();
        availableDrawers = data.drawers || [];
      }
    } catch (e) {
      console.error(e);
    }
    activeDrawerMenu = columnId;
  }

  async function saveToDrawer(columnId: string) {
    const drawerName = prompt("Masukkan nama laci untuk menyimpan obrolan ini:");
    if (!drawerName || !drawerName.trim()) return;
    
    try {
      const res = await fetch("http://127.0.0.1:8000/api/drawer/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: userEmail, column: columnId, drawer_name: drawerName.trim() })
      });
      if (res.ok) {
        messages[columnId] = [];
        activeDrawerMenu = null;
        alert(`✅ Obrolan berhasil disimpan ke Laci: ${drawerName}`);
      }
    } catch (e) {
      alert("❌ Gagal menyimpan ke laci.");
    }
  }

  async function loadFromDrawer(columnId: string, drawerName: string) {
    if (!confirm(`Tarik laci '${drawerName}' ke meja? (Meja saat ini akan dibersihkan)`)) return;
    try {
      const res = await fetch("http://127.0.0.1:8000/api/drawer/load", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: userEmail, column: columnId, drawer_name: drawerName })
      });
      if (res.ok) {
        activeDrawerMenu = null;
        await loadHistory(); // Refresh history from backend
      }
    } catch (e) {
      alert("❌ Gagal memuat dari laci.");
    }
  }

  function handleAction(columnId: string, actionType: "setujui" | "tolak", taskId?: string) {
    const commandText = taskId ? `${actionType} ${taskId}` : actionType;
    handleSend(columnId, commandText);
  }

  async function saveApiKey() {
    if (!apiKeyInput) return;
    
    // Validasi khusus OpenRouter
    if (!apiKeyInput.startsWith("sk-or-v1-")) {
      alert("❌ API Key tidak valid. Kunci OpenRouter harus diawali dengan 'sk-or-v1-'");
      return;
    }
    
    try {
      const res = await fetch("http://127.0.0.1:8000/api/provider", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: localStorage.getItem("mamet_user_email") || "andreanastasya798@gmail.com",
          name: "openrouter",
          api_key: apiKeyInput,
          priority: 1
        })
      });
      const data = await res.json();
      if (res.ok) {
        alert("API Key berhasil disimpan ke Database!");
        apiKeyInput = ""; // Kosongkan input setelah disimpan
      } else {
        alert("Gagal menyimpan: " + data.detail);
      }
    } catch (e) {
      alert("Gagal terhubung ke server Kernel");
    }
  }

  async function handleFileUpload(e: Event) {
    const target = e.target as HTMLInputElement;
    const file = target.files?.[0];
    if (!file) return;

    uploading = true;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.status === "success") {
        messages["kolom1"] = [...messages["kolom1"], {
          role: "system",
          content: `✅ Dokumen "${file.name}" berhasil diunggah. (${data.chunks} chunk, ${data.char_count} karakter)`
        }];
      } else {
        messages["kolom1"] = [...messages["kolom1"], { role: "system", content: `❌ ${data.message || "Gagal mengunggah"}` }];
      }
    } catch (error) {
      messages["kolom1"] = [...messages["kolom1"], { role: "system", content: "❌ Gagal mengunggah dokumen" }];
    } finally {
      uploading = false;
      target.value = '';
    }
  }

  async function pickProjectFolder() {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
        title: "Pilih Folder Proyek"
      });
      if (selected && typeof selected === 'string') {
        projectContextPath = selected;
      }
    } catch (error) {
      console.warn("Tauri dialog gagal (kemungkinan dijalankan di peramban Web). Fallback ke prompt.");
      const manualPath = prompt("Fitur pemilih folder otomatis hanya berjalan di aplikasi Desktop Tauri.\n\nKarena Anda mengakses via Peramban Web (Chrome/Edge), silakan masukkan path (alamat) folder proyek Anda secara manual:\n(Contoh: D:\\SLAMET\\other\\mamet-os)");
      
      if (manualPath && manualPath.trim()) {
        projectContextPath = manualPath.trim();
      }
    }
  }

  async function openDashboard() {
    activeColumn = 'setting';
    loadingDashboard = true;
    try {
      // Ambil data budget
      const bRes = await fetch(`http://127.0.0.1:8000/api/budget?email=${userEmail}`);
      budgetData = await bRes.json();
      
      // Ambil data backups
      const rRes = await fetch(`http://127.0.0.1:8000/api/backups`);
      const rData = await rRes.json();
      backupsData = rData.backups || [];
    } catch (e) {
      console.error("Gagal memuat dashboard:", e);
    } finally {
      loadingDashboard = false;
    }
  }

  async function executeRollback(filename: string) {
    if (!confirm(`Apakah Anda yakin ingin memulihkan sistem ke versi ${filename}?\nPERINGATAN: Perubahan kode setelah backup ini akan tertimpa.`)) return;
    
    try {
      const res = await fetch("http://127.0.0.1:8000/api/rollback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename })
      });
      const data = await res.json();
      if (data.status === "success") {
        alert("✅ " + data.message);
        openDashboard(); // Reload data
      } else {
        alert("❌ Gagal: " + data.message);
      }
    } catch (e) {
      alert("❌ Terjadi kesalahan saat menghubungi server.");
    }
  }

  let syncState = $state("idle"); // 'idle', 'backup', 'restore'

  async function syncBackup() {
    syncState = "backup";
    try {
      const res = await fetch("http://127.0.0.1:8000/api/sync/backup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: userEmail })
      });
      const data = await res.json();
      alert((data.status === "success" || data.status === "partial" ? "✅ " : "❌ ") + data.message);
    } catch (e) {
      alert("❌ Gagal terhubung ke peladen sinkronisasi.");
    } finally {
      syncState = "idle";
    }
  }

  async function syncRestore() {
    if (!confirm("PENTING: Proses ini akan mengunduh dan MENIMPA memori aktif Anda saat ini dengan cadangan dari Google Drive.\n\nLanjutkan?")) return;
    
    syncState = "restore";
    try {
      const res = await fetch("http://127.0.0.1:8000/api/sync/restore", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: userEmail })
      });
      const data = await res.json();
      alert((data.status === "success" ? "✅ " : "❌ ") + data.message);
    } catch (e) {
      alert("❌ Gagal memulihkan dari Google Drive.");
    } finally {
      syncState = "idle";
    }
  }
</script>

<div class="flex h-screen bg-transparent text-slate-200 font-sans overflow-hidden relative">
  <!-- AMBIENT GLOW ORBS -->
  <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-mamet-cyan/20 blur-[120px] animate-blob pointer-events-none z-0"></div>
  <div class="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-mamet-purple/15 blur-[120px] animate-blob pointer-events-none z-0" style="animation-delay: 2s; animation-direction: reverse;"></div>
  
  <!-- SIDEBAR (Panel Kiri) -->
  <aside class="w-64 glass-panel rounded-none border-y-0 border-l-0 flex flex-col shrink-0 z-20 shadow-[4px_0_24px_rgba(0,0,0,0.2)]">
    <div class="p-5 border-b border-white/5 flex items-center gap-3">
      <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-mamet-cyan to-mamet-purple flex items-center justify-center font-bold text-white shadow-lg shadow-mamet-cyan/30">
        M
      </div>
      <div>
        <h1 class="text-sm font-bold tracking-wide text-white">MAMET OS</h1>
        <p class="text-[10px] text-slate-400 tracking-wider">PERSONAL KERNEL v3.0</p>
      </div>
    </div>

    <!-- Navigasi Utama -->
    <nav class="flex-1 p-3 space-y-1 overflow-y-auto custom-scrollbar">
      {#each columns as col}
        <button
          onclick={() => activeColumn = col.id}
          class="w-full text-left flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-300 {activeColumn === col.id ? 'bg-mamet-cyan/10 text-mamet-cyan border border-mamet-cyan/30 cyan-glow' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200 border border-transparent'}"
        >
          <span class="flex items-center justify-center text-xl">{@html col.icon}</span>
          <div>
            <div class="text-sm font-medium">{col.label}</div>
            <div class="text-[10px] opacity-70">{col.desc}</div>
          </div>
        </button>
      {/each}
      
      <div class="my-4 border-t border-white/5 mx-2"></div>
      
      <button
        onclick={openDashboard}
        class="w-full text-left flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-300 {activeColumn === 'setting' ? 'bg-mamet-purple/10 text-mamet-purple border border-mamet-purple/30 shadow-[0_0_15px_rgba(233,179,255,0.3)]' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200 border border-transparent'}"
      >
        <span class="flex items-center justify-center text-xl">{@html svgSettings}</span>
        <div>
          <div class="text-sm font-medium">Pengaturan</div>
          <div class="text-[10px] opacity-70">Sistem & Budget AI</div>
        </div>
      </button>
    </nav>
    
    <!-- Bagian Bawah Sidebar (API Key) -->
    <div class="p-4 border-t border-white/5 bg-[#121217]">
      <div class="flex flex-col gap-2">
        <span class="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">OpenRouter API Key</span>
        <div class="flex items-center gap-2 bg-black/40 px-2 py-1.5 rounded-md border border-white/5">
          <input 
            type="password" 
            bind:value={apiKeyInput} 
            placeholder="sk-or-v1-..."
            autocomplete="new-password"
            id="api_key_input"
            name="api_key_input"
            class="bg-transparent text-xs text-white focus:outline-none w-full placeholder-slate-600"
          />
          <button onclick={saveApiKey} class="text-xs text-mamet-cyan hover:text-white font-medium transition-colors">Save</button>
        </div>
      </div>
    </div>
  </aside>

  <!-- MAIN AREA (Kolom Utama) -->
  <main class="flex-1 flex flex-col overflow-hidden relative bg-transparent">
    
    {#if activeColumn !== 'setting'}
      <!-- MODE CHAT -->
      {#each columns as col}
        {#if activeColumn === col.id}
          <section class="flex-1 flex flex-col w-full h-full animate-in fade-in duration-300">
            <!-- Header Kolom Aktif -->
            <div class="px-6 py-4 border-b border-white/5 bg-black/20 backdrop-blur-md flex justify-between items-center z-10 shadow-sm shrink-0">
              <div class="flex items-center gap-3">
                <span class="flex items-center justify-center text-2xl text-mamet-cyan/80">{@html col.icon}</span>
                <div>
                  <div class="flex items-center gap-2">
                    <h2 class="text-base font-semibold text-white/90">{col.label}</h2>
                    <button 
                      onclick={() => clearChat(col.id)}
                      class="text-slate-500 hover:text-rose-400 p-1 rounded transition-colors"
                      title="Bersihkan Percakapan (New Chat)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                    </button>
                    <button 
                      onclick={() => openDrawerMenu(col.id)}
                      class="text-slate-500 hover:text-amber-400 p-1 rounded transition-colors ml-1"
                      title="Laci (Simpan/Ambil Obrolan)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path><line x1="9" y1="14" x2="15" y2="14"></line></svg>
                    </button>
                  </div>
                  <p class="text-xs text-slate-500">{col.desc}</p>
                </div>
              </div>
              
              {#if col.id === "kolom1"}
                 <label class="cursor-pointer text-sm {uploading ? 'bg-slate-600' : 'bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400'} px-3 py-1.5 rounded transition-colors border border-indigo-500/20 font-medium flex items-center gap-2">
                   {uploading ? '⏳ Mengunggah...' : '📎 Upload Dokumen'}
                   <input
                     type="file"
                     class="hidden"
                     accept=".txt,.md,.pdf,.docx,.csv,.json"
                     onchange={handleFileUpload}
                     disabled={uploading}
                   />
                 </label>
              {/if}

              {#if col.id === "kolom2"}
                <div class="flex items-center gap-2">
                  {#if projectContextPath}
                    <div class="flex items-center gap-2 bg-mamet-cyan/10 border border-mamet-cyan/30 text-mamet-cyan px-3 py-1.5 rounded-lg text-sm max-w-[200px] shadow-[0_0_10px_rgba(0,219,233,0.1)]">
                      <span class="truncate flex items-center gap-2" title={projectContextPath}>{@html svgFolder} {projectContextPath.split(/[\\/]/).pop()}</span>
                      <button onclick={() => projectContextPath = null} class="hover:text-rose-400 transition-colors" title="Hapus Project Context">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                      </button>
                    </div>
                  {:else}
                    <button 
                      onclick={pickProjectFolder}
                      class="bg-black/30 border border-white/10 hover:border-mamet-cyan/40 text-slate-300 px-3 py-1.5 rounded-lg text-sm transition-colors flex items-center gap-2 hover:text-mamet-cyan"
                      title="Pilih folder lokal sebagai konteks"
                    >
                      {@html svgFolder} Pilih Folder
                    </button>
                  {/if}
                  <select 
                    bind:value={selectedAgent}
                    class="bg-[#1a1a1f] border border-white/10 rounded-lg text-sm text-white/90 px-3 py-1.5 outline-none focus:border-blue-500/50 transition-colors cursor-pointer"
                  >
                    <option value={null}>Tanpa Agen</option>
                    <option value="database">Database Explorer</option>
                    <option value="file">File Analysis</option>
                    <option value="web">Web Search</option>
                    <option value="research">Research</option>
                  </select>
                </div>
              {/if}
            </div>

            <!-- Chat Area -->
            <div 
              class="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 custom-scrollbar"
              bind:this={chatContainers[col.id]}
            >
              {#if messages[col.id].length === 0}
                <div class="flex flex-col items-center justify-center h-full text-mamet-cyan/20">
                  <span class="text-6xl mb-4 opacity-50 drop-shadow-[0_0_15px_rgba(0,219,233,0.2)]">{@html col.icon}</span>
                  <p class="text-sm font-medium tracking-wide text-slate-500">Mulai percakapan di {col.label}</p>
                </div>
              {/if}

              {#each messages[col.id] as msg}
                <div class="flex flex-col {msg.role === 'user' ? 'items-end' : 'items-start'}">
                  <div class="max-w-[85%] md:max-w-[75%] p-4 rounded-2xl text-[15px] leading-relaxed shadow-[0_4px_20px_rgba(0,0,0,0.15)] backdrop-blur-md transition-all duration-300 hover:-translate-y-0.5
                    {msg.role === 'user' 
                      ? 'bg-mamet-cyan/15 border border-mamet-cyan/30 border-t-mamet-cyan/60 text-mamet-cyan hover:shadow-[0_8px_25px_rgba(0,219,233,0.25)] rounded-tr-sm' 
                      : 'bg-white/[0.03] border border-white/10 border-t-white/20 text-slate-200 hover:border-white/30 rounded-tl-sm'}">
                    
                    <!-- KONTEN PESAN (MARKDOWN) -->
                    <div class="prose prose-invert prose-p:leading-relaxed prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10 prose-pre:p-4 prose-pre:rounded-xl max-w-none prose-a:text-mamet-cyan prose-strong:text-white prose-td:border-white/20 prose-th:border-white/20 text-[14px]">
                      {#if msg.role === 'user'}
                        <div class="whitespace-pre-wrap font-mono">{msg.content}</div>
                      {:else}
                        {@html DOMPurify.sanitize(marked.parse(msg.content))}
                        <div class="mt-3 flex justify-end">
                          <button 
                            onclick={() => copyToClipboard(msg.content)}
                            class="text-[11px] text-slate-400 hover:text-mamet-cyan flex items-center gap-1.5 transition-colors bg-white/5 hover:bg-white/10 px-2.5 py-1.5 rounded-lg border border-white/5"
                            title="Salin Teks Mentah"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            Copy Response
                          </button>
                        </div>
                      {/if}
                    </div>
                    
                    {#if msg.requires_approval && col.id === "kolom3"}
                      <div class="mt-4 flex gap-3 border-t border-white/10 pt-4">
                        <button 
                          onclick={() => handleAction(col.id, "setujui", msg.approval_details?.task_id)}
                          class="flex-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-500 border border-emerald-500/20 px-4 py-2.5 rounded-lg text-sm font-bold transition-colors flex items-center justify-center gap-2"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                          Setujui
                        </button>
                        <button 
                          onclick={() => handleAction(col.id, "tolak", msg.approval_details?.task_id)}
                          class="flex-1 bg-rose-500/10 hover:bg-rose-500/20 text-rose-500 border border-rose-500/20 px-4 py-2.5 rounded-lg text-sm font-bold transition-colors flex items-center justify-center gap-2"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                          Tolak
                        </button>
                      </div>
                    {/if}
                  </div>
                </div>
              {/each}
              
              {#if loadings[col.id]}
                <div class="flex items-start">
                  <div class="p-4 rounded-2xl bg-[#18181b] border border-white/10 text-slate-400 rounded-tl-sm flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-slate-500 animate-bounce"></div>
                    <div class="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style="animation-delay: 0.1s"></div>
                    <div class="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style="animation-delay: 0.2s"></div>
                  </div>
                </div>
              {/if}
            </div>

            <!-- Input Area -->
            <div class="p-4 border-t border-white/5 bg-black/40 backdrop-blur-xl shrink-0 z-10 relative">
              <div class="max-w-4xl mx-auto">
                <div class="relative flex items-end gap-2 bg-white/[0.03] border border-white/10 border-t-white/20 p-2 rounded-2xl focus-within:border-mamet-cyan/60 focus-within:ring-1 focus-within:ring-mamet-cyan/50 focus-within:shadow-[0_0_30px_rgba(0,219,233,0.2)] focus-within:bg-white/[0.05] transition-all duration-300">
                  <textarea
                    bind:value={inputs[col.id]}
                    onkeydown={(e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(col.id); } }}
                    placeholder="Tulis instruksi atau ketik sesuatu..."
                    class="w-full bg-transparent text-sm text-white placeholder-slate-500 px-3 py-2.5 outline-none resize-none min-h-[48px] max-h-[200px] custom-scrollbar"
                    rows="1"
                  ></textarea>
                  <button
                    aria-label="Kirim pesan"
                    onclick={() => handleSend(col.id)}
                    disabled={loadings[col.id] || !inputs[col.id].trim()}
                    class="glass-btn-primary shrink-0 m-0.5 p-3 rounded-xl disabled:bg-white/5 disabled:border-white/10 disabled:text-slate-500 disabled:shadow-none"
                  >
                    {#if loadings[col.id]}
                      <svg class="animate-spin" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
                    {:else}
                      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                    {/if}
                  </button>
                </div>
                <div class="mt-2 flex justify-between items-center px-1">
                   <span class="text-xs text-slate-600">Tekan <kbd class="bg-white/5 px-1 rounded">Shift + Enter</kbd> untuk baris baru</span>
                </div>
              </div>
            </div>

          </section>
        {/if}
      {/each}

    {:else}
      <!-- MODE SETTINGS / DASHBOARD -->
      <section class="flex-1 overflow-y-auto p-6 md:p-10 custom-scrollbar animate-in fade-in duration-300">
        <div class="max-w-4xl mx-auto space-y-8">
          
          <div class="border-b border-white/10 pb-6 mb-8">
            <h2 class="text-2xl font-bold text-white flex items-center gap-3">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-mamet-purple"><path d="M12 20v-6M6 20V10M18 20V4"/></svg>
              Command Center
            </h2>
            <p class="text-sm text-slate-400 mt-2">Pusat kendali pengaturan sistem, anggaran AI, dan cadangan pemulihan MAMET OS.</p>
          </div>

          {#if loadingDashboard}
            <div class="flex items-center justify-center h-32">
              <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          {:else}
            <!-- SECTION: BUDGET CONTROL -->
            <section>
              <h3 class="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider flex items-center gap-2">
                💰 Budget & Pemakaian AI
              </h3>
              {#if budgetData && budgetData.providers && Object.keys(budgetData.providers).length > 0}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {#each Object.entries(budgetData.providers) as [provider, data]}
                    {@const d = data as any}
                    <div class="glass-panel p-5 relative overflow-hidden group">
                      <div class="absolute bottom-0 left-0 h-1 bg-white/5 w-full">
                        <div class="h-full {d.status === 'exceeded' ? 'bg-mamet-amber' : 'bg-mamet-cyan'} transition-all duration-1000 cyan-glow" style="width: {d.percentage}%"></div>
                      </div>
                      
                      <div class="flex justify-between items-start mb-2">
                        <h4 class="font-bold text-white capitalize text-lg">{provider}</h4>
                        <span class="text-xs px-2.5 py-1 rounded-full {d.status !== 'exceeded' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/20 text-rose-400 border border-rose-500/20'}">
                          {d.status !== 'exceeded' ? 'Aktif' : 'Limit Habis'}
                        </span>
                      </div>
                      <div class="text-xs text-slate-400 mb-1">Total Biaya Bulan Ini:</div>
                      <div class="text-2xl font-mono font-bold text-slate-200 mb-5">
                        Rp {(d.used || 0).toLocaleString('id-ID')}
                        <span class="text-sm text-slate-500 font-sans font-normal ml-1">/ Rp {(d.monthly_cap || 0).toLocaleString('id-ID')}</span>
                      </div>
                      
                      <div class="grid grid-cols-2 gap-3 text-xs border-t border-white/5 pt-4">
                        <div>
                          <div class="text-slate-500 mb-1">Sisa Limit Budget</div>
                          <div class="font-mono text-emerald-400/80 bg-emerald-500/10 px-2 py-1 rounded w-fit">Rp {(d.remaining || 0).toLocaleString('id-ID')}</div>
                        </div>
                        <div>
                          <div class="text-slate-500 mb-1">Status Pemakaian</div>
                          <div class="font-mono text-slate-300 bg-white/5 px-2 py-1 rounded w-fit">{d.percentage}% {d.status}</div>
                        </div>
                      </div>
                    </div>
                  {/each}
                </div>
              {:else}
                <div class="text-sm text-slate-500 bg-[#1a1a1f] p-6 rounded-xl border border-white/5 text-center">
                  Belum ada data pemakaian tercatat. Mulai chat untuk mengumpulkan data.
                </div>
              {/if}
            </section>

            <!-- SECTION: WARISAN DIGITAL (GOOGLE DRIVE SYNC) -->
            <section class="pt-4">
              <h3 class="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider flex items-center gap-2">
                ☁️ Sinkronisasi Cloud (Warisan Digital)
              </h3>
              
              <div class="glass-panel overflow-hidden">
                <div class="p-5 bg-black/20 border-b border-white/5 flex gap-4">
                  <div class="text-indigo-400 bg-indigo-500/10 p-2 rounded-lg h-fit border border-indigo-500/20">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"></path><path d="M12 12v9"></path><path d="m8 17 4-4 4 4"></path></svg>
                  </div>
                  <p class="text-sm text-slate-400 leading-relaxed">
                    Cadangkan seluruh ingatan asisten, pangkalan pengetahuan (RAG), dan Kunci API (yang telah dienkripsi dengan sandi AES-256) ke akun Google Drive Anda.
                    Ini memastikan "otak" MAMET OS selalu aman dan bisa diwariskan ke perangkat lain.
                  </p>
                </div>
                <div class="p-5 flex gap-4 bg-white/5">
                  <button 
                    onclick={syncBackup}
                    disabled={syncState !== 'idle'}
                    class="flex-1 glass-btn-primary py-3 rounded-xl flex items-center justify-center gap-2 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {#if syncState === 'backup'}
                      <div class="w-4 h-4 border-2 border-white/80 border-t-transparent rounded-full animate-spin"></div>
                      Sedang Menyinkronkan...
                    {:else}
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"></path><path d="M12 12v9"></path><path d="m8 17 4-4 4 4"></path></svg>
                      Unggah ke Google Drive
                    {/if}
                  </button>
                  <button 
                    onclick={syncRestore}
                    disabled={syncState !== 'idle'}
                    class="flex-1 border border-white/10 hover:border-emerald-500/50 bg-black/40 hover:bg-emerald-500/10 text-slate-300 hover:text-emerald-400 py-3 rounded-xl flex items-center justify-center gap-2 font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {#if syncState === 'restore'}
                      <div class="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div>
                      Sedang Mengunduh...
                    {:else}
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"></path><path d="M12 21v-9"></path><path d="m8 16 4 4 4-4"></path></svg>
                      Pulihkan (Restore) Memori
                    {/if}
                  </button>
                </div>
              </div>
            </section>

            <!-- SECTION: ROLLBACK (SANDBOX) -->
            <section class="pt-4">
              <h3 class="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider flex items-center gap-2">
                🛡️ Sistem Keamanan & Rollback
              </h3>
              
              <div class="glass-panel overflow-hidden">
                <div class="p-5 bg-black/20 border-b border-white/5 flex gap-4">
                  <div class="text-mamet-cyan bg-mamet-cyan/10 p-2 rounded-lg h-fit border border-mamet-cyan/20">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                  </div>
                  <p class="text-sm text-slate-400 leading-relaxed">
                    Setiap kali Engineer (Kolom 3) mengubah kode sistem, MAMET OS otomatis membuat file ZIP dari kondisi terakhir. 
                    Anda dapat memutar waktu kembali ke versi sebelum kerusakan terjadi.
                  </p>
                </div>
                
                {#if backupsData.length > 0}
                  <div class="divide-y divide-white/5">
                    {#each backupsData as backup}
                      <div class="p-5 flex items-center justify-between hover:bg-white/5 transition-colors group">
                        <div class="flex items-center gap-4">
                          <div class="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500 shrink-0 border border-amber-500/20">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                          </div>
                          <div>
                            <div class="font-medium text-sm text-slate-200">{backup.filename}</div>
                            <div class="text-xs text-slate-500 mt-0.5">
                              {new Date(backup.created_at).toLocaleString('id-ID')} • {(backup.size / 1024).toFixed(1)} KB
                            </div>
                          </div>
                        </div>
                        <button 
                          onclick={() => executeRollback(backup.filename)}
                          class="px-4 py-2 rounded-lg text-sm font-semibold bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 border border-rose-500/20 transition-all opacity-0 group-hover:opacity-100 focus:opacity-100 flex items-center gap-2"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path></svg>
                          Rollback
                        </button>
                      </div>
                    {/each}
                  </div>
                {:else}
                  <div class="p-8 text-center text-sm text-slate-500">
                    Belum ada titik pemulihan (backup) yang tersedia.<br>Sistem otomatis membuatnya saat Engineer mengedit kode.
                  </div>
                {/if}
              </div>
            </section>
          {/if}
        </div>
      </section>
    {/if}
  </main>
</div>

<style>
  /* Custom Scrollbar for a premium look */
  .custom-scrollbar::-webkit-scrollbar {
    width: 6px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2);
  }
</style>
