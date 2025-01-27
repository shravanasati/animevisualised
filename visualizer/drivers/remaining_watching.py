import numpy as np
import pandas as pd
import plotly.express as px
from matplotlib import pyplot as plt

from .base import (
    IVisualizationDriver,
    MatplotlibVisualizationResult,
    PlotlyVisualizationResult,
)


def trim_anime_title(name: str, max_name_length: int = 10):
    return name[: max_name_length + 1] + "..."


class RemainingCountDriver(IVisualizationDriver):
    def visualize(self):
        df = self.df[self.df["my_status"] == "Watching"]
        anime_names = df["series_title"].apply(trim_anime_title)
        if len(anime_names) == 0:
            return MatplotlibVisualizationResult(
                "Remaining Watching Content", self.get_not_enough_data_image()
            )
        watched = df["my_watched_episodes"]
        total_episodes = df["series_episodes"]
        max_total = total_episodes.max()
        total_episodes_fixed = total_episodes.apply(lambda x: x if x > 0 else max_total)
        remaining = total_episodes_fixed - watched

        watched_scaled = watched / total_episodes_fixed * max_total
        remaining_scaled = remaining / total_episodes_fixed * max_total

        zero_entries = total_episodes[total_episodes == 0].index
        remaining[zero_entries] = 0
        remaining_scaled[zero_entries] = 0

        results = {
            anime_names.iloc[i]: [
                watched.iloc[i],
                watched_scaled.iloc[i],
                remaining.iloc[i],
                remaining_scaled.iloc[i],
            ]
            for i in range(len(anime_names))
        }

        category_names = ("watched", "remaining")

        if self.opts.interactive_charts:
            # plotly code
            data = pd.DataFrame.from_dict(
                results,
                orient="index",
                columns=["watched", "watched_scaled", "remaining", "remaining_scaled"],
            )
            data.reset_index(inplace=True)
            data.rename(columns={"index": "names"}, inplace=True)

            fig = px.bar(
                data,
                x=["watched_scaled", "remaining_scaled"],
                y="names",
                orientation="h",
                title="Watched vs Remaining Episodes",
                color_discrete_sequence=px.colors.qualitative.Set3,
                # hover_data={
                #     "watched_scaled": False,
                #     "remaining_scaled": False,
                #     "remaining": True,
                #     "watched": True,
                # },
                # labels={"value": "Episode Count", "y": "Anime Names"},
            )

            return PlotlyVisualizationResult("Remaining Watching Content", fig)

        # matplotlib code
        data = np.array(list(results.values()))
        data_cum = data.cumsum(axis=1)
        category_colors = plt.colormaps["summer"](
            np.linspace(0.15, 0.85, data.shape[1])
        )

        fig, ax = plt.subplots(figsize=(9.2, 5))
        ax.invert_yaxis()
        ax.set_xlim(0, np.sum(data, axis=1).max())

        for i, (colname, color) in enumerate(zip(category_names, category_colors)):
            widths = data[:, i]
            starts = data_cum[:, i] - widths
            rects = ax.barh(
                anime_names, widths, left=starts, height=0.5, label=colname, color=color
            )

            r, g, b, _ = color
            ax.bar_label(rects, label_type="center", color="black")

        ax.set_yticks(labels=anime_names, rotation=52, ticks=anime_names)
        ax.set_title("Remaining Watching Content")
        ax.set_ylabel("Anime Names")
        ax.set_xlabel("Episode Count")
        ax.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )

        ax.legend(
            ncols=len(category_names),
            bbox_to_anchor=(0, 1),
            loc="lower left",
            fontsize="small",
        )
        return MatplotlibVisualizationResult(
            "Remaining Watching Content", self.b64_image_from_plt_fig(fig)
        )
