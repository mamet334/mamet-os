<script lang="ts">
  import { onMount } from 'svelte';
  import { open } from '@tauri-apps/plugin-dialog';

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
  let apiKey = $state("");
  let selectedAgent = $state<string | null>(null);
  let projectContextPath = $state<string | null>(null);

  // State untuk Dashboard (Settings)
  let budgetData = $state<any>(null);
  let backupsData = $state<any[]>([]);
  let loadingDashboard = $state(false);

  let userEmail = $state("default");

  onMount(() => {
    // Coba ambil API key dari localStorage
    apiKey = localStorage.getItem("openrouter_key") || "";
    userEmail = localStorage.getItem("mamet_user_email") || "default";
  });

  async function handleSend(columnId: string, customText?: string) {
    const textToSend = customText !== undefined ? customText : inputs[columnId];
    if (!textToSend.trim() || loadings[columnId]) return;

    // Tambah pesan user ke UI
    messages[columnId] = [...messages[columnId], { role: "user", content: textToSend }];
    if (customText === undefined) {
      inputs[columnId] = "";
    }
    
    loadings[columnId] = true;

    try {
      const res = await fetch("http://127.0.0.1:8000/api/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userEmail,
          column: columnId,
          message: textToSend,
          api_key: apiKey || null,
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
    }
  }

  function handleAction(columnId: string, actionType: "setujui" | "tolak", taskId?: string) {
    const commandText = taskId ? `${actionType} ${taskId}` : actionType;
    handleSend(columnId, commandText);
  }

  function saveApiKey() {
    localStorage.setItem("openrouter_key", apiKey);
    alert("API Key tersimpan secara lokal!");
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
      console.error("Gagal membuka folder picker:", error);
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
</script>

<div class="flex h-screen bg-transparent text-slate-200 font-sans overflow-hidden">
  
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
            bind:value={apiKey} 
            placeholder="sk-or-v1-..."
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
                  <h2 class="text-base font-semibold text-white/90">{col.label}</h2>
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
            <div class="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 custom-scrollbar">
              {#if messages[col.id].length === 0}
                <div class="flex flex-col items-center justify-center h-full text-mamet-cyan/20">
                  <span class="text-6xl mb-4 opacity-50 drop-shadow-[0_0_15px_rgba(0,219,233,0.2)]">{@html col.icon}</span>
                  <p class="text-sm font-medium tracking-wide text-slate-500">Mulai percakapan di {col.label}</p>
                </div>
              {/if}

              {#each messages[col.id] as msg}
                <div class="flex flex-col {msg.role === 'user' ? 'items-end' : 'items-start'}">
                  <div class="max-w-[85%] md:max-w-[75%] p-4 rounded-2xl text-[15px] leading-relaxed shadow-sm backdrop-blur-sm
                    {msg.role === 'user' 
                      ? 'bg-mamet-cyan/20 border border-mamet-cyan/30 text-mamet-cyan shadow-[0_0_15px_rgba(0,219,233,0.15)] rounded-tr-sm' 
                      : 'bg-white/5 border border-white/10 text-slate-200 rounded-tl-sm'}">
                    <div class="whitespace-pre-wrap font-mono text-[14px]">{msg.content}</div>
                    
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
            <div class="p-4 border-t border-white/5 bg-black/30 backdrop-blur-md shrink-0">
              <div class="max-w-4xl mx-auto">
                <div class="relative flex items-end gap-2 bg-white/5 border border-white/10 p-2 rounded-2xl focus-within:border-mamet-cyan/50 focus-within:ring-1 focus-within:ring-mamet-cyan/50 transition-all shadow-inner">
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
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
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
