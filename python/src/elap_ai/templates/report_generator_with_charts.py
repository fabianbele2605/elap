"""Generador de reportes con gráficos Chart.js interactivos

Extiende report_generator.py agregando:
- Gráficos de línea (tendencias)
- Gráficos de pastel (distribución)
- Gráficos de barras (comparativas)
"""

from typing import List, Dict, Any, Optional


class ChartData:
    """Datos para un gráfico Chart.js"""

    def __init__(
        self,
        type: str,  # 'line', 'pie', 'bar', 'doughnut'
        title: str,
        labels: List[str],
        datasets: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None
    ):
        self.type = type
        self.title = title
        self.labels = labels
        self.datasets = datasets
        self.options = options or {}

    def to_json_config(self) -> str:
        """Convierte a configuración de Chart.js como string JavaScript"""
        import json

        config = {
            'type': self.type,
            'data': {
                'labels': self.labels,
                'datasets': self.datasets
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': self.title,
                        'font': {'size': 14, 'weight': 'bold'}
                    },
                    'legend': {
                        'display': True,
                        'position': 'bottom'
                    }
                }
            }
        }

        # Merge options personalizadas sin callbacks
        if self.options:
            safe_options = {k: v for k, v in self.options.items() if not callable(v)}
            config['options'].update(safe_options)

        return json.dumps(config)


def create_trend_chart(
    title: str,
    months: List[str],
    data: List[float],
    label: str = "Valor",
    color: str = "#2a5298"
) -> ChartData:
    """Crea gráfico de línea para tendencias"""
    return ChartData(
        type='line',
        title=title,
        labels=months,
        datasets=[
            {
                'label': label,
                'data': data,
                'borderColor': color,
                'backgroundColor': f"rgba({hex_to_rgb(color)}, 0.1)",
                'tension': 0.4,
                'fill': True,
                'pointRadius': 5,
                'pointBackgroundColor': color,
                'pointHoverRadius': 7
            }
        ],
        options={
            'scales': {
                'y': {
                    'beginAtZero': True
                }
            }
        }
    )


def create_distribution_chart(
    title: str,
    labels: List[str],
    data: List[float],
    colors: Optional[List[str]] = None
) -> ChartData:
    """Crea gráfico de pastel para distribución"""
    if colors is None:
        colors = [
            '#2a5298', '#27ae60', '#f39c12', '#e74c3c',
            '#9b59b6', '#1abc9c', '#34495e', '#e67e22'
        ][:len(labels)]

    return ChartData(
        type='doughnut',
        title=title,
        labels=labels,
        datasets=[
            {
                'data': data,
                'backgroundColor': colors,
                'borderColor': '#fff',
                'borderWidth': 2
            }
        ]
    )


def create_comparison_chart(
    title: str,
    categories: List[str],
    series: List[Dict[str, Any]],  # [{"label": "2025", "data": [...]}, ...]
    colors: Optional[List[str]] = None
) -> ChartData:
    """Crea gráfico de barras para comparativas"""
    if colors is None:
        colors = ['#2a5298', '#27ae60', '#f39c12']

    datasets = []
    for idx, s in enumerate(series):
        datasets.append({
            'label': s.get('label', f'Serie {idx+1}'),
            'data': s.get('data', []),
            'backgroundColor': colors[idx % len(colors)],
            'borderColor': colors[idx % len(colors)],
            'borderWidth': 1
        })

    return ChartData(
        type='bar',
        title=title,
        labels=categories,
        datasets=datasets,
        options={
            'scales': {
                'y': {
                    'beginAtZero': True
                }
            }
        }
    )


def hex_to_rgb(hex_color: str) -> str:
    """Convierte hex color a RGB"""
    hex_color = hex_color.lstrip('#')
    return ', '.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))


# Factory functions para gráficos especializados

def create_financial_charts() -> List[ChartData]:
    """Crea set de gráficos para reportes financieros"""
    return [
        create_trend_chart(
            "Evolución de Ingresos (Q1-Q3 2026)",
            ['Q1', 'Q2', 'Q3'],
            [18900, 20500, 21200],
            "Ingresos MM",
            "#2a5298"
        ),
        create_comparison_chart(
            "Comparativa Márgenes vs Sector",
            ['Andina Foods', 'Competidor A', 'Competidor B', 'Promedio Sector'],
            [
                {'label': 'Margen Neto %', 'data': [5.9, 4.8, 5.1, 5.2]}
            ],
            ['#27ae60', '#f39c12', '#e74c3c', '#95a5a6']
        ),
        create_distribution_chart(
            "Distribución de Ingresos por Línea",
            ['Bebidas Alcohólicas', 'Snacks', 'Bebidas No Alcohólicas', 'Otros'],
            [43.4, 27.4, 20.3, 8.9],
            ['#2a5298', '#27ae60', '#f39c12', '#e74c3c']
        )
    ]


