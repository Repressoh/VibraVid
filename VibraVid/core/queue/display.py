import threading

from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich import box

from .queue import download_manager
from VibraVid.source.utils.tracker import download_tracker


class DownloadDisplay:
    MAX_QUEUED_ROWS = 3
    MAX_COMPLETED_ROWS = 5

    def __init__(self):
        self._live: Live | None = None
        self._update_event = threading.Event()
        self._console = Console()

    def _build_renderable(self) -> Table:
        """Build the full display from current queue/tracker state."""

        queued = download_manager.get_queue()
        active = download_manager.get_active()
        completed = download_manager.get_completed()
        tracker_data = {d["id"]: d for d in download_tracker.get_active_downloads()}
        # Also include history so completed jobs can show quality/language
        for h in download_tracker.get_history():
            if h["id"] not in tracker_data:
                tracker_data[h["id"]] = h

        table = Table(
            title="Download Monitor",
            box=box.ROUNDED,
            expand=True,
            title_style="bold #22c55e",
            border_style="#a855f7",
            header_style="bold #a855f7",
        )
        table.add_column("#", style="dim", width=6)
        table.add_column("Title", style="bold white", ratio=3)
        table.add_column("Quality", style="#c084fc", ratio=1)
        table.add_column("Language", style="#c084fc", ratio=1)
        table.add_column("Status", ratio=1)
        table.add_column("Progress", style="#22c55e", ratio=1)
        table.add_column("Speed", style="dim", ratio=1)
        table.add_column("Segments", style="dim", ratio=1)

        # --- Active jobs (with live progress from tracker) ---
        for job in active:
            dl = tracker_data.get(job.id)
            if dl:
                status_raw = dl.get("status", "running")
                if status_raw == "joining":
                    status_str = "[#a855f7]⚙ Joining[/]"
                else:
                    status_str = "[#22c55e]↓ Running[/]"
                progress = f"{dl['progress']:.1f}%"
                speed = dl.get("speed", "...")
                segments = dl.get("segments", "...")
                quality = dl.get("quality", "")
                language = dl.get("language", "")
            else:
                status_str = "[#22c55e]↓ Running[/]"
                progress = "..."
                speed = "..."
                segments = "..."
                quality = ""
                language = ""

            table.add_row(
                job.id[:6], job.title, quality, language,
                status_str,
                progress, speed, segments,
            )

        # --- Queued jobs (show first N, summarize rest) ---
        queued_shown = queued[:self.MAX_QUEUED_ROWS]
        queued_remaining = len(queued) - len(queued_shown)
        for job in queued_shown:
            table.add_row(
                job.id[:6], job.title, "", "",
                "[dim]\u23f3 Queued[/]",
                "-", "-", "-",
            )
        if queued_remaining > 0:
            table.add_row(
                "", f"[dim]... +{queued_remaining} more in queue[/]", "", "",
                "", "", "", "",
            )

        # --- Completed / Failed (show last N, summarize rest) ---
        completed_shown = completed[-self.MAX_COMPLETED_ROWS:] if len(completed) > self.MAX_COMPLETED_ROWS else completed
        completed_hidden = len(completed) - len(completed_shown)
        if completed_hidden > 0:
            table.add_row(
                "", f"[dim]... {completed_hidden} earlier completed[/]", "", "",
                "", "", "", "",
            )
        for job in completed_shown:
            dl = tracker_data.get(job.id)
            quality = dl.get("quality", "") if dl else ""
            language = dl.get("language", "") if dl else ""

            if job.status == "completed":
                status_str = "[#22c55e]✓ Done[/]"
                pct = "100%"
            elif job.status == "failed":
                status_str = "[#ef4444]✗ Failed[/]"
                pct = "-"
            elif job.status == "cancelled":
                status_str = "[#ef4444]⊘ Cancelled[/]"
                pct = "-"
            else:
                status_str = f"[dim]{job.status}[/]"
                pct = "-"

            table.add_row(
                job.id[:6], job.title, quality, language,
                status_str,
                pct, "-", "-",
            )

        return table

    def force_update(self):
        """Trigger an immediate display refresh (called by DownloadManager on state change)."""
        self._update_event.set()

    def start(self):
        """Start the live display. Blocks until all jobs are finished."""
        download_manager.set_on_state_change(self.force_update)

        with Live(
            self._build_renderable(),
            console=self._console,
            refresh_per_second=2,       # Auto-refresh baseline; force_update() triggers immediate refreshes
        ) as live:
            self._live = live

            while not download_manager.is_finished():
                try:
                    live.update(self._build_renderable())
                except Exception:
                    pass
                self._update_event.wait(timeout=4.0)
                self._update_event.clear()

            # Final render with everything completed
            live.update(self._build_renderable())

        self._live = None


# Global instance
download_display = DownloadDisplay()
