"""Chart and visualization generation."""

import uuid
from typing import Optional, Any
import pandas as pd


class ChartGenerator:
    """Generates professional charts and visualizations."""

    @staticmethod
    def bar_chart(
        data: dict[str, float],
        title: str,
        xlabel: str = "Categorías",
        ylabel: str = "Valores",
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate bar chart.

        Args:
            data: Dictionary mapping labels to values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            output_path: Where to save (defaults to /tmp)

        Returns:
            Path to saved chart PNG
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("matplotlib required: pip install matplotlib")

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(data.keys(), data.values(), color="#4472C4")
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        if output_path is None:
            output_path = f"/tmp/chart_bar_{uuid.uuid4()}.png"

        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        return output_path

    @staticmethod
    def line_chart(
        data: dict[str, list[float]],
        x_labels: list[str],
        title: str,
        xlabel: str = "Período",
        ylabel: str = "Valores",
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate line chart.

        Args:
            data: Dictionary mapping series names to value lists
            x_labels: X-axis labels
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            output_path: Where to save

        Returns:
            Path to saved chart PNG
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("matplotlib required: pip install matplotlib")

        fig, ax = plt.subplots(figsize=(10, 6))

        for series_name, values in data.items():
            ax.plot(x_labels, values, marker="o", label=series_name, linewidth=2)

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()

        if output_path is None:
            output_path = f"/tmp/chart_line_{uuid.uuid4()}.png"

        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        return output_path

    @staticmethod
    def pie_chart(
        data: dict[str, float],
        title: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate pie chart.

        Args:
            data: Dictionary mapping labels to values
            title: Chart title
            output_path: Where to save

        Returns:
            Path to saved chart PNG
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("matplotlib required: pip install matplotlib")

        fig, ax = plt.subplots(figsize=(8, 8))
        colors = ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#70AD47"]

        ax.pie(
            data.values(),
            labels=data.keys(),
            autopct="%1.1f%%",
            colors=colors[:len(data)],
            startangle=90,
        )
        ax.set_title(title, fontsize=14, fontweight="bold")

        plt.tight_layout()

        if output_path is None:
            output_path = f"/tmp/chart_pie_{uuid.uuid4()}.png"

        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        return output_path

    @staticmethod
    def histogram(
        data: list[float],
        title: str,
        xlabel: str = "Valores",
        ylabel: str = "Frecuencia",
        bins: int = 20,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate histogram.

        Args:
            data: List of values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            bins: Number of bins
            output_path: Where to save

        Returns:
            Path to saved chart PNG
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("matplotlib required: pip install matplotlib")

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(data, bins=bins, color="#4472C4", edgecolor="black")
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        if output_path is None:
            output_path = f"/tmp/chart_hist_{uuid.uuid4()}.png"

        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        return output_path

    @staticmethod
    def scatter_plot(
        x_data: list[float],
        y_data: list[float],
        title: str,
        xlabel: str = "X",
        ylabel: str = "Y",
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate scatter plot.

        Args:
            x_data: X-axis values
            y_data: Y-axis values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            output_path: Where to save

        Returns:
            Path to saved chart PNG
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("matplotlib required: pip install matplotlib")

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(x_data, y_data, color="#4472C4", s=100, alpha=0.6)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.3)

        plt.tight_layout()

        if output_path is None:
            output_path = f"/tmp/chart_scatter_{uuid.uuid4()}.png"

        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        return output_path
