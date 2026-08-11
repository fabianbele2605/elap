"""Generador de gráficos Chart.js para respuestas de agentes"""

import json
import base64
from typing import List, Dict, Any


class ChartGenerator:
    """Genera gráficos HTML con Chart.js a partir de datos"""

    @staticmethod
    def generate_bar_chart(title: str, labels: List[str], data: List[float], colors: str = "rgb(75, 192, 192)") -> str:
        """Genera un gráfico de barras"""
        chart_id = f"chart_{id(labels)}"

        html = f"""
<div style="margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 8px;">
<h3 style="margin-top: 0; color: #333;">{title}</h3>
<canvas id="{chart_id}" style="max-width: 100%; height: 300px;"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx{chart_id} = document.getElementById('{chart_id}').getContext('2d');
new Chart(ctx{chart_id}, {{
    type: 'bar',
    data: {{
        labels: {json.dumps(labels)},
        datasets: [{{
            label: '{title}',
            data: {json.dumps(data)},
            backgroundColor: '{colors}',
            borderColor: 'rgb(200, 200, 200)',
            borderWidth: 1
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{ y: {{ beginAtZero: true }} }}
    }}
}});
</script>
</div>
"""
        return html

    @staticmethod
    def generate_pie_chart(title: str, labels: List[str], data: List[float]) -> str:
        """Genera un gráfico tipo pastel"""
        chart_id = f"chart_{id(labels)}"
        colors = [
            "rgb(255, 99, 132)",
            "rgb(54, 162, 235)",
            "rgb(255, 206, 86)",
            "rgb(75, 192, 192)",
            "rgb(153, 102, 255)",
            "rgb(255, 159, 64)"
        ]

        html = f"""
<div style="margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 8px;">
<h3 style="margin-top: 0; color: #333;">{title}</h3>
<canvas id="{chart_id}" style="max-width: 100%; height: 300px;"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx{chart_id} = document.getElementById('{chart_id}').getContext('2d');
new Chart(ctx{chart_id}, {{
    type: 'pie',
    data: {{
        labels: {json.dumps(labels)},
        datasets: [{{
            data: {json.dumps(data)},
            backgroundColor: {json.dumps(colors[:len(labels)])},
            borderColor: 'rgb(200, 200, 200)',
            borderWidth: 1
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ position: 'right' }} }}
    }}
}});
</script>
</div>
"""
        return html

    @staticmethod
    def generate_line_chart(title: str, labels: List[str], datasets: Dict[str, List[float]]) -> str:
        """Genera un gráfico de líneas"""
        chart_id = f"chart_{id(title)}"
        colors = ["rgb(75, 192, 192)", "rgb(255, 99, 132)", "rgb(54, 162, 235)"]

        chart_datasets = []
        for idx, (label, data) in enumerate(datasets.items()):
            color = colors[idx % len(colors)]
            chart_datasets.append({
                "label": label,
                "data": data,
                "borderColor": color,
                "backgroundColor": color.replace("rgb", "rgba").replace(")", ", 0.1)"),
                "borderWidth": 2,
                "fill": True,
                "tension": 0.4
            })

        html = f"""
<div style="margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 8px;">
<h3 style="margin-top: 0; color: #333;">{title}</h3>
<canvas id="{chart_id}" style="max-width: 100%; height: 300px;"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx{chart_id} = document.getElementById('{chart_id}').getContext('2d');
new Chart(ctx{chart_id}, {{
    type: 'line',
    data: {{
        labels: {json.dumps(labels)},
        datasets: {json.dumps(chart_datasets)}
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: true }} }},
        scales: {{ y: {{ beginAtZero: true }} }}
    }}
}});
</script>
</div>
"""
        return html
