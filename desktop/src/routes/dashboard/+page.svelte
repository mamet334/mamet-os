<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  let status: any = null;
  let email = '';
  let loading = true;
  let errorMsg = '';

  onMount(async () => {
    email = localStorage.getItem('email') || '';
    if (!email) {
      goto('/');
      return;
    }
    
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/status?email=${encodeURIComponent(email)}`);
      if (res.ok) {
        status = await res.json();
      } else {
        errorMsg = "Gagal memuat status sistem";
      }
    } catch (e) {
      errorMsg = "Gagal terhubung ke Kernel";
    } finally {
      loading = false;
    }
  });
  
  function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('email');
    goto('/');
  }
</script>

<div class="min-h-screen bg-gray-900 text-white p-8 font-sans">
  <div class="max-w-4xl mx-auto">
    <div class="flex justify-between items-center mb-10">
      <div>
        <h1 class="text-4xl font-bold">Dashboard Awal</h1>
        <p class="text-xl text-gray-400 mt-2">Selamat datang, {email}</p>
      </div>
      <button on:click={logout} class="px-4 py-2 border border-gray-600 rounded hover:bg-gray-800 transition">🚪 Keluar</button>
    </div>
    
    {#if loading}
      <div class="text-center py-20 text-gray-400">Memuat status sistem...</div>
    {:else if errorMsg}
      <div class="bg-red-500/20 border border-red-500 text-red-300 p-4 rounded">{errorMsg}</div>
    {:else if status}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        <div class="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
          <h2 class="text-gray-400 uppercase text-sm tracking-wider mb-4 border-b border-gray-700 pb-2">Status Sistem</h2>
          <ul class="space-y-3">
            <li class="flex justify-between"><span>Kernel:</span> <span class="text-green-400">✅ {status.kernel}</span></li>
            <li class="flex justify-between"><span>AI Provider:</span> <span class="text-blue-400">✅ {status.ai_provider}</span></li>
            <li class="flex justify-between"><span>RAG Engine:</span> <span class="text-purple-400">📊 {status.rag.docs} dokumen</span></li>
            <li class="flex justify-between"><span>User Memory:</span> <span class="text-yellow-400">🧠 {status.memory.facts} fakta</span></li>
            <li class="flex justify-between"><span>Engineer:</span> <span class="text-green-400">🔧 {status.engineer}</span></li>
            <li class="flex justify-between"><span>Backup:</span> <span class="text-gray-300">📦 {status.backup.count} arsip</span></li>
          </ul>
        </div>
        
        <div class="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg flex flex-col justify-between">
          <div>
            <h2 class="text-gray-400 uppercase text-sm tracking-wider mb-4 border-b border-gray-700 pb-2">Budget AI</h2>
            <div class="text-3xl font-bold mt-2 mb-1">
              Rp {status.budget && status.budget.total_budget_used !== undefined ? status.budget.total_budget_used.toLocaleString('id-ID') : 0}
            </div>
            <div class="text-gray-400 text-sm">
              dari batas Rp {status.budget && status.budget.total_budget_cap !== undefined ? status.budget.total_budget_cap.toLocaleString('id-ID') : 100000}
            </div>
            
            <div class="w-full bg-gray-700 rounded-full h-2.5 mt-4">
              <div class="bg-blue-600 h-2.5 rounded-full" style="width: {status.budget && status.budget.total_budget_cap > 0 ? Math.min((status.budget.total_budget_used / status.budget.total_budget_cap) * 100, 100) : 0}%"></div>
            </div>
          </div>
          
          <div class="mt-8 space-y-3">
            <button on:click={() => goto('/credit')} class="w-full bg-gray-700 hover:bg-gray-600 text-white font-medium py-3 px-4 rounded transition flex items-center justify-center gap-2">
              🎬 Tentang MAMET OS
            </button>
            <button on:click={() => goto('/workspace')} class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded transition flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(37,99,235,0.5)]">
              🚀 Masuk ke 3 Kolom
            </button>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>
