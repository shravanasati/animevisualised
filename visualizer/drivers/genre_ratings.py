from io import BytesIO

from matplotlib import pyplot as plt

from .base import IVisualizationDriver, VisualizationResult


class GenreRatingsDriver(IVisualizationDriver):
    def visualize(self) -> VisualizationResult:
        df = self.df[self.df["my_status"] != "Plan to Watch"]
        items = zip(df["series_genres"], df["my_score"])

        genres_data: dict[str, list[int]] = {}

        for genres_score_pair in items:
            genres = genres_score_pair[0]
            rating = genres_score_pair[1]
            for g in genres:
                if g in genres_data:
                    genres_data[g].append(rating)
                else:
                    genres_data[g] = [rating]

        if self.opts.disable_nsfw:
            for g in self.NSFW_GENRES:
                if g in genres_data:
                    genres_data.pop(g)

        average_data = {
            k: round(sum(v) / len(v), 2) for k, v in genres_data.items() if len(v) != 0
        }
        plottable_data = dict(sorted(average_data.items(), key=lambda x: x[1]))

        fig, ax = plt.subplots()
        ax.set_title("Average rating of anime per genre")
        ax.set_xlabel("Genres")
        ax.set_ylabel("Average rating (out of 10)")

        bar = ax.bar(plottable_data.keys(), plottable_data.values())
        ax.bar_label(bar)
        fig.autofmt_xdate()

        buf = BytesIO()
        fig.savefig(buf)
        buf.seek(0)

        return VisualizationResult("Genre Ratings", self.to_base64(buf).decode("utf-8"))
