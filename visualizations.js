// Global variables
let allData = [];
let minGoalsFilter = 0;

// League mapping - maps team names to their leagues
function getLeague(team) {
    const teamLower = team.toLowerCase();
    
    // Premier League (England)
    const premierLeagueTeams = [
        'arsenal', 'aston villa', 'bournemouth', 'brentford', 'brighton', 'chelsea',
        'crystal palace', 'everton', 'fulham', 'leicester city', 'liverpool',
        'manchester city', 'manchester utd', 'newcastle utd', 'nott\'ham forest',
        'tottenham', 'west ham', 'wolves'
    ];
    
    // La Liga (Spain)
    const laLigaTeams = [
        'alavés', 'athletic club', 'atlético madrid', 'barcelona', 'betis', 'celta vigo',
        'espanyol', 'getafe', 'girona', 'las palmas', 'leganés', 'mallorca',
        'osasuna', 'rayo vallecano', 'real madrid', 'real sociedad', 'sevilla',
        'valencia', 'valladolid', 'villareal', 'villarreal'
    ];
    
    // Serie A (Italy)
    const serieATeams = [
        'atalanta', 'bologna', 'como', 'empoli', 'fiorentina', 'genoa', 'inter',
        'juventus', 'lazio', 'milan', 'monza', 'napoli', 'parma', 'roma',
        'torino', 'udinese', 'venezia', 'verona', 'hellas verona'
    ];
    
    // Bundesliga (Germany)
    const bundesligaTeams = [
        'augsburg', 'bayern munich', 'bayer leverkusen', 'leverkusen', 'borussia dortmund',
        'dortmund', 'freiburg', 'hoffenheim', 'mainz 05', 'st. pauli', 'werder bremen',
        'wolfsburg', 'eint frankfurt', 'frankfurt'
    ];
    
    // Ligue 1 (France)
    const ligue1Teams = [
        'angers', 'auxerre', 'brest', 'lens', 'lille', 'lyon', 'marseille', 'monaco',
        'montpellier', 'nantes', 'nice', 'psg', 'paris saint-germain', 'reims',
        'rennes', 'saint-étienne', 'strasbourg', 'toulouse'
    ];
    
    // Eredivisie (Netherlands) - if any
    const eredivisieTeams = ['ajax', 'psv', 'feyenoord'];
    
    // Other leagues
    if (premierLeagueTeams.some(t => teamLower.includes(t))) return 'Premier League';
    if (laLigaTeams.some(t => teamLower.includes(t))) return 'La Liga';
    if (serieATeams.some(t => teamLower.includes(t))) return 'Serie A';
    if (bundesligaTeams.some(t => teamLower.includes(t))) return 'Bundesliga';
    if (ligue1Teams.some(t => teamLower.includes(t))) return 'Ligue 1';
    if (eredivisieTeams.some(t => teamLower.includes(t))) return 'Eredivisie';
    
    return 'Other';
}

// Color scale for leagues
const leagueColors = {
    'Premier League': '#38003c',      // Purple
    'La Liga': '#ff6900',             // Orange
    'Serie A': '#0068a8',             // Blue
    'Bundesliga': '#d20026',          // Red
    'Ligue 1': '#1d3557',             // Dark Blue
    'Eredivisie': '#ff6600',          // Orange-Red
    'Other': '#999999'                // Gray
};

function getLeagueColor(league) {
    return leagueColors[league] || leagueColors['Other'];
}

