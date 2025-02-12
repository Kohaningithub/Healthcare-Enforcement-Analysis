<script lang="ts">
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import { interpolatePath } from 'd3-interpolate-path';

  // 定义数据类型
  interface DataItem {
    Date: string;
    Category: string;
    [key: string]: any;
  }

  interface Category {
    id: string;
    label: string;
  }

  interface TimeRange {
    id: string;
    label: string;
  }

  // 导出的属性
  export let data: DataItem[] = [];

  
  let svg: SVGElement;
  let selectedCategory: string = 'all';
  let selectedTimeRange: string = 'all';
  
  let width = 590;
  let height = 350;
  let margin = { top: 20, right: 0, bottom: 65, left: 60 };
  
  const categories: Category[] = [
    { id: 'all', label: 'All Categories' },
    { id: 'Criminal and Civil Actions', label: 'Criminal and Civil Actions' },
    { id: 'State Enforcement Agencies', label: 'State Enforcement Agencies' },
    { id: 'Fraud Self-Disclosures', label: 'Fraud Self-Disclosures' },
    { id: 'CMP and Affirmative Exclusions', label: 'CMP and Affirmative Exclusions' },
    { id: 'CIA Reportable Events', label: 'CIA Reportable Events' },
    { id: 'COVID-19', label: 'COVID-19 Related' },
    { id: 'Grant and Contractor Fraud', label: 'Grant and Contractor Fraud' },
    { id: 'Stipulated Penalties', label: 'Stipulated Penalties and Material Breaches' }
  ];

  const timeRanges: TimeRange[] = [
    { id: 'all', label: 'All Time (2013-Present)' },
    { id: '6m', label: 'Past 6 Months' },
    { id: '1y', label: 'Past 1 Year' },
    { id: '5y', label: 'Past 5 Years' }
  ];

  $: filteredData = data.filter((d: DataItem) => {
    const categoryMatch = 
      selectedCategory === 'all' || 
      d.Category.includes(selectedCategory);
    
    if (selectedTimeRange === 'all') return categoryMatch;
    
    const date = new Date(d.Date);
    const now = new Date();
    const monthsDiff = (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24 * 30);
    const yearsDiff = monthsDiff / 12;
    
    return categoryMatch && (
      (selectedTimeRange === '6m' && monthsDiff <= 6) ||
      (selectedTimeRange === '1y' && monthsDiff <= 12) ||
      (selectedTimeRange === '5y' && yearsDiff <= 5)
    );
  });

  interface TimelineDataItem {
    date: Date;
    value: number;
  }

  $: timelineData = d3.rollups(
    filteredData,
    v => v.length,
    d => d3.timeMonth(new Date(d.Date))
  ).map(([date, count]): TimelineDataItem => ({
    date,
    value: count
  })).sort((a, b) => a.date.getTime() - b.date.getTime());

  $: tableData = timelineData.map((item: TimelineDataItem) => ({
    date: item.date,
    category: categories.find(c => c.id === selectedCategory)?.label || 'All Categories',
    value: item.value
  }));

  let transitionMessage = '';
  
  // Add state to track previous selections
  let previousCategory = 'all';
  let previousTimeRange = 'all';
  let previousData = [];

  function getTransitionContext(newData) {
    // Only update previousData when there's a selection change
    if (selectedCategory !== previousCategory || selectedTimeRange !== previousTimeRange) {
      const context = calculateChange(previousData, newData);
      previousData = [...newData];
      previousCategory = selectedCategory;
      previousTimeRange = selectedTimeRange;
      return context;
    } else {
      // Return null or initial state when there's no change
      return {
        oldAverage: 0,
        newAverage: calculateMonthlyAverage(newData),
        percentChange: 0,
        increased: false,
        newTotal: d3.sum(newData, d => d.value),
        newMonths: newData.length,
        explanation: 'Select a different category or time range to see changes'
      };
    }
  }

  function calculateMonthlyAverage(data) {
    if (!data.length) return 0;
    const total = d3.sum(data, d => d.value);
    return total / data.length;
  }

  function calculateChange(oldData, newData) {
    const oldAvg = calculateMonthlyAverage(oldData);
    const newAvg = calculateMonthlyAverage(newData);
    
    const percentChange = oldAvg === 0 ? 
      100 : 
      ((newAvg - oldAvg) / oldAvg * 100);

    return {
      oldAverage: oldAvg.toFixed(1),
      newAverage: newAvg.toFixed(1),
      percentChange: Math.abs(percentChange).toFixed(1),
      increased: newAvg > oldAvg,
      newTotal: d3.sum(newData, d => d.value),
      newMonths: newData.length,
      explanation: `
        Previous: ${d3.sum(oldData, d => d.value)} actions over ${oldData.length} months (${oldAvg.toFixed(1)} per month)
        Current: ${d3.sum(newData, d => d.value)} actions over ${newData.length} months (${newAvg.toFixed(1)} per month)
      `
    };
  }

  function createChart() {
    if (!svg || !timelineData.length) return;

    const svgEl = d3.select(svg);
    svgEl.selectAll("*").remove();  // Clear existing elements

    // Set up scales
    const x = d3.scaleTime()
      .domain(d3.extent(timelineData, d => d.date))
      .range([margin.left, width - margin.right]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(timelineData, d => d.value)])
      .nice()
      .range([height - margin.bottom, margin.top]);

    // Create line
    const line = d3.line()
      .x(d => x(d.date))
      .y(d => y(d.value))
      .curve(d3.curveMonotoneX);

    // Add line path
    svgEl.append("path")
      .attr("class", "line-path")
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 2)
      .attr("d", line(timelineData));

    // Add axes
    svgEl.append("g")
      .attr("class", "x-axis")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x)
        .ticks(selectedTimeRange === 'all' ? d3.timeYear.every(1) : d3.timeMonth.every(3))
        .tickFormat(d3.timeFormat("%b %Y")))
      .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    svgEl.append("g")
      .attr("class", "y-axis")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y));

    // Add dots
    svgEl.selectAll(".dot")
      .data(timelineData)
      .join("circle")
      .attr("class", "dot")
      .attr("cx", d => x(d.date))
      .attr("cy", d => y(d.value))
      .attr("r", 3)
      .attr("fill", "steelblue");
  }

  let currentContext = null; // Store the current context
  let transitionInProgress = false;

  async function updateChart(newData) {
    const context = getTransitionContext(newData);
    currentContext = context;
    transitionInProgress = true;
    
    const svgEl = d3.select(svg);
    
    // Add transition guide overlay
    const overlay = svgEl.append("g")
      .attr("class", "transition-overlay")
      .style("opacity", 0);
    
    // Add direction indicator with meaningful text
    overlay.append("text")
      .attr("class", "transition-text")
      .attr("x", width / 2)
      .attr("y", height / 2)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .text(context.increased ? 
        `↑ Activity increased by ${context.percentChange}%` :
        `↓ Activity decreased by ${context.percentChange}%`);

    // Fade in overlay
    await overlay.transition()
      .duration(300)
      .style("opacity", 1)
      .end();
    
    // Fade out old chart
    await svgEl.select(".line-path")
      .transition()
      .duration(400)
      .style("opacity", 0.3)
      .end();
    
    // Update chart
    createChart();
    
    // Highlight the change
    svgEl.select(".line-path")
      .style("stroke-width", "4")
      .style("stroke", context.increased ? "#2ecc71" : "#e74c3c")
      .transition()
      .duration(750)
      .style("stroke-width", "2")
      .style("stroke", "steelblue");
    
    // Remove overlay
    overlay.remove();
    
    transitionInProgress = false;
  }

  // Watch for data changes
  $: {
    if (timelineData && timelineData.length > 0) {
      if (!svg) {
        // Initial creation
        setTimeout(createChart, 0);
      } else {
        // Update with transition
        updateChart(timelineData);
      }
    }
  }

  onMount(() => {
    if (timelineData && timelineData.length > 0) {
      createChart();
    }
  });
