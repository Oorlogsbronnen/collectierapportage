// Assuming your JSON file is named all_reports.json in the root of your repository
const jsonFilePath = 'all_reports.json';

// Fetch the JSON file
fetch(jsonFilePath)
  .then(response => response.text()) // Read the file as text
  .then(jsonText => {
    // Split the text into lines
    const lines = jsonText.split(/\n/);

    // Data processing logic
    const data = lines.map(line => {
      try {
        const entry = JSON.parse(line.trim());
        return entry.flatMap(entryItem => entryItem.content.map(contentItem => ({
          collection: entryItem.collection,
          contentCount: Object.keys(contentItem).length,
          lastUpdate: new Date(entryItem.lastUpdate),
        })));
      } catch (error) {
        console.error('Error parsing JSON line:', error);
        return []; // Return an empty array for lines with parsing errors
      }
    }).flat();

    // Set up D3.js
    const svg = d3.select("#visualization")
      .append("svg")
      .attr("width", 800)
      .attr("height", 400);

    // Define scales and axes
    const xScale = d3.scaleTime()
      .domain(d3.extent(data, d => d.lastUpdate))
      .range([0, 800]);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.contentCount)])
      .range([400, 0]);

    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale);

    // Draw axes
    svg.append("g")
      .attr("transform", "translate(0, 400)")
      .call(xAxis);

    svg.append("g")
      .call(yAxis);

    // Draw line
    const line = d3.line()
      .x(d => xScale(d.lastUpdate))
      .y(d => yScale(d.contentCount));

    svg.append("path")
      .data([data])
      .attr("class", "line")
      .attr("d", line);
  })
  .catch(error => console.error('Error fetching JSON:', error));
