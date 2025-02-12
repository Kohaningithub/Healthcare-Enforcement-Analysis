<script>
    export let currentView;
  </script>
  
  <div class="explanation">
    <section class="overview">
      <h2>Understanding Healthcare Fraud Enforcement</h2>
      <p>
        Healthcare fraud—like billing for services never provided or overcharging for medical care—costs 
        billions each year. This dashboard shows how government investigators track down and stop these 
        frauds. You can explore when and where enforcement actions happen, helping us understand which 
        types of fraud are most common and how they're being addressed.
      </p>
    </section>

    <section class="methodology">
      <h3>Data Collection Methodology</h3>
      <p>
        This dataset was compiled through automated web scraping of the HHS OIG enforcement action database, 
        capturing cases from 2013 to present. 
    </section>

    <div class="data-source">
      <p>Data source: <a href="https://oig.hhs.gov" target="_blank" rel="noopener">HHS OIG</a></p>
      <p>Map: <a href="https://data.ojp.usdoj.gov/Shapefile/US-Attorney-Districts-Shapefile-simplified/vigs-nsnz/about_data" target="_blank" rel="noopener">
        US Attorney Districts Shapefile</a> | 
        <a href="https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html" target="_blank" rel="noopener">
        Census State Shapefile</a></p>
      <p>Code: <a href="https://github.com/Kohaningithub/Data-Collection-Method" target="_blank" rel="noopener">GitHub</a></p>
    </div>

  </div>

    {#if currentView === 'geographic'}
      <section class="analysis-guide">
        <h3>Start Your Investigation:</h3>
        <ul>
          <li>Which regions face the highest enforcement activity?</li>
          <li>How do enforcement patterns differ between judicial districts?</li>
          <li>Are there geographic clusters of healthcare fraud cases?</li>
        </ul>

        <h3>How to Analyze the Data:</h3>
        <ol>
          <li>Start with the state view to identify high-activity regions</li>
          <li>Switch to district view to understand local enforcement patterns</li>
          <li>Compare neighboring districts to identify regional trends</li>
          <li>Look for clusters that might indicate coordinated enforcement efforts</li>
        </ol>
      </section>
    {:else}
      <section class="analysis-guide">
        <h3>Key Questions This View Answers:</h3>
        <ul>
          <li>How have enforcement patterns changed over time?</li>
          <li>Are there seasonal patterns in enforcement actions?</li>
          <li>What impact did major policy changes or events have?</li>
        </ul>

        <h3>How to Analyze the Data:</h3>
        <ol>
          <li>Start with the full timeline to identify long-term trends</li>
          <li>Zoom into specific periods of interest</li>
          <li>Compare year-over-year patterns</li>
          <li>Look for correlations with known policy changes or initiatives</li>
        </ol>
      </section>
    {/if}
  

  <style>
    .explanation {
      max-width: 800px;
      margin: 0 auto;
      line-height: 1.6;
    }

    .overview {
      margin-bottom: 2rem;
    }

    .analysis-guide {
      background: #f8f9fa;
      padding: 1.5rem;
      border-radius: 8px;
      margin-bottom: 1.5rem;
      text-align: center;
    }

    .explanation h3 {
      font-size: 0.9rem;
      margin: 0.04 0;
      color: #34495e;
    }

    .explanation h2 {
      font-size: 0.9rem;
      margin: 0 1 0.5rem 0;
      color: #34495e;
    }

    .explanation p {
      margin: 0rem 0;
      color: #34495e;
      text-align: left; 
      line-height: 1.3;
    }

    .explanation ul {
      margin: 0rem 0 0rem 0rem;
      padding: 0;
      color: #34495e;
      text-align: left;
    }

    .explanation li {
      margin-bottom: 0.3rem;
    }

    .explanation a {
      color: #3498db;
      text-decoration: none;
    }

    .explanation a:hover {
      text-decoration: underline;
    }

    .data-source {
      font-size: 0.75rem;
      margin-top: 0.2rem;
      padding-top: 0rem;
      border-top: 1px solid #eee;
    }

    p {
      line-height: 1.3;
      color: #2c3e50;
    }

    .methodology {
      background: #f8f9fa;
      padding: 1rem;
      border-radius: 8px;
      margin-bottom: 1.5rem;
      border-left: 4px solid #3498db;
    }

    .method-list {
      margin: 0.5rem 0;
      padding-left: 1.5rem;
      font-size: 0.9rem;
    }

    .method-note {
      font-size: 0.85rem;
      color: #666;
      margin-top: 0.5rem;
      font-style: italic;
    }

    .guide-section {
      margin-bottom: 1.5rem;
      padding: 1rem;
      background: white;
      border-radius: 6px;
      border-left: 3px solid #3498db;
    }

    .guide-section h4 {
      color: #2c3e50;
      margin: 0 0 0.5rem 0;
      font-size: 0.9rem;
    }

    .guide-section ul, .guide-section ol {
      margin: 0.5rem 0;
      padding-left: 1.2rem;
    }

    .guide-section li {
      margin-bottom: 0.5rem;
      font-size: 0.85rem;
      line-height: 1.4;
    }

    .guide-section strong {
      color: #2c3e50;
    }

    .guide-section ul ul, .guide-section ol ul {
      margin: 0.3rem 0;
      color: #666;
    }

  </style>

