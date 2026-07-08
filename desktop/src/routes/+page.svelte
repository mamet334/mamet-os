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

<div class="h-screen w-full flex items-center justify-center bg-gray-900 text-white font-sans">
  <div class="bg-gray-800 p-8 rounded-xl shadow-2xl w-96 border border-gray-700">
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">MAMET OS</h1>
      <p class="text-gray-400 mt-2">Warisan Digital Pribadi</p>
    </div>
    
    {#if errorMsg}
      <div class="bg-red-500/20 border border-red-500 text-red-300 px-4 py-2 rounded mb-4 text-sm">
        {errorMsg}
      </div>
    {/if}
    
    <form on:submit|preventDefault={handleSubmit} class="space-y-4">
      <div>
        <label class="block text-sm text-gray-400 mb-1">Email</label>
        <input type="email" bind:value={email} required 
               class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500" />
      </div>
      
      <div>
        <label class="block text-sm text-gray-400 mb-1">Password</label>
        <input type="password" bind:value={password} required 
               class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500" />
      </div>
      
      <button type="submit" disabled={loading}
              class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition-colors disabled:opacity-50">
        {loading ? 'Memproses...' : (isRegister ? 'Daftar' : 'Masuk')}
      </button>
    </form>
    
    <div class="mt-6 text-center text-sm text-gray-400">
      {#if isRegister}
        Sudah punya akun? <button class="text-blue-400 hover:underline" on:click={() => {isRegister=false; errorMsg='';}}>Masuk</button>
      {:else}
        Belum punya akun? <button class="text-blue-400 hover:underline" on:click={() => {isRegister=true; errorMsg='';}}>Daftar</button>
      {/if}
    </div>
  </div>
</div>
