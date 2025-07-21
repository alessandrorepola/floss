
// PyFault Enhanced HTML Report JavaScript
// Embedded data to avoid CORS issues
const SUNBURST_DATA = {"name": "PyFault", "children": [{"name": "src", "children": [{"name": "equilateral.py", "value": 6, "score": 0.5202200572599404, "max_score": 0.7071067811865475, "suspiciousness": 0.5202200572599404}, {"name": "isosceles.py", "value": 5, "score": 0.4, "max_score": 0.5, "suspiciousness": 0.4}], "value": 11}]};
const RANKING_DATA = {"items": [{"name": "equilateral.py:10", "element": "equilateral.py:10", "suspiciousness": 0.7071067811865475, "score": 0.7071067811865475, "rank": 1, "file": "equilateral.py", "line": 10}, {"name": "equilateral.py:11", "element": "equilateral.py:11", "suspiciousness": 0.7071067811865475, "score": 0.7071067811865475, "rank": 2, "file": "equilateral.py", "line": 11}, {"name": "equilateral.py:13", "element": "equilateral.py:13", "suspiciousness": 0.7071067811865475, "score": 0.7071067811865475, "rank": 3, "file": "equilateral.py", "line": 13}, {"name": "equilateral.py:5", "element": "equilateral.py:5", "suspiciousness": 0.5, "score": 0.5, "rank": 4, "file": "equilateral.py", "line": 5}, {"name": "equilateral.py:7", "element": "equilateral.py:7", "suspiciousness": 0.5, "score": 0.5, "rank": 5, "file": "equilateral.py", "line": 7}, {"name": "isosceles.py:5", "element": "isosceles.py:5", "suspiciousness": 0.5, "score": 0.5, "rank": 6, "file": "isosceles.py", "line": 5}, {"name": "isosceles.py:6", "element": "isosceles.py:6", "suspiciousness": 0.5, "score": 0.5, "rank": 7, "file": "isosceles.py", "line": 6}, {"name": "isosceles.py:8", "element": "isosceles.py:8", "suspiciousness": 0.5, "score": 0.5, "rank": 8, "file": "isosceles.py", "line": 8}, {"name": "isosceles.py:10", "element": "isosceles.py:10", "suspiciousness": 0.5, "score": 0.5, "rank": 9, "file": "isosceles.py", "line": 10}, {"name": "equilateral.py:8", "element": "equilateral.py:8", "suspiciousness": 0.0, "score": 0.0, "rank": 10, "file": "equilateral.py", "line": 8}, {"name": "isosceles.py:11", "element": "isosceles.py:11", "suspiciousness": 0.0, "score": 0.0, "rank": 11, "file": "isosceles.py", "line": 11}]};

