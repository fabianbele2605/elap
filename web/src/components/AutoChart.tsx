import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface AutoChartProps {
  title: string;
  tableMarkdown: string;
}

export const AutoChart: React.FC<AutoChartProps> = ({ title, tableMarkdown }) => {
  // Parsear tabla markdown
  const parseTableData = (markdown: string) => {
    const rows = markdown.trim().split('\n');
    const headers: string[] = [];
    const data: any[] = [];

    rows.forEach((row, idx) => {
      if (row.startsWith('|') && !row.includes('---')) {
        const cells = row
          .split('|')
          .filter(c => c.trim().length > 0 || c === '')
          .map(c => c.trim());

        if (idx === 0) {
          headers.push(...cells);
        } else {
          const obj: any = {};
          headers.forEach((header, hIdx) => {
            const value = cells[hIdx];
            const numValue = parseFloat(value?.replace(/[^0-9.-]/g, '') || '0');
            obj[header] = isNaN(numValue) ? value : numValue;
          });
          if (Object.keys(obj).length > 0) {
            data.push(obj);
          }
        }
      }
    });

    return { headers, data };
  };

  const { headers, data } = parseTableData(tableMarkdown);

  if (data.length === 0) {
    return (
      <div className="p-4 bg-amber-50 border border-amber-300 rounded-lg text-amber-700">
        No se pudo extraer datos para el gráfico
      </div>
    );
  }

  // Detectar tipo de gráfico según el título
  const chartType = title.toLowerCase().includes('proyectado')
    ? 'line'
    : title.toLowerCase().includes('comparación')
    ? 'bar'
    : 'area';

  const numericColumns = headers.filter(h => {
    const sample = data[0]?.[h];
    return typeof sample === 'number' || !isNaN(Number(sample));
  });

  const colors = ['#2563eb', '#dc2626', '#16a34a', '#ea580c', '#7c3aed'];

  return (
    <div className="w-full my-4 p-4 bg-slate-50 border border-slate-300 rounded-lg">
      <h3 className="text-sm font-bold text-slate-700 mb-4">{title}</h3>

      <ResponsiveContainer width="100%" height={300}>
        {chartType === 'line' && (
          <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={headers[0]} />
            <YAxis />
            <Tooltip
              formatter={(value) => typeof value === 'number' ? `$${(value / 1000).toFixed(1)}B` : value}
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
            />
            <Legend />
            {numericColumns.slice(1).map((col, idx) => (
              <Line
                key={col}
                type="monotone"
                dataKey={col}
                stroke={colors[idx % colors.length]}
                strokeWidth={2}
                dot={{ fill: colors[idx % colors.length], r: 4 }}
                activeDot={{ r: 6 }}
              />
            ))}
          </LineChart>
        )}

        {chartType === 'bar' && (
          <BarChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={headers[0]} />
            <YAxis />
            <Tooltip
              formatter={(value) => typeof value === 'number' ? `$${(value / 1000).toFixed(1)}B` : value}
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
            />
            <Legend />
            {numericColumns.slice(1).map((col, idx) => (
              <Bar
                key={col}
                dataKey={col}
                fill={colors[idx % colors.length]}
              />
            ))}
          </BarChart>
        )}

        {chartType === 'area' && (
          <AreaChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={headers[0]} />
            <YAxis />
            <Tooltip
              formatter={(value) => typeof value === 'number' ? `$${(value / 1000).toFixed(1)}B` : value}
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
            />
            <Legend />
            {numericColumns.slice(1).map((col, idx) => (
              <Area
                key={col}
                type="monotone"
                dataKey={col}
                fill={colors[idx % colors.length]}
                stroke={colors[idx % colors.length]}
                fillOpacity={0.6}
              />
            ))}
          </AreaChart>
        )}
      </ResponsiveContainer>
    </div>
  );
};
