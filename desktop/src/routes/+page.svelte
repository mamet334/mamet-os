<script lang="ts">
  import { goto } from '$app/navigation';
  
  let email = '';
  let password = '';
  let isRegister = false;
  let errorMsg = '';
  let loading = false;

  async function handleSubmit() {
    loading = true;
    errorMsg = '';
    const endpoint = isRegister ? 'http://127.0.0.1:8000/api/register' : 'http://127.0.0.1:8000/api/login';
    
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      
      if (!res.ok) {
        errorMsg = data.detail || "Terjadi kesalahan";
      } else {
        localStorage.setItem('token', data.token);
        localStorage.setItem('email', email);
        goto('/dashboard');
      }
    } catch (e) {
      errorMsg = "Gagal menghubungi server Kernel";
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen w-full flex items-center justify-center p-4">
  <div class="glass-panel p-10 w-full max-w-md animate-fade-in relative overflow-hidden">
    <!-- Decorative glow -->
    <div class="absolute -top-20 -right-20 w-40 h-40 bg-mamet-cyan/20 rounded-full blur-3xl"></div>
    <div class="absolute -bottom-20 -left-20 w-40 h-40 bg-mamet-purple/20 rounded-full blur-3xl"></div>

    <div class="text-center mb-10 relative z-10">
      <div class="w-16 h-16 mx-auto bg-gradient-to-br from-mamet-cyan to-mamet-purple rounded-2xl flex items-center justify-center shadow-lg shadow-mamet-cyan/20 mb-4 hover:scale-105 transition-transform">
        <span class="text-2xl font-bold text-white">M</span>
      </div>
      <h1 class="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">MAMET OS</h1>
      <p class="text-mamet-cyan font-medium mt-2 tracking-wide text-sm uppercase">Warisan Digital Pribadi</p>
    </div>
    
    {#if errorMsg}
      <div class="bg-rose-500/10 border border-rose-500/50 text-rose-300 px-4 py-3 rounded-xl mb-6 text-sm flex items-center gap-2">
        <span>⚠️</span> {errorMsg}
      </div>
    {/if}
    
    <form on:submit|preventDefault={handleSubmit} class="space-y-5 relative z-10">
      <div>
        <label class="block text-sm text-slate-300 mb-2 ml-1">Alamat Email</label>
        <input type="email" bind:value={email} required placeholder="email@anda.com"
               class="glass-input w-full" />
      </div>
      
      <div>
        <label class="block text-sm text-slate-300 mb-2 ml-1">Kata Sandi</label>
        <input type="password" bind:value={password} required placeholder="••••••••"
               class="glass-input w-full" />
      </div>
      
      <div class="pt-4">
        <button type="submit" disabled={loading}
                class="glass-btn-primary w-full py-3 text-lg">
          {loading ? 'Memproses...' : (isRegister ? 'Buat Warisan Baru' : 'Akses Ingatan')}
        </button>
      </div>
    </form>
    
    <div class="mt-8 text-center text-sm text-slate-400 relative z-10">
      {#if isRegister}
        Sudah memiliki akses? <button class="text-mamet-cyan hover:text-white transition-colors font-medium ml-1" on:click={() => {isRegister=false; errorMsg='';}}>Masuk</button>
      {:else}
        Belum memiliki warisan? <button class="text-mamet-cyan hover:text-white transition-colors font-medium ml-1" on:click={() => {isRegister=true; errorMsg='';}}>Daftar</button>
      {/if}
    </div>
  </div>
</div>