</script>

<div class="timeline-container">
  <div class="controls">
    <div class="control-group">
      <label for="category">Category:</label>
      <select id="category" bind:value={selectedCategory}>
        {#each categories as category}
          <option value={category.id}>{category.label}</option>
        {/each}
      </select>
    </div>

    <div class="control-group">
      <label for="timeRange">Time Range:</label>
      <select id="timeRange" bind:value={selectedTimeRange}>
        {#each timeRanges as range}
          <option value={range.id}>{range.label}</option>
        {/each}
      </select>
    </div>
  </div>

  <div class="analysis-context">
    {#if currentContext}
      <div class="context-panel" class:transitioning={transitionInProgress}>
        <h4>Analysis Context</h4>
        <div class="metric">
          <span class="label">Current Average:</span>
          <span class="value">{currentContext.newAverage} actions/month</span>
        </div>
        <div class="metric">
          <span class="label">Change in Monthly Average:</span>
          <div class="value-group">
            <span class="value" class:increased={currentContext.increased} class:decreased={!currentContext.increased}>
              {currentContext.increased ? '↑' : '↓'} {currentContext.percentChange}%
            </span>
            <div class="tooltip">
              <span class="tooltip-indicator">What's this? »</span>
              <span class="tooltiptext">
                This percentage shows how the monthly average has changed.
                <br><br>
                {currentContext.explanation}
              </span>
            </div>
          </div>
        </div>
        <div class="metric">
          <span class="label">Current Period:</span>
          <span class="value">{currentContext.newTotal} actions over {currentContext.newMonths} months</span>
        </div>
      </div>
    {/if}
  </div>

  <div class="content-wrapper">
    <div class="chart-section">
      <div class="stats-summary">
        <div class="stat-box">
          <h3>Total Actions</h3>
          <p>{filteredData.length}</p>
        </div>
      </div>
      
      <div class="chart-container">
        <svg bind:this={svg}></svg>
      </div>
    </div>

    <div class="data-preview">
      <h3 class="preview-header">Data Preview</h3>
      <div class="table-container">
        {#each tableData as item (item.date)}
          <div class="table-row">
            <td>{item.date.toLocaleDateString()}</td>
            <td>{item.category}</td>
            <td>{item.value}</td>
          </div>
        {/each}
      </div>
      <div class="table-footer">
        Total rows: {timelineData.length}
      </div>
    </div>
  </div>

  <!-- Analysis Guide moved here, below everything -->
  <div class="analysis-guide-container">
    <h3>Using the Timeline Analysis Tools</h3>
    
    <div class="guide-section">
      <h4>Category and Time Range Combinations</h4>
      <p>Combine different categories and time ranges to uncover specific patterns:</p>
      <ul>
        <li>
          <strong>Start Broad:</strong> View "All Categories" over "All Time" to identify major trends and unusual spikes
        </li>
        <li>
          <strong>Drill Down:</strong> When you spot an interesting period, narrow the time range to "Past 1 Year" or "Past 6 Months" for detailed analysis
        </li>
        <li>
          <strong>Compare Categories:</strong> Switch between categories within the same time period to see how different types of fraud evolve
        </li>
      </ul>
    </div>

    <div class="guide-section">
      <h4>Example Analysis Workflows</h4>
      <ol>
        <li>
          <strong>COVID-19 Impact Analysis:</strong>
          <ul>
            <li>Select "COVID-19 Related" category</li>
            <li>Compare "Past 1 Year" vs "All Time" to see pandemic-era changes</li>
            <li>Switch to "All Categories" to see overall enforcement patterns during the same period</li>
          </ul>
        </li>
        <li>
          <strong>Enforcement Priority Shifts:</strong>
          <ul>
            <li>Start with "Criminal and Civil Actions"</li>
            <li>Use "Past 5 Years" to identify trends</li>
            <li>Compare with "State Enforcement Agencies" to see jurisdictional patterns</li>
          </ul>
        </li>
      </ol>
    </div>

    <div class="guide-section">
      <h4>Understanding the Metrics</h4>
      <ul>
        <li>
          <strong>Monthly Average:</strong> Shows typical enforcement activity level - useful for comparing different time periods
        </li>
        <li>
          <strong>Percentage Change:</strong> Indicates how current selection differs from previous - helps identify significant shifts
        </li>
        <li>
          <strong>Total Actions:</strong> Absolute number of cases - important for understanding overall enforcement volume
        </li>
      </ul>
    </div>
  </div>
</div>

<style>
  .timeline-container {
    width: 100%;
  }

  .content-wrapper {
    display: grid;
    grid-template-columns: minmax(600px, 39%) minmax(250px, 28%);
    gap: 1%;
  }

  .chart-section {
    order: 1;
    padding-right: 1rem;
    background: white; 
    min-width: 700px;
  }


  .controls {
    display: flex;
    gap: 4rem;
    padding: 0.75rem;
  }

  label {
    font-size: 1.1rem;
    font-weight: 800;
    color: #2c3e50;
  }

  .chart-container {
    width: 100%;
    height: 400px;  /* Explicit height */
    position: relative;
  }

  svg {
    width: 100%;
    height: 100%;
  }

  .data-preview {
    order: 2;
    width: 300px; 
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
    height: 400px;
    overflow: hidden;
    position: relative;
  }

  .preview-header {
    margin: 0;
    padding: 1rem;
    background: #f8f9fa;
    border-bottom: 1px solid #eee;
    border-radius: 8px 8px 0 0;
    color: #2c3e50;
    font-size: 1rem;
    text-align: center !important; /* 强制居中 */
    width: 100%;
    box-sizing: border-box;
    display: block;
  }

  .data-preview h3 {
    margin: 0;
    padding: 1rem;
    background: #f8f9fa;
    border-bottom: 1px solid #eee;
    color: #2c3e50;
    font-size: 1rem;
    text-align: center;
    width: 100%;
    box-sizing: border-box;
  }
  
  .table-container {
    flex: 1;
    overflow-y: auto;
        width: 100%;
    
  }

  .table-row {
    display: grid;
    grid-template-columns: 63px 190px 30px;  /* 固定每列的宽度 */
    border-bottom: 1px solid #eee;
  }

  .table-row td {
    padding: 8px 5px;
    font-size: 10px;
    line-height: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .table-row td:first-child {  /* 日期列 */
    border-right: 1px solid #eee;
  }

  .table-row td:nth-child(2) {  /* 类别列 */
    border-right: 1px solid #eee;
    padding-left: 6rpx;
  }

  .table-row td:last-child {  /* 数值列 */
    text-align: left;
    padding-right: 0px;
  }


  .table-footer {
    text-align: center;
    font-size: 0.75rem;

  }

  .stats-summary {
    width: 200px;
    margin: 0 auto 1rem auto;
    
  }

  .stat-box {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 5px;
    text-align: center;
    border: 1px solid #eee;
  }

  .stat-box h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.0 rem;
    color: #2c3e50;
  }

  .stat-box p {
    margin: 0;
    font-size: 2.5 rem;
    font-weight: bold;
    color: #3498db;
  }

  .transition-message {
    text-align: center;
    padding: 0.5rem;
    color: #666;
    font-style: italic;
    min-height: 4rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    justify-content: center;
  }

  .analysis-context {
    margin: 1rem 0;
    padding: 0 1rem;
  }

  .context-panel {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    transition: opacity 0.3s ease;
  }

  .context-panel.transitioning {
    opacity: 0.7;
  }

  .context-panel h4 {
    margin: 0 0 0.5rem 0;
    color: #2c3e50;
    font-size: 0.9rem;
  }

  .metric {
    position: relative;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid #eee;
  }

  .metric:last-child {
    border-bottom: none;
  }

  .label {
    color: #666;
    font-size: 0.85rem;
  }

  .value {
    font-weight: 600;
    color: #2c3e50;
    margin-right: 8px;
  }

  .increased {
    color: #2ecc71;
  }

  .decreased {
    color: #e74c3c;
  }

  .tooltip {
    position: relative;
    display: inline-block;
    margin-left: 8px;
    cursor: help;
  }

  .tooltiptext {
    visibility: hidden;
    width: 300px;
    background-color: #2c3e50;
    color: #fff;
    text-align: left;
    border-radius: 6px;
    padding: 10px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    transition: opacity 0.3s;
    font-size: 0.8rem;
    line-height: 1.4;
    white-space: pre-line;
  }

  .tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
  }

  .analysis-guide-container {
    margin-top: 3rem;  /* Increased margin to separate from content above */
    padding: 2rem;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #3498db;
    max-width: 1000px;  /* Limit width for better readability */
    margin-left: auto;
    margin-right: auto;
  }

  .analysis-guide-container h3 {
    color: #2c3e50;
    font-size: 1.2rem;
    margin: 0 0 1.5rem 0;
  }

  .guide-section {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: white;
    border-radius: 6px;
    border-left: 3px solid #3498db;
  }

  .guide-section:last-child {
    margin-bottom: 0;
  }

  .guide-section h4 {
    color: #2c3e50;
    margin: 0 0 1rem 0;
    font-size: 1rem;
  }

  .guide-section ul, 
  .guide-section ol {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
  }

  .guide-section li {
    margin-bottom: 0.75rem;
    font-size: 0.9rem;
    line-height: 1.5;
    color: #34495e;
  }

  .guide-section strong {
    color: #2c3e50;
  }

  .tooltip-indicator {
    color: #3498db;
    font-size: 0.8rem;
    text-decoration: underline dotted;
    cursor: help;
  }

  .value-group {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .value {
    font-weight: 600;
    color: #2c3e50;
    text-align: right;
    min-width: 60px; /* Ensures consistent spacing */
  }

  .increased {
    color: #2ecc71;
  }

  .decreased {
    color: #e74c3c;
  }

  .tooltip-indicator {
    color: #3498db;
    font-size: 0.8rem;
    text-decoration: underline dotted;
    cursor: help;
  }

  .transition-overlay {
    pointer-events: none;
  }
  
  .transition-text {
    font-size: 1.2rem;
    font-weight: bold;
    fill: #2c3e50;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,0.1));
  }
</style>