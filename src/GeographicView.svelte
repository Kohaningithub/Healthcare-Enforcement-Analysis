<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  export let data = [];
  let svg;
  let width = 960;
  let height = 500;
  let selectedView = 'state';

  let transitioning = false;
  let transitionMessage = '';

  function normalizeStateName(name) {
    const stateMap = {
      'Mississippi': 'Mississippi',
      'MS': 'Mississippi',
      'California': 'California',
      'CA': 'California',
    };
    return stateMap[name] || name;
  }

  function processData() {
    const counts = new Map();
    
    data.forEach(d => {
      if (d.Agency) {
        let location = null;
        
        if (selectedView === 'state') {
          const patterns = [
            /District of ([^,]+)/i,
            /State of ([^,]+)/i,
            /([^,]+) Attorney General/i,
            /United States Attorney.*?(?:District of|,)\s*([^,]+)/i
          ];

          for (const pattern of patterns) {
            const match = d.Agency.match(pattern);
            if (match) {
              location = match[1].trim();
              break;
            }
          }
        } else {
          const districtMatch = d.Agency.match(/(?:District of|,)\s*([^,]+)\s*(?:District|$)/i);
          if (districtMatch) {
            location = districtMatch[1].trim();
            if (!location.toLowerCase().includes('district')) {
              location += ' District';
            }
          }
        }

        if (location) {
          location = normalizeStateName(location);
          counts.set(location, (counts.get(location) || 0) + 1);
        }
      }
    });

    return counts;
  }

  let tooltip;

  async function drawMap() {
    try {
      const filename = selectedView === 'state' ? 'us-states.json' : 'us-districts.json';
      const response = await fetch(`/${filename}`);
      if (!response.ok) {
        throw new Error(`Failed to load ${filename}`);
      }
      
      const geoData = await response.json();
      const counts = processData();
      const maxCount = Math.max(...counts.values(), 1);
      
      const colorScale = d3.scaleSequential()
        .domain([0, maxCount])
        .interpolator(d3.interpolateBlues);
       
      const svgEl = d3.select(svg)
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', [0, 0, width, height]);
      
      svgEl.selectAll("*").remove();
      
      const projection = d3.geoAlbersUsa()
        .fitSize([width - 100, height - 60], geoData);
      
      const path = d3.geoPath()
        .projection(projection);

      const g = svgEl.append("g")
        .attr("transform", `translate(30, 30)`);

      const regions = g.selectAll("path")
        .data(geoData.features)
        .join("path")
        .attr("d", path)
        .attr("fill", d => {
          const name = selectedView === 'state' ? 
            d.properties.NAME : 
            d.properties.judicial_d || d.properties.NAME;
          const count = counts.get(name) || 0;
          return colorScale(count);
        })
        .attr("stroke", "#fff")
        .attr("stroke-width", 1)
        .attr("class", "region");

      regions.select("title").remove();

      tooltip = svgEl.append("g")
        .attr("class", "tooltip")
        .style("opacity", 0)
        .style("pointer-events", "none");
      
      tooltip.append("rect")
        .attr("class", "tooltip-bg")
        .attr("rx", 4)
        .attr("fill", "white")
        .attr("stroke", "#ccc")
        .attr("stroke-width", 1);
      
      tooltip.append("text")
        .attr("class", "tooltip-text")
        .attr("y", 15)
        .attr("x", 10)
        .attr("fill", "#2c3e50");

      regions
        .style("opacity", 0)
        .style("transform", "scale(0.95)")
        .transition()
        .duration(1200)
        .ease(d3.easeCubicOut)
        .style("opacity", 1)
        .style("transform", "scale(1)")
        .style("fill", d => {
          const name = selectedView === 'state' ? 
            d.properties.NAME : 
            d.properties.judicial_d || d.properties.NAME;
          const count = counts.get(name) || 0;
          return colorScale(count);
        });

      regions
        .on("mouseover", function(event, d) {
          const name = selectedView === 'state' ? 
            d.properties.NAME : 
            d.properties.judicial_d || d.properties.NAME;
          const count = counts.get(name) || 0;

          d3.select(this)
            .transition()
            .duration(200)
            .style("opacity", 0.8)
            .style("stroke", "#2c3e50")
            .style("stroke-width", 2);

          const [x, y] = d3.pointer(event);
          
          tooltip.select("text")
            .text(`${name}: ${count} enforcement actions`);
          
          const bbox = tooltip.select("text").node().getBBox();
          
          tooltip.select("rect")
            .attr("width", bbox.width + 20)
            .attr("height", bbox.height + 20);

          tooltip
            .attr("transform", `translate(${x + 10},${y - 30})`)
            .transition()
            .duration(200)
            .style("opacity", 0.9);
        })
        .on("mouseout", function() {
          d3.select(this)
            .transition()
            .duration(200)
            .style("opacity", 1)
            .style("stroke", "#fff")
            .style("stroke-width", 1);

          tooltip
            .transition()
            .duration(200)
            .style("opacity", 0);
        });

      const legendWidth = 20;
      const legendHeight = 150;
      
      const legend = svgEl.append("g")
        .attr("transform", `translate(${width - 60}, ${height/2 - legendHeight/2})`);

      const defs = svgEl.append("defs");
      const linearGradient = defs.append("linearGradient")
        .attr("id", "legend-gradient")
        .attr("x1", "0%")
        .attr("x2", "0%")
        .attr("y1", "100%")
        .attr("y2", "0%");

      linearGradient.selectAll("stop")
        .data(d3.range(10))
        .enter()
        .append("stop")
        .attr("offset", d => d * 10 + "%")
        .attr("stop-color", d => colorScale(d * maxCount / 9));

      legend.append("rect")
        .attr("width", legendWidth)
        .attr("height", legendHeight)
        .style("fill", "url(#legend-gradient)");

      const legendScale = d3.scaleLinear()
        .domain([0, maxCount])
        .range([legendHeight, 0])
        .nice();

      const legendAxis = d3.axisRight(legendScale)
        .ticks(5)
        .tickSize(6)
        .tickFormat(d3.format("d"));

      legend.append("g")
        .attr("transform", `translate(${legendWidth}, 0)`)
        .call(legendAxis)
        .select(".domain")
        .remove();

      legend.append("text")
        .attr("x", 37)
        .attr("y", -10)
        .attr("text-anchor", "end")
        .attr("font-size", "10px")
        .text("Actions");

    } catch (error) {
      console.error("Error drawing map:", error);
    }
  }

  $: {
    if (selectedView && data && data.length > 0) {
      drawMap();
    }
  }

  onMount(() => {
    if (data && data.length > 0) {
      drawMap();
    }
  });

  async function handleViewChange(newView) {
    transitioning = true;
    
    // 1. Fade current view
    d3.select(svg)
      .transition()
      .duration(300)
      .style("opacity", 0);
      
    // 2. Show context message
    transitionMessage = newView === 'district' ?
      "Switching to judicial districts to show detailed local patterns..." :
      "Switching to state view to show broader regional patterns...";
      
    // 3. Brief pause to read message
    await new Promise(r => setTimeout(r, 800));
    
    // 4. Update view
    selectedView = newView;
    await drawMap();
    
    // 5. Fade in new view
    d3.select(svg)
      .transition()
      .duration(300)
      .style("opacity", 1);
      
    transitioning = false;
    transitionMessage = '';
  }
