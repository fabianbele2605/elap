"""
Generador de reportes QA para documentos
Implementa CAPA 5: ENTREGA del Document Quality Standard
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DocumentQAReporter:
    """Genera reportes de calidad para documentos generados"""

    def __init__(self, validation_report: Dict[str, Any]):
        self.report = validation_report

    def get_summary(self) -> str:
        """Resumen ejecutivo del QA"""
        status = self.report.get('status', 'UNKNOWN')
        score = self.report.get('overall_score', 0)
        ready = "✅ LISTO PARA ENTREGAR" if self.report.get('ready_for_delivery') else "❌ REVISAR ANTES DE ENTREGAR"

        return f"""
╔════════════════════════════════════════╗
║  📊 REPORTE DE CALIDAD DOCUMENTOS      ║
╚════════════════════════════════════════╝

📄 Documento: {self.report.get('document')}
🤖 Agente: {self.report.get('agent')}
📋 Tipo: {self.report.get('document_type')}
⏰ Timestamp: {self.report.get('timestamp')}

📈 SCORE GENERAL: {score}%
🎯 STATUS: {status}
✨ ENTREGA: {ready}

────────────────────────────────────────
        """

    def get_detailed_report(self) -> str:
        """Reporte detallado con todos los checks"""
        lines = [self.get_summary()]

        # Checks de contenido
        content_check = self.report.get('checks', {}).get('content', {})
        lines.append("📋 VALIDACIÓN DE CONTENIDO")
        lines.append(f"  Status: {content_check.get('status', 'N/A')}")
        lines.append(f"  Score: {content_check.get('score', 0)}%")
        if content_check.get('issues'):
            lines.append("  ⚠️ Issues:")
            for issue in content_check.get('issues', [])[:5]:
                lines.append(f"    - {issue}")
        lines.append("")

        # Checks de formato
        format_check = self.report.get('checks', {}).get('format', {})
        lines.append("🔍 VALIDACIÓN DE FORMATO")
        lines.append(f"  Status: {format_check.get('status', 'N/A')}")
        lines.append(f"  Score: {format_check.get('score', 0)}%")
        if format_check.get('issues'):
            lines.append("  ⚠️ Issues:")
            for issue in format_check.get('issues', [])[:5]:
                lines.append(f"    - {issue}")
        if format_check.get('warnings'):
            lines.append("  💡 Warnings:")
            for warning in format_check.get('warnings', [])[:3]:
                lines.append(f"    - {warning}")
        lines.append("")

        # Issues y warnings globales
        all_issues = self.report.get('all_issues', [])
        all_warnings = self.report.get('all_warnings', [])

        if all_issues:
            lines.append(f"🔴 PROBLEMAS CRÍTICOS ({len(all_issues)})")
            for issue in all_issues[:10]:
                lines.append(f"  ❌ {issue}")
            lines.append("")

        if all_warnings:
            lines.append(f"🟡 ADVERTENCIAS ({len(all_warnings)})")
            for warning in all_warnings[:10]:
                lines.append(f"  ⚠️ {warning}")
            lines.append("")

        # Recomendaciones
        lines.append("💡 RECOMENDACIONES")
        if all_issues:
            lines.append("  1. RESOLVER problemas críticos antes de entregar")
        if all_warnings:
            lines.append("  2. REVISAR advertencias para mejorar calidad")
        if self.report.get('overall_score', 0) < 80:
            lines.append("  3. MEJORAR score general (objetivo: ≥90%)")
        if not all_issues and not all_warnings:
            lines.append("  ✅ Documento listo para producción")

        lines.append("\n" + "="*40 + "\n")

        return "\n".join(lines)

    def get_json_report(self) -> str:
        """Reporte en formato JSON"""
        return json.dumps(self.report, indent=2, ensure_ascii=False)

    def save_report(self, output_path: str) -> str:
        """Guarda reporte en archivo"""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Guardar JSON
        json_path = str(path.with_suffix('.json'))
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(self.get_json_report())

        # Guardar TXT
        txt_path = str(path.with_suffix('.txt'))
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(self.get_detailed_report())

        logger.info(f"✅ Reporte QA guardado: {json_path}")
        logger.info(f"✅ Reporte legible guardado: {txt_path}")

        return json_path

    @staticmethod
    def create_badge(score: int, status: str) -> str:
        """Crea un badge de calidad para usar en documentos"""
        emoji_map = {
            "🟢 PASS": "✅",
            "🟡 WARN": "⚠️",
            "🔴 FAIL": "❌",
        }
        emoji = emoji_map.get(status, "❓")
        return f"{emoji} {score}%"

    @staticmethod
    def should_block_delivery(report: Dict[str, Any]) -> bool:
        """Determina si el documento debería ser bloqueado de entrega"""
        issues = report.get('all_issues', [])
        score = report.get('overall_score', 0)

        # Bloquear si hay problemas críticos O si score < 60
        return len(issues) > 0 or score < 60

    @staticmethod
    def get_delivery_status(report: Dict[str, Any]) -> str:
        """Status amigable para el usuario"""
        if DocumentQAReporter.should_block_delivery(report):
            return "🔴 BLOQUEADO - Revisar antes de entregar"
        elif report.get('all_warnings'):
            return "🟡 ADVERTENCIAS - Revisar antes de entregar"
        else:
            return "🟢 LISTO PARA ENTREGAR"
