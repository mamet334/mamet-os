<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  let status: any = null;
  let email = '';
  let loading = true;
  let errorMsg = '';

  onMount(async () => {
    email = localStorage.getItem('mamet_user_email') || '';
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
    localStorage.removeItem('mamet_user_email');
    goto('/');
  }
</script>

<div class="min-h-screen p-8">
  <div class="max-w-5xl mx-auto animate-fade-in">
    <div class="flex justify-between items-center mb-12">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-mamet-cyan to-mamet-purple flex items-center justify-center shadow-lg shadow-mamet-cyan/20">
          <span class="text-xl font-bold text-white">M</span>
        </div>
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-white">Dashboard <span class="text-transparent bg-clip-text bg-gradient-to-r from-mamet-cyan to-mamet-purple">Awal</span></h1>
          <p class="text-slate-400 mt-1 font-mono text-sm">{email}</p>
        </div>
      </div>
      <button on:click={logout} class="glass-btn-secondary text-rose-400 hover:text-rose-300 hover:border-rose-400/30">🚪 Keluar</button>
    </div>
    
    {#if loading}
      <div class="flex items-center justify-center h-64">
        <div class="w-10 h-10 border-2 border-mamet-cyan border-t-transparent rounded-full animate-spin"></div>
      </div>
    {:else if errorMsg}
      <div class="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-4 rounded-xl glass-panel">{errorMsg}</div>
    {:else if status}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
        
        <!-- Status Panel -->
        <div class="glass-panel p-8 relative overflow-hidden group">
          <div class="absolute -right-10 -top-10 w-32 h-32 bg-mamet-cyan/10 rounded-full blur-2xl group-hover:bg-mamet-cyan/20 transition-all duration-500"></div>
          
          <h2 class="text-mamet-cyan uppercase text-xs font-bold tracking-widest mb-6">Status Sistem Aktif</h2>
          <ul class="space-y-4">
            <li class="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/5 hover:border-mamet-cyan/30 transition-colors">
              <span class="text-slate-300">Kernel Inti</span> 
              <span class="text-emerald-400 flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> {status.kernel}</span>
            </li>
            <li class="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/5 hover:border-mamet-cyan/30 transition-colors">
              <span class="text-slate-300">Penyedia AI</span> 
              <span class="text-mamet-cyan font-medium">{status.ai_provider}</span>
            </li>
            <li class="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/5 hover:border-mamet-cyan/30 transition-colors">
              <span class="text-slate-300">Database RAG</span> 
              <span class="text-mamet-purple font-mono">{status.rag.docs} docs</span>
            </li>
            <li class="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/5 hover:border-mamet-cyan/30 transition-colors">
              <span class="text-slate-300">Memori Personal</span> 
              <span class="text-mamet-amber font-mono">{status.memory.facts} fakta</span>
            </li>
          </ul>
        </div>
        
        <!-- Budget Panel -->
        <div class="glass-panel p-8 flex flex-col justify-between relative overflow-hidden group">
          <div class="absolute -left-10 -bottom-10 w-32 h-32 bg-mamet-purple/10 rounded-full blur-2xl group-hover:bg-mamet-purple/20 transition-all duration-500"></div>
          
          <div class="relative z-10">
            <h2 class="text-mamet-purple uppercase text-xs font-bold tracking-widest mb-6">Anggaran AI Bulan Ini</h2>
            
            <div class="flex items-baseline gap-2 mt-2 mb-1">
              <span class="text-4xl font-bold text-white">Rp {status.budget && status.budget.total_budget_used !== undefined ? status.budget.total_budget_used.toLocaleString('id-ID') : 0}</span>
            </div>
            <div class="text-slate-400 text-sm">
              dari limit Rp {status.budget && status.budget.total_budget_cap !== undefined ? status.budget.total_budget_cap.toLocaleString('id-ID') : 100000}
            </div>
            
            <div class="w-full bg-black/40 rounded-full h-3 mt-6 border border-white/5 overflow-hidden">
              <div class="bg-gradient-to-r from-mamet-cyan to-mamet-purple h-full rounded-full transition-all duration-1000 relative" 
                   style="width: {status.budget && status.budget.total_budget_cap > 0 ? Math.min((status.budget.total_budget_used / status.budget.total_budget_cap) * 100, 100) : 0}%">
                   <div class="absolute inset-0 bg-white/20 w-full h-full" style="animation: shimmer 2s infinite"></div>
              </div>
            </div>
          </div>
          
          <div class="mt-10 space-y-4 relative z-10">
            <button on:click={() => goto('/workspace')} class="glass-btn-primary w-full py-4 text-lg cyan-glow">
              🚀 Masuk ke 3 Kolom
            </button>
            <button on:click={() => goto('/credit')} class="glass-btn-secondary w-full py-3 text-slate-300 hover:text-white">
              📽️ Tentang MAMET OS
            </button>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  @keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
</style>