// Load and parse CSV data
d3.csv("players_data_light-2024_2025.csv").then(function(data) {
    // Parse numeric columns
    data.forEach(function(d) {
        d.Min = +d.Min || 0;
        d.Gls = +d.Gls || 0;
        d.xG = +d.xG || 0;
        d["90s"] = +d["90s"] || 0;
        d.Age = +d.Age || null;
        d.Squad = d.Squad || "Unknown";
        d.Pos = d.Pos || "Unknown";
        
        // Assign league and color
        d.League = getLeague(d.Squad);
        d.LeagueColor = getLeagueColor(d.League);
        
        // Calculate goals per minute
        d.goalsPerMin = d.Min > 0 ? d.Gls / d.Min : 0;
        
        // Estimate shots from xG (average xG per shot is typically ~0.12)
        // If xG is 0 but player has goals, estimate minimum shots = goals
        const avgXGPerShot = 0.12;
        if (d.xG > 0) {
            d.shots = d.xG / avgXGPerShot;
        } else if (d.Gls > 0) {
            // If no xG but has goals, estimate shots based on goals
            // Assuming a minimum conversion rate of 10%, shots = goals / 0.1
            d.shots = d.Gls / 0.1;
        } else {
            d.shots = 0;
        }
        
        // Calculate shots per 90 minutes
        d.shotsPer90 = d["90s"] > 0 ? (d.shots / d["90s"]) : 0;
        
        // Calculate shot conversion rate (goals/shots * 100)
        d.conversionRate = d.shots > 0 ? (d.Gls / d.shots) * 100 : 0;
    });
    
    // Filter out players with no minutes played
    allData = data.filter(d => d.Min > 0);
    
    // Initialize visualizations
    initBarChart();
    initScatterPlot();
    
    // Setup slider
    setupSlider();
});

// Setup slider for bar chart
function setupSlider() {
    const slider = d3.select("#goalsSlider");
    const valueDisplay = d3.select("#minGoalsValue");
    
    slider.on("input", function() {
        minGoalsFilter = +this.value;
        valueDisplay.text(minGoalsFilter);
        updateBarChart();
    });
}

// Initialize Bar Chart
function initBarChart() {
    const margin = {top: 40, right: 80, bottom: 60, left: 100};
    const width = 900 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;
    
    // Clear previous chart
    d3.select("#barChart").selectAll("*").remove();
    
    const svg = d3.select("#barChart")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom);
    
    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
    
    // Store SVG and g for updates
    window.barChartSVG = svg;
    window.barChartG = g;
    window.barChartMargin = margin;
    window.barChartWidth = width;
    window.barChartHeight = height;
    
    updateBarChart();
}

