<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import TimelineView from './TimelineView.svelte';
  import GeographicView from './GeographicView.svelte';
  import ViewExplanation from './ViewExplanation.svelte';
  
  let currentView = 'timeline';
  let selectedYear = 2021;
  let data = [];
  let loading = true;
  let error = null;

  async function loadData() {
    loading = true;
    error = null;
    try {
      const dataFile = `./enforcement_actions_all_combined.csv`;
      data = await d3.csv(dataFile, d => ({
        ...d,
        Date: new Date(d.Date),
        MonthYear: d3.timeFormat('%b-%Y')(new Date(d.Date))
      }));
      data.sort((a, b) => a.Date - b.Date);
    } catch (err) {
      console.error('Error loading data:', err);
      error = err.message;
      data = [];
    } finally {
      loading = false;
    }
  }
    

  onMount(() => {
    loadData(selectedYear);
  });
</script>

<main>
  <header>
    <h1>Healthcare Fraud Enforcement Actions (2013-Present)</h1>
    <p class="subtitle">Tracking patterns in healthcare fraud enforcement across time and geography</p>
  </header>

  <nav class="view-controls">
    <button 
      class:active={currentView === 'timeline'} 
      on:click={() => currentView = 'timeline'}>
      Timeline Analysis
    </button>
    <button 
      class:active={currentView === 'geographic'} 
      on:click={() => currentView = 'geographic'}>
      Geographic Distribution
    </button>
  </nav>

  <div class="dashboard-layout">
    <ViewExplanation {currentView} />
    
    <div class="view-container">
      {#if currentView === 'timeline'}
        <TimelineView {data} {selectedYear} />
      {:else if currentView === 'geographic'}
        <GeographicView {data} />
      {/if}
    </div>
  </div>
</main>

<style>
  main {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  header {
    text-align: center;
    margin-bottom: 1rem;
  }

  h1 {
    font-size: 2rem;
    margin: 0;
    color: #2c3e50;
  }

  .subtitle {
    font-size: 1.1rem;
    color: #666;
    margin: 0.5rem 0 0 0;
  }

  .dashboard-layout {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .view-container {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .view-controls {
    margin-bottom: 0.5rem;
    display: flex;
    gap: 1rem;
  }

  .view-controls button {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    background: #f8f9fa;
    cursor: pointer;
    font-weight: bold;
    color: #666;
  }

  .view-controls button.active {
    background: #3498db;
    color: white;
  }

  .view-controls button:hover {
    background: #e9ecef;
  }

  .view-controls button.active:hover {
    background: #2980b9;
  }
</style>