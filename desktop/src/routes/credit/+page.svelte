<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { fade } from 'svelte/transition';
  
  let lines: string[] = [];
  let isPlaying = false;
  
  onMount(async () => {
    try {
      const res = await fetch('/credit.txt');
      if (res.ok) {
        const text = await res.text();
        lines = text.split('\n');
      } else {
        lines = ["MAMET OS", "Warisan Digital Pribadi", "", "Gagal memuat teks credit."];
      }
    } catch (e) {
      lines = ["MAMET OS", "Warisan Digital Pribadi"];
    }
    
    // Start animation shortly after load
    setTimeout(() => {
      isPlaying = true;
    }, 500);
  });
  
  function skip() {
    goto('/workspace');
  }
</script>

<style>
  .credits-container {
    perspective: 1000px;
    overflow: hidden;
  }
  
  .credits-text {
    animation-name: crawl;
    animation-timing-function: linear;
    animation-fill-mode: forwards;
    transform-origin: 50% 100%;
  }
  
  @keyframes crawl {
    0% {
      transform: translateY(100vh);
      opacity: 0;
    }
    5% {
      opacity: 1;
    }
    100% {
      transform: translateY(calc(-100% + 100vh));
      opacity: 1;
    }
  }
</style>

<div class="h-screen w-full bg-black text-white relative credits-container font-serif">
  <button on:click={skip} class="absolute top-6 right-6 z-50 text-gray-400 hover:text-white bg-white/10 px-4 py-2 rounded-full backdrop-blur transition border border-white/20">
    ⏭️ Lewati
  </button>
  
  {#if isPlaying}
    <div class="absolute w-full h-full flex justify-center items-start" in:fade={{duration: 1000}}>
      <div class="w-full max-w-2xl text-center credits-text px-8 space-y-4 pb-[50vh]" style="animation-duration: {Math.max(30, lines.length * 2.0)}s;">
        {#each lines as line}
          {#if line.trim() === ''}
            <div class="h-8"></div>
          {:else if line.startsWith('---')}
            <div class="w-24 h-px bg-white/30 mx-auto my-8"></div>
          {:else if line.match(/^[A-Z\s\?\,]+$/)}
            <h2 class="text-2xl font-bold tracking-widest text-mamet-cyan mt-12 mb-6 drop-shadow-[0_0_10px_rgba(0,219,233,0.5)]">{line}</h2>
          {:else}
            <p class="text-xl leading-relaxed text-slate-300">{line}</p>
          {/if}
        {/each}
      </div>
    </div>
  {/if}
</div>