document.addEventListener('DOMContentLoaded', function() {
    console.log('PyFault enhanced report loaded');
    
    // Initialize interactive features
    initializeSorting();
    initializeTooltips();
    
    // Load visualizations with embedded data
    loadVisualizationsWithEmbeddedData();
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

function loadVisualizationsWithEmbeddedData() {
    // Check if D3.js is available
    if (typeof d3 !== 'undefined') {
        console.log('D3.js found, loading visualizations with embedded data');
        loadSunburstChartWithData(SUNBURST_DATA);
        loadRankingChartWithData(RANKING_DATA);
    } else {
        console.log('D3.js not found, loading from CDN');
        const script = document.createElement('script');
        script.src = 'https://d3js.org/d3.v7.min.js';
        script.crossOrigin = 'anonymous';
        
        script.onload = function() {
            console.log('D3.js loaded from CDN');
            loadSunburstChartWithData(SUNBURST_DATA);
            loadRankingChartWithData(RANKING_DATA);
        };
        
        script.onerror = function() {
            console.warn('Failed to load D3.js from CDN');
            showVisualizationError();
        };
        
        document.head.appendChild(script);
        
        // Fallback timeout
        setTimeout(() => {
            if (typeof d3 === 'undefined') {
                console.warn('D3.js loading timeout');
                showVisualizationError();
            }
        }, 10000);
    }
}

function showVisualizationError() {
    const sunburstContainer = document.getElementById('sunburst-chart');
    const rankingContainer = document.getElementById('ranking-chart');
    
    const errorMessage = `
        <div style="text-align: center; padding: 40px; color: #6c757d;">
            <h4>📊 Interactive Visualizations</h4>
            <p>Visualizations require an internet connection to load D3.js library.</p>
            <p>Data is available in the tables below.</p>
        </div>
    `;
    
    if (sunburstContainer) {
        sunburstContainer.innerHTML = errorMessage;
    }
    if (rankingContainer) {
        rankingContainer.innerHTML = errorMessage;
    }
}

function loadSunburstChartWithData(data) {
    const container = document.getElementById('sunburst-chart');
    if (!container) {
        console.warn('Sunburst container not found');
        return;
    }
    
    console.log('Creating sunburst chart with embedded data:', data);
    
    try {
        createSunburstChart(container, data);
    } catch (error) {
        console.error('Error creating sunburst chart:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #dc3545;">
                ⚠️ Error creating sunburst visualization
            </div>
        `;
    }
}

function loadRankingChartWithData(data) {
    const container = document.getElementById('ranking-chart');
    if (!container) {
        console.warn('Ranking container not found');
        return;
    }
    
    console.log('Creating ranking chart with embedded data:', data);
    
    try {
        createRankingChart(container, data);
    } catch (error) {
        console.error('Error creating ranking chart:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #dc3545;">
                ⚠️ Error creating ranking visualization
            </div>
        `;
    }
}

function createSunburstChart(container, data) {
    // Clear container
    container.innerHTML = '';
    
    console.log('Sunburst data received:', data);
    
    if (!data || !data.children || data.children.length === 0) {
        console.warn('No sunburst data available');
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #6c757d;">
                <p>📊 No data available for sunburst visualization</p>
                <p>Debug: data = ${JSON.stringify(data)}</p>
            </div>
        `;
        return;
    }
    
    const width = container.clientWidth || 600;
    const height = 500;
    const radius = Math.min(width, height) / 2 - 10;
    
    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${width / 2},${height / 2})`);
    
    // Create partition layout
    const partition = d3.partition()
        .size([2 * Math.PI, radius]);
    
    // Create hierarchy
    const root = d3.hierarchy(data)
        .sum(d => d.value || 1)
        .sort((a, b) => (b.value || 0) - (a.value || 0));
    
    partition(root);
    
    console.log('Sunburst hierarchy created with', root.descendants().length, 'nodes');
    
    // Color scale
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    
    // Create arc generator
    const arc = d3.arc()
        .startAngle(d => d.x0)
        .endAngle(d => d.x1)
        .innerRadius(d => d.y0)
        .outerRadius(d => d.y1);
    
    // Add arcs
    const paths = svg.selectAll('path')
        .data(root.descendants().filter(d => d.depth > 0))
        .enter().append('path')
        .attr('d', arc)
        .style('fill', d => color(d.depth))
        .style('stroke', '#fff')
        .style('stroke-width', 1)
        .style('opacity', 0.8)
        .on('mouseover', function(event, d) {
            d3.select(this).style('opacity', 1);
            showTooltip(event, d);
        })
        .on('mouseout', function(event, d) {
            d3.select(this).style('opacity', 0.8);
            hideTooltip();
        });
    
    console.log('Sunburst paths created:', paths.size());
    
    // Add labels for larger segments
    const labels = svg.selectAll('text')
        .data(root.descendants().filter(d => d.depth > 0 && (d.x1 - d.x0) > 0.1))
        .enter().append('text')
        .attr('transform', d => {
            const angle = (d.x0 + d.x1) / 2;
            const radius = (d.y0 + d.y1) / 2;
            return `rotate(${angle * 180 / Math.PI - 90}) translate(${radius},0) rotate(${angle > Math.PI ? 180 : 0})`;
        })
        .attr('dy', '0.35em')
        .style('text-anchor', d => (d.x0 + d.x1) / 2 > Math.PI ? 'end' : 'start')
        .style('font-size', '12px')
        .style('fill', '#333')
        .text(d => d.data.name);
    
    console.log('Sunburst labels created:', labels.size());
    
    if (paths.size() === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #dc3545;">
                <p>⚠️ No visual elements created for sunburst</p>
                <p>Debug: ${root.descendants().length} total nodes, ${root.descendants().filter(d => d.depth > 0).length} visible nodes</p>
            </div>
        `;
    }
}

function createRankingChart(container, data) {
    // Clear container
    container.innerHTML = '';
    
    console.log('Ranking data received:', data);
    
    if (!data || !data.items || data.items.length === 0) {
        console.warn('No ranking data available');
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #6c757d;">
                <p>📊 No ranking data available</p>
                <p>Debug: data = ${JSON.stringify(data)}</p>
            </div>
        `;
        return;
    }
    
    const width = container.clientWidth || 600;
    const height = 400;
    const margin = {top: 20, right: 30, bottom: 60, left: 100};
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    
    // Take top 20 items for better visualization
    const topItems = data.items.slice(0, 20);
    console.log('Creating ranking chart with', topItems.length, 'items');
    
    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Scales
    const maxScore = d3.max(topItems, d => d.suspiciousness || 0);
    console.log('Max suspiciousness score:', maxScore);
    
    const x = d3.scaleLinear()
        .domain([0, maxScore || 1])
        .range([0, chartWidth]);
    
    const y = d3.scaleBand()
        .domain(topItems.map((d, i) => i))  // Use index instead of name for better spacing
        .range([0, chartHeight])
        .padding(0.1);
    
    // Color scale based on suspiciousness
    const colorScale = d3.scaleSequential(d3.interpolateReds)
        .domain([0, maxScore || 1]);
    
    // Add bars
    const bars = g.selectAll('.bar')
        .data(topItems)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', 0)
        .attr('y', (d, i) => y(i))
        .attr('width', d => x(d.suspiciousness || 0))
        .attr('height', y.bandwidth())
        .style('fill', d => colorScale(d.suspiciousness || 0))
        .style('stroke', '#333')
        .style('stroke-width', 0.5)
        .on('mouseover', function(event, d) {
            showTooltip(event, d);
        })
        .on('mouseout', hideTooltip);
    
    console.log('Ranking bars created:', bars.size());
    
    // Add x-axis
    g.append('g')
        .attr('transform', `translate(0,${chartHeight})`)
        .call(d3.axisBottom(x))
        .append('text')
        .attr('x', chartWidth / 2)
        .attr('y', 40)
        .style('text-anchor', 'middle')
        .style('fill', '#333')
        .text('Suspiciousness Score');
    
    // Add y-axis with element names
    g.append('g')
        .call(d3.axisLeft(y).tickFormat(i => {
            const item = topItems[i];
            return item ? item.name.slice(0, 30) + (item.name.length > 30 ? '...' : '') : '';
        }))
        .selectAll('text')
        .style('font-size', '10px');
    
    if (bars.size() === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #dc3545;">
                <p>⚠️ No bars created for ranking chart</p>
                <p>Debug: ${topItems.length} items processed</p>
            </div>
        `;
    }
}

// Tooltip functions
let tooltip;

function showTooltip(event, d) {
    if (!tooltip) {
        tooltip = d3.select('body').append('div')
            .style('position', 'absolute')
            .style('padding', '10px')
            .style('background', 'rgba(0, 0, 0, 0.8)')
            .style('color', 'white')
            .style('border-radius', '5px')
            .style('pointer-events', 'none')
            .style('opacity', 0);
    }
    
    let content = `<strong>${d.data?.name || d.name}</strong>`;
    if (d.suspiciousness !== undefined) {
        content += `<br/>Suspiciousness: ${d.suspiciousness.toFixed(4)}`;
    }
    if (d.value !== undefined) {
        content += `<br/>Value: ${d.value}`;
    }
    
    tooltip.html(content)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
        .transition()
        .duration(200)
        .style('opacity', 1);
}

function hideTooltip() {
    if (tooltip) {
        tooltip.transition()
            .duration(200)
            .style('opacity', 0);
    }
}

// Initialize sorting and other interactive features
function initializeSorting() {
    const tables = document.querySelectorAll('.ranking-table');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => sortTable(table, index));
        });
    });
}

function initializeTooltips() {
    // Tooltip initialization code would go here
    console.log('Tooltips initialized');
}

function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aVal = a.cells[column].textContent.trim();
        const bVal = b.cells[column].textContent.trim();
        
        // Try to parse as numbers
        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return bNum - aNum; // Descending for numbers
        }
        
        return aVal.localeCompare(bVal);
    });
    
    rows.forEach(row => tbody.appendChild(row));
}
        