// Update Bar Chart based on filter
function updateBarChart() {
    const margin = window.barChartMargin;
    const width = window.barChartWidth;
    const height = window.barChartHeight;
    const g = window.barChartG;
    
    // Filter data based on minimum goals
    const filteredData = allData
        .filter(d => d.Gls >= minGoalsFilter)
        .sort((a, b) => b.goalsPerMin - a.goalsPerMin)
        .slice(0, 10);
    
    // Remove previous elements
    g.selectAll(".bar").remove();
    g.selectAll(".axis").remove();
    g.selectAll("text.bar-label").remove();
    g.selectAll(".legend").remove();
    
    if (filteredData.length === 0) {
        g.append("text")
            .attr("x", width / 2)
            .attr("y", height / 2)
            .attr("text-anchor", "middle")
            .attr("font-size", "18px")
            .attr("fill", "#999")
            .text("No players match the filter criteria");
        return;
    }
    
    // Scales
    const xScale = d3.scaleLinear()
        .domain([0, d3.max(filteredData, d => d.goalsPerMin)])
        .range([0, width])
        .nice();
    
    const yScale = d3.scaleBand()
        .domain(filteredData.map(d => d.Player))
        .range([0, height])
        .padding(0.2);
    
    // X-axis
    const xAxis = d3.axisBottom(xScale)
        .tickFormat(d3.format(".6f"));
    
    g.append("g")
        .attr("class", "axis")
        .attr("transform", `translate(0,${height})`)
        .call(xAxis)
        .append("text")
        .attr("class", "axis-label")
        .attr("x", width / 2)
        .attr("y", 45)
        .attr("text-anchor", "middle")
        .text("Goals per Minute");
    
    // Y-axis
    const yAxis = d3.axisLeft(yScale);
    
    g.append("g")
        .attr("class", "axis")
        .call(yAxis)
        .selectAll("text")
        .style("font-size", "11px");
    
    // Tooltip
    const tooltip = d3.select("#tooltip");
    
    // Bars
    const bars = g.selectAll(".bar")
        .data(filteredData)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", 0)
        .attr("y", d => yScale(d.Player))
        .attr("width", d => xScale(d.goalsPerMin))
        .attr("height", yScale.bandwidth())
        .attr("fill", d => d.LeagueColor)
        .on("mouseover", function(event, d) {
            d3.select(this)
                .attr("opacity", 0.8);
            tooltip
                .style("opacity", 1)
                .html(`
                    <strong>${d.Player}</strong><br/>
                    Team: ${d.Squad}<br/>
                    League: ${d.League}<br/>
                    Position: ${d.Pos}<br/>
                    Goals: ${d.Gls}<br/>
                    Minutes: ${d.Min}<br/>
                    Goals/Min: ${d.goalsPerMin.toFixed(6)}<br/>
                    Goals/90: ${(d.Gls / d["90s"]).toFixed(2)}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        })
        .on("mouseout", function() {
            d3.select(this)
                .attr("opacity", 1);
            tooltip.style("opacity", 0);
        });
    
    // Value labels on bars
    g.selectAll("text.bar-label")
        .data(filteredData)
        .enter()
        .append("text")
        .attr("class", "bar-label")
        .attr("x", d => xScale(d.goalsPerMin) + 5)
        .attr("y", d => yScale(d.Player) + yScale.bandwidth() / 2)
        .attr("dy", "0.35em")
        .attr("font-size", "10px")
        .attr("fill", "#333")
        .text(d => `${d.Gls} goals`);
    
    // Add legend for bar chart
    addBarChartLegend(g, width, height, margin);
}

// Add legend for bar chart
function addBarChartLegend(g, width, height, margin) {
    const legendX = width + 20;
    const legendY = 20;
    const legendItemHeight = 20;
    
    const uniqueLeagues = Array.from(new Set(allData.map(d => d.League))).sort();
    
    const legend = g.append("g")
        .attr("class", "legend")
        .attr("transform", `translate(${legendX},${legendY})`);
    
    legend.append("text")
        .attr("class", "legend-title")
        .attr("x", 0)
        .attr("y", 0)
        .attr("font-weight", "bold")
        .attr("font-size", "12px")
        .text("League:");
    
    const legendItems = legend.selectAll(".legend-item")
        .data(uniqueLeagues)
        .enter()
        .append("g")
        .attr("class", "legend-item")
        .attr("transform", (d, i) => `translate(0,${(i + 1) * legendItemHeight})`);
    
    legendItems.append("rect")
        .attr("width", 15)
        .attr("height", 15)
        .attr("fill", d => getLeagueColor(d));
    
    legendItems.append("text")
        .attr("x", 20)
        .attr("y", 12)
        .attr("font-size", "11px")
        .text(d => d);
}

// Initialize Scatter Plot
function initScatterPlot() {
    const margin = {top: 40, right: 80, bottom: 80, left: 100};
    const width = 900 - margin.left - margin.right;
    const height = 600 - margin.top - margin.bottom;
    
    const svg = d3.select("#scatterPlot")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom);
    
    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
    
    // Filter data: only players with shots and meaningful data
    const scatterData = allData.filter(d => 
        d.shots > 0 && 
        d["90s"] > 0 && 
        d.shotsPer90 > 0
    );
    
    // Scales
    const xScale = d3.scaleLinear()
        .domain(d3.extent(scatterData, d => d.shotsPer90))
        .range([0, width])
        .nice();
    
    const yScale = d3.scaleLinear()
        .domain([0, d3.max(scatterData, d => d.conversionRate)])
        .range([height, 0])
        .nice();
    
    // Grid lines
    const xGridLines = d3.axisBottom(xScale)
        .tickSize(-height)
        .tickFormat("")
        .ticks(10);
    
    const yGridLines = d3.axisLeft(yScale)
        .tickSize(-width)
        .tickFormat("")
        .ticks(10);
    
    g.append("g")
        .attr("class", "grid-line")
        .attr("transform", `translate(0,${height})`)
        .call(xGridLines);
    
    g.append("g")
        .attr("class", "grid-line")
        .call(yGridLines);
    
    // X-axis
    const xAxis = d3.axisBottom(xScale)
        .ticks(10);
    
    g.append("g")
        .attr("class", "axis")
        .attr("transform", `translate(0,${height})`)
        .call(xAxis)
        .append("text")
        .attr("class", "axis-label")
        .attr("x", width / 2)
        .attr("y", 50)
        .attr("text-anchor", "middle")
        .text("Shots per 90 Minutes");
    
    // Y-axis
    const yAxis = d3.axisLeft(yScale)
        .ticks(10)
        .tickFormat(d => d + "%");
    
    g.append("g")
        .attr("class", "axis")
        .call(yAxis)
        .append("text")
        .attr("class", "axis-label")
        .attr("transform", "rotate(-90)")
        .attr("y", -60)
        .attr("x", -height / 2)
        .attr("text-anchor", "middle")
        .text("Shot Conversion Rate (%)");
    
    // Tooltip
    const tooltip = d3.select("#tooltip");
    
    // Points
    g.selectAll(".point")
        .data(scatterData)
        .enter()
        .append("circle")
        .attr("class", "point")
        .attr("cx", d => xScale(d.shotsPer90))
        .attr("cy", d => yScale(d.conversionRate))
        .attr("r", 4)
        .attr("fill", d => d.LeagueColor)
        .attr("stroke", "#fff")
        .attr("stroke-width", 0.5)
        .attr("opacity", 0.7)
        .on("mouseover", function(event, d) {
            d3.select(this)
                .attr("r", 6)
                .attr("opacity", 1)
                .attr("stroke-width", 1.5);
            
            tooltip
                .style("opacity", 1)
                .html(`
                    <strong>${d.Player}</strong><br/>
                    Team: ${d.Squad}<br/>
                    League: ${d.League}<br/>
                    Position: ${d.Pos}<br/>
                    Goals: ${d.Gls}<br/>
                    Estimated Shots: ${d.shots.toFixed(1)}<br/>
                    Shots/90: ${d.shotsPer90.toFixed(2)}<br/>
                    Conversion Rate: ${d.conversionRate.toFixed(1)}%
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        })
        .on("mouseout", function() {
            d3.select(this)
                .attr("r", 4)
                .attr("opacity", 0.7)
                .attr("stroke-width", 0.5);
            tooltip.style("opacity", 0);
        });
    
    // Add legend for scatter plot
    addScatterLegend(g, width, height, margin);
    
    // Add title
    svg.append("text")
        .attr("x", (width + margin.left + margin.right) / 2)
        .attr("y", 20)
        .attr("text-anchor", "middle")
        .attr("font-size", "14px")
        .attr("fill", "#666")
        .text("Note: Shots are estimated from Expected Goals (xG) data");
}

// Add legend for scatter plot
function addScatterLegend(g, width, height, margin) {
    const legendX = width + 20;
    const legendY = 20;
    const legendItemHeight = 20;
    
    const uniqueLeagues = Array.from(new Set(allData.map(d => d.League))).sort();
    
    const legend = g.append("g")
        .attr("class", "legend")
        .attr("transform", `translate(${legendX},${legendY})`);
    
    legend.append("text")
        .attr("class", "legend-title")
        .attr("x", 0)
        .attr("y", 0)
        .attr("font-weight", "bold")
        .attr("font-size", "12px")
        .text("League:");
    
    const legendItems = legend.selectAll(".legend-item")
        .data(uniqueLeagues)
        .enter()
        .append("g")
        .attr("class", "legend-item")
        .attr("transform", (d, i) => `translate(0,${(i + 1) * legendItemHeight})`);
    
    legendItems.append("circle")
        .attr("r", 6)
        .attr("cx", 7)
        .attr("cy", 7)
        .attr("fill", d => getLeagueColor(d))
        .attr("stroke", "#fff")
        .attr("stroke-width", 0.5);
    
    legendItems.append("text")
        .attr("x", 18)
        .attr("y", 11)
        .attr("font-size", "11px")
        .text(d => d);
}

