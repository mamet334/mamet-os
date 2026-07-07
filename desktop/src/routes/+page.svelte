<script lang="ts">
  import { onMount } from 'svelte';

  // State untuk kolom aktif (mode Mobile)
  let activeColumn = $state("kolom2");
  
  // Konfigurasi Kolom
  const columns = [
    { id: "kolom1", label: "Pencarian Cepat", icon: "🔍", desc: "RAG & Dokumen" },
    { id: "kolom2", label: "Asisten Pribadi", icon: "🤖", desc: "User Memory & Sub-Agent" },
    { id: "kolom3", label: "Engineer", icon: "🔧", desc: "Self-Maintenance" },
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

  // State untuk Dashboard (Fase 2)
  let showDashboard = $state(false);
  let budgetData = $state<any>(null);
  let backupsData = $state<any[]>([]);
  let loadingDashboard = $state(false);

  onMount(() => {
    // Coba ambil API key dari localStorage
    apiKey = localStorage.getItem("openrouter_key") || "";
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
          user_id: "default@mamet.os",
          column: columnId,
          message: textToSend,
          api_key: apiKey || null,
          agent: columnId === "kolom2" ? selectedAgent : null
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

  async function openDashboard() {
    showDashboard = true;
    loadingDashboard = true;
    try {
      // Ambil data budget
      const bRes = await fetch(`http://127.0.0.1:8000/api/budget?email=default`);
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

<div class="flex flex-col h-screen bg-[#09090b] text-slate-200 font-sans">
  
  <!-- HEADER -->
  <header class="flex items-center justify-between px-6 py-3 border-b border-white/10 bg-[#0f0f13] shrink-0 shadow-sm z-10">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
        M
      </div>
      <div>
        <h1 class="text-sm font-bold tracking-wide text-white">MAMET OS</h1>
        <p class="text-[10px] text-slate-400 tracking-wider">PERSONAL KERNEL v2.0</p>
      </div>
    </div>
    
    <div class="flex items-center gap-4">
      <div class="flex items-center gap-2 bg-black/40 px-3 py-1.5 rounded-md border border-white/5">
        <span class="text-xs text-slate-400">API Key:</span>
        <input 
          type="password" 
          bind:value={apiKey} 
          placeholder="sk-or-v1-..."
          class="bg-transparent text-xs text-white focus:outline-none w-32 placeholder-slate-600"
        />
        <button onclick={saveApiKey} class="text-xs text-indigo-400 hover:text-indigo-300 font-medium ml-1">Simpan</button>
      </div>
      <button onclick={openDashboard} class="text-xs bg-indigo-600/20 hover:bg-indigo-600/40 border border-indigo-500/30 text-indigo-300 px-3 py-1.5 rounded-md transition-colors shadow-sm font-semibold flex items-center gap-1.5">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20v-6M6 20V10M18 20V4"/></svg>
        Dashboard Panel
      </button>
    </div>
  </header>

  <!-- MOBILE TABS -->
  <nav class="md:hidden flex border-b border-white/10 bg-[#0f0f13] shrink-0">
    {#each columns as col}
      <button
        onclick={() => activeColumn = col.id}
        class="flex-1 py-3 text-center text-sm transition-colors {activeColumn === col.id ? 'border-b-2 border-indigo-500 text-indigo-400 bg-white/5' : 'text-slate-500 hover:text-slate-300'}"
      >
        <span class="block text-lg mb-1">{col.icon}</span>
        <span class="text-[11px] font-medium">{col.label}</span>
      </button>
    {/each}
  </nav>

  <!-- MAIN THREE-PANE VIEW -->
  <main class="flex-1 flex overflow-hidden">
    
    <!-- Desktop: Render all 3 columns. Mobile: Render only active column -->
    {#each columns as col}
      <section class="flex-1 flex flex-col {activeColumn === col.id ? 'flex' : 'hidden md:flex'} border-r border-white/5 last:border-r-0 relative group">
        
        <!-- Column Header -->
        <div class="px-5 py-4 border-b border-white/5 bg-[#121217] flex justify-between items-center z-10 shadow-sm">
          <div class="flex items-center gap-2">
            <span class="text-lg">{col.icon}</span>
            <div>
              <h2 class="text-sm font-semibold text-white/90">{col.label}</h2>
              <p class="text-[10px] text-slate-500">{col.desc}</p>
            </div>
          </div>
          
          {#if col.id === "kolom1"}
             <label class="cursor-pointer text-xs {uploading ? 'bg-slate-600' : 'bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400'} px-2 py-1.5 rounded transition-colors border border-indigo-500/20">
               {uploading ? '⏳ Upload...' : '📎 Upload'}
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
            <select 
              bind:value={selectedAgent}
              class="bg-[#1a1a1f] border border-white/10 rounded-lg text-xs text-white/70 px-2 py-1 outline-none focus:border-blue-500/50 transition-colors"
            >
              <option value={null}>Tanpa Agen</option>
              <option value="database">Database Explorer</option>
              <option value="file">File Analysis</option>
              <option value="web">Web Search</option>
              <option value="research">Research</option>
            </select>
          {/if}
        </div>

        <!-- Chat Area -->
        <div class="flex-1 overflow-y-auto p-5 space-y-5 bg-[#09090b] custom-scrollbar">
          {#if messages[col.id].length === 0}
            <div class="flex flex-col items-center justify-center h-full text-slate-600 opacity-50">
              <span class="text-4xl mb-3">{col.icon}</span>
              <p class="text-xs font-medium tracking-wide">Mulai percakapan di {col.label}</p>
            </div>
          {/if}

          {#each messages[col.id] as msg}
            <div class="flex flex-col {msg.role === 'user' ? 'items-end' : 'items-start'}">
              <div class="max-w-[90%] p-3.5 rounded-2xl text-sm leading-relaxed shadow-sm
                {msg.role === 'user' 
                  ? 'bg-indigo-600 text-white rounded-tr-sm' 
                  : 'bg-[#18181b] border border-white/10 text-slate-200 rounded-tl-sm'}">
                <div class="whitespace-pre-wrap font-mono text-[13px]">{msg.content}</div>
                
                <!-- Approval Buttons for Engineer Column -->
                {#if msg.requires_approval && col.id === "kolom3"}
                  <div class="mt-4 flex gap-2 border-t border-white/10 pt-3">
                    <button 
                      onclick={() => handleAction(col.id, "setujui", msg.approval_details?.task_id)}
                      class="flex-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-500 border border-emerald-500/20 px-3 py-2 rounded-lg text-xs font-bold transition-colors flex items-center justify-center gap-1.5"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                      Setujui
                    </button>
                    <button 
                      onclick={() => handleAction(col.id, "tolak", msg.approval_details?.task_id)}
                      class="flex-1 bg-rose-500/10 hover:bg-rose-500/20 text-rose-500 border border-rose-500/20 px-3 py-2 rounded-lg text-xs font-bold transition-colors flex items-center justify-center gap-1.5"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                      Tolak
                    </button>
                  </div>
                {/if}
              </div>
            </div>
          {/each}
          
          {#if loadings[col.id]}
            <div class="flex items-start">
              <div class="max-w-[85%] p-3.5 rounded-2xl bg-[#18181b] border border-white/10 text-slate-400 rounded-tl-sm flex items-center gap-2">
                <div class="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce"></div>
                <div class="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
            </div>
          {/if}
        </div>

        <!-- Input Area -->
        <div class="p-4 border-t border-white/5 bg-[#121217]">
          <div class="relative flex items-end gap-2 bg-[#09090b] border border-white/10 p-1.5 rounded-xl focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/50 transition-all">
            <textarea
              bind:value={inputs[col.id]}
              onkeydown={(e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(col.id); } }}
              placeholder="Tulis instruksi..."
              class="w-full bg-transparent text-sm text-white placeholder-slate-500 px-3 py-2.5 outline-none resize-none min-h-[44px] max-h-[120px] custom-scrollbar"
              rows="1"
            ></textarea>
            <button
              aria-label="Kirim pesan"
              onclick={() => handleSend(col.id)}
              disabled={loadings[col.id] || !inputs[col.id].trim()}
              class="p-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white transition-colors shrink-0 m-0.5"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </div>
          <div class="mt-2 flex justify-between items-center px-1">
             <span class="text-[10px] text-slate-600">Shift + Enter untuk baris baru</span>
          </div>
        </div>

      </section>
    {/each}
  </main>

  <!-- DASHBOARD OVERLAY MODAL -->
  {#if showDashboard}
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div class="bg-[#121217] border border-white/10 rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        
        <div class="flex items-center justify-between p-5 border-b border-white/5 bg-[#18181b]">
          <h2 class="text-lg font-bold text-white flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-indigo-400"><path d="M12 20v-6M6 20V10M18 20V4"/></svg>
            Command Center
          </h2>
          <button onclick={() => showDashboard = false} class="text-slate-400 hover:text-white p-1">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>

        <div class="p-6 overflow-y-auto custom-scrollbar flex-1 space-y-8">
          {#if loadingDashboard}
            <div class="flex items-center justify-center h-32">
              <div class="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          {:else}
            <!-- SECTION: BUDGET CONTROL -->
            <section>
              <h3 class="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider flex items-center gap-2">
                💰 Budget & Pemakaian AI
              </h3>
              {#if budgetData && Object.keys(budgetData).length > 0}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {#each Object.entries(budgetData) as [provider, data]}
                    {@const d = data as any}
                    <div class="bg-[#1a1a1f] p-4 rounded-xl border border-white/5 relative overflow-hidden">
                      <!-- Progress bar background -->
                      <div class="absolute bottom-0 left-0 h-1 bg-indigo-600/30 w-full">
                        <div class="h-full bg-indigo-500" style="width: {Math.min(100, (d.usage_cost / d.budget_cap) * 100)}%"></div>
                      </div>
                      
                      <div class="flex justify-between items-start mb-2">
                        <h4 class="font-bold text-white capitalize">{provider}</h4>
                        <span class="text-xs px-2 py-0.5 rounded-full {d.budget_available ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}">
                          {d.budget_available ? 'Aktif' : 'Limit Habis'}
                        </span>
                      </div>
                      <div class="text-xs text-slate-400 mb-1">Total Biaya Bulan Ini:</div>
                      <div class="text-2xl font-mono font-bold text-slate-200 mb-4">
                        Rp {d.usage_cost.toLocaleString('id-ID')}
                        <span class="text-xs text-slate-500 font-sans font-normal ml-1">/ Rp {d.budget_cap.toLocaleString('id-ID')}</span>
                      </div>
                      
                      <div class="grid grid-cols-2 gap-2 text-xs border-t border-white/5 pt-3">
                        <div>
                          <div class="text-slate-500">Tokens In</div>
                          <div class="font-mono text-slate-300">{d.tokens_in.toLocaleString()}</div>
                        </div>
                        <div>
                          <div class="text-slate-500">Tokens Out</div>
                          <div class="font-mono text-slate-300">{d.tokens_out.toLocaleString()}</div>
                        </div>
                      </div>
                    </div>
                  {/each}
                </div>
              {:else}
                <div class="text-sm text-slate-500 bg-[#1a1a1f] p-4 rounded-xl border border-white/5">
                  Belum ada data pemakaian tercatat. Mulai chat untuk mengumpulkan data.
                </div>
              {/if}
            </section>

            <!-- SECTION: ROLLBACK (SANDBOX) -->
            <section>
              <h3 class="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider flex items-center gap-2">
                🛡️ Sistem Keamanan & Rollback
              </h3>
              
              <div class="bg-[#1a1a1f] rounded-xl border border-white/5 overflow-hidden">
                <div class="p-4 bg-black/20 border-b border-white/5">
                  <p class="text-xs text-slate-400 leading-relaxed">
                    Setiap kali Engineer (Kolom 3) mengubah kode sistem, MAMET OS otomatis membuat file ZIP dari kondisi terakhir. 
                    Anda dapat memutar waktu kembali ke versi sebelum kerusakan terjadi.
                  </p>
                </div>
                
                {#if backupsData.length > 0}
                  <div class="divide-y divide-white/5">
                    {#each backupsData as backup}
                      <div class="p-4 flex items-center justify-between hover:bg-white/5 transition-colors group">
                        <div class="flex items-center gap-3">
                          <div class="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                          </div>
                          <div>
                            <div class="font-medium text-sm text-slate-200">{backup.filename}</div>
                            <div class="text-xs text-slate-500">
                              {new Date(backup.created_at).toLocaleString('id-ID')} • {(backup.size / 1024).toFixed(1)} KB
                            </div>
                          </div>
                        </div>
                        <button 
                          onclick={() => executeRollback(backup.filename)}
                          class="px-3 py-1.5 rounded text-xs font-semibold bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 border border-rose-500/20 transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100"
                        >
                          🔄 Rollback
                        </button>
                      </div>
                    {/each}
                  </div>
                {:else}
                  <div class="p-6 text-center text-sm text-slate-500">
                    Belum ada titik pemulihan (backup) yang tersedia. Sistem otomatis membuatnya saat Engineer mengedit kode.
                  </div>
                {/if}
              </div>
            </section>
          {/if}
        </div>
      </div>
    </div>
  {/if}

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