</script>

<div class="container">
  <div class="view-controls">
    <label>
      <input 
        type="radio" 
        name="view" 
        value="state" 
        checked={selectedView === 'state'}
        on:change={() => handleViewChange('state')}
        disabled={transitioning}
      >
      State View
    </label>
    <label>
      <input 
        type="radio" 
        name="view" 
        value="district"
        checked={selectedView === 'district'}
        on:change={() => handleViewChange('district')}
        disabled={transitioning}
      >
      District View
    </label>
  </div>

  {#if transitionMessage}
    <div class="transition-message">
      {transitionMessage}
    </div>
  {/if}

  <div class="map-container">
    <svg bind:this={svg}></svg>
  </div>
</div>

<style>
  .container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
    height: 100%;
  }

  .view-controls {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .view-controls label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
  }

  .map-container {
    width: 50%;
    height: 450px;
    border: 2px solid #ccc;
    border-radius: 4px;
    background: white;
    overflow: hidden;
  }

  svg {
    width: 100%;
    height: 100%;
    display: block;
  }

  .tooltip-bg {
    fill: white;
    stroke: #ccc;
    stroke-width: 1;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
  }

  .tooltip-text {
    font-size: 12px;
    fill: #2c3e50;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .region {
    transition: all 0.3s ease;
  }

  .region:hover {
    opacity: 0.8;
    cursor: pointer;
    filter: brightness(1.1);
  }

  .transition-message {
    text-align: center;
    padding: 1rem;
    color: #666;
    font-style: italic;
  }
</style>