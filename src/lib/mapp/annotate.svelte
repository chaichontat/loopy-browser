<script lang="ts">
  import { annotating } from '$lib/store';
  import * as d3 from 'd3';
  import { makeDownload } from '../utils';

  function handleNewKey(name: string | null) {
    if (name === null) {
      alert('Empty name.');
      return;
    }
    $annotating.keys.push(name);
    $annotating.keys = $annotating.keys;
  }
</script>

<section class="flex flex-col gap-y-2">
  <p class="mt-2">Annotate</p>
  <div class="flex gap-x-6">
    {#each $annotating.keys as key, i}
      <label class="flex items-center gap-x-1 hover:underline">
        <div class="h-3 w-3" style={`background-color: ${d3.schemeTableau10[i % 10]}`} />
        <button on:click={() => ($annotating.curr = key)} class:font-bold={$annotating.curr === key}
          >{key}</button
        >
      </label>
    {/each}
  </div>

  <label>
    <input type="checkbox" bind:checked={$annotating.show} />
    Show overlay
  </label>

  <button
    class="button my-0 flex-grow py-2 transition-colors duration-75 dark:bg-slate-800 hover:dark:bg-slate-500"
    on:click={() => handleNewKey(prompt('Enter new key.'))}>Add</button
  >

  <button
    class="button my-0 flex-grow py-2 transition-colors duration-75 dark:bg-slate-800 hover:dark:bg-slate-500"
    on:click={() => {
      if ($annotating.spots)
        makeDownload({ name: 'annotations.csv', s: $annotating.spots, type: 'text/csv' });
    }}>Download</button
  >
</section>

<style lang="postcss">
</style>