def create_hr_charts() -> List[ChartData]:
    """Crea set de gráficos para reportes HR"""
    return [
        create_trend_chart(
            "Evolución de Empleados Activos",
            ['Q1', 'Q2', 'Q3'],
            [178, 182, 187],
            "Empleados",
            "#27ae60"
        ),
        create_distribution_chart(
            "Distribución por Área",
            ['Administrativo', 'Dirección', 'Comercial', 'Documentación'],
            [115, 28, 31, 13],
            ['#2a5298', '#27ae60', '#f39c12', '#e74c3c']
        ),
        create_comparison_chart(
            "Rotación Anual vs Sector",
            ['Andina Foods', 'Promedio Sector', 'Mejor en clase'],
            [
                {'label': 'Rotación %', 'data': [2.5, 4.2, 1.8]}
            ],
            ['#27ae60', '#f39c12', '#2a5298']
        )
    ]


def create_sales_charts() -> List[ChartData]:
    """Crea set de gráficos para reportes de ventas"""
    return [
        create_trend_chart(
            "Pipeline de Ventas (Q1-Q3)",
            ['Q1', 'Q2', 'Q3'],
            [7200, 7850, 8500],
            "Pipeline MM",
            "#2a5298"
        ),
        create_distribution_chart(
            "Distribución por Canal",
            ['Canal Directo', 'Distribuidores', 'E-commerce'],
            [52, 35, 13],
            ['#2a5298', '#27ae60', '#f39c12']
        ),
        create_comparison_chart(
            "Performance por Línea de Negocio",
            ['Línea A', 'Línea B', 'Línea C'],
            [
                {'label': 'Ingresos 2025', 'data': [8200, 6500, 3800]},
                {'label': 'Ingresos 2026', 'data': [9200, 7420, 4580]}
            ],
            ['#95a5a6', '#2a5298']
        )
    ]


def generate_html_with_charts(
    base_html: str,
    charts: List[ChartData]
) -> str:
    """Inyecta gráficos en el HTML base de reportes"""

    import json

    # Generar divs para los gráficos
    charts_html = ""
    charts_script = ""

    for idx, chart in enumerate(charts):
        chart_id = f"chart_{idx}"
        charts_html += f"""
        <div class="chart-container">
            <canvas id="{chart_id}"></canvas>
        </div>
        """

        config = chart.to_json_config()
        charts_script += f"""
        const ctx{idx} = document.getElementById('{chart_id}').getContext('2d');
        new Chart(ctx{idx}, {json.dumps(config)});
        """

    # Inyectar en HTML
    # Buscar "</head>" y agregar Chart.js CDN
    head_injection = """
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    """

    html = base_html.replace("</head>", f"{head_injection}</head>")

    # Buscar la sección de gráficos placeholder y reemplazar
    charts_section = f"""
    <!-- Sección de Gráficos -->
    <div class="section">
        <h2>📈 Visualización de Datos</h2>
        {charts_html}
    </div>
    """

    # Buscar dónde insertar (antes del footer)
    if "<div class=\"footer\">" in html:
        html = html.replace(
            "<div class=\"footer\">",
            f"{charts_section}\n\n<div class=\"footer\">"
        )

    # Agregar script al final del body
    script_injection = f"""
    <script>
        // Gráficos Chart.js
        {charts_script}
    </script>
    """

    html = html.replace("</body>", f"{script_injection}</body>")

    return html


# CSS para los contenedores de gráficos
CHART_STYLES = """
<style>
    .chart-container {
        background: white;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        max-width: 100%;
        overflow-x: auto;
    }

    .chart-container canvas {
        max-height: 400px;
    }

    @media (max-width: 768px) {
        .chart-container {
            padding: 15px;
        }

        .chart-container canvas {
            max-height: 300px;
        }
    }
</style>
"""
