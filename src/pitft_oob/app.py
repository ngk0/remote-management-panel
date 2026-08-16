from __future__ import annotations

import threading

from pitft_oob.ports.clock import Clock
from pitft_oob.ports.display import DisplayPort
from pitft_oob.ports.input import InputPort
from pitft_oob.registry import PollingStatusService
from pitft_oob.ui.controller import PanelController
from pitft_oob.ui.render import PillowRenderer


class Application:
    """Responsive input/render loop fed by an independent status poller."""

    def __init__(
        self,
        display: DisplayPort,
        inputs: InputPort,
        status: PollingStatusService,
        controller: PanelController,
        renderer: PillowRenderer,
        clock: Clock,
        clock_redraw_seconds: float = 10.0,
    ) -> None:
        self.display = display
        self.inputs = inputs
        self.status = status
        self.controller = controller
        self.renderer = renderer
        self.clock = clock
        self.clock_redraw_seconds = clock_redraw_seconds
        self._stop = threading.Event()

    def stop(self) -> None:
        self._stop.set()

    def run(self) -> None:
        dirty = True
        last_snapshot_time = None
        next_clock_draw = 0.0
        clear_feedback_at = 0.0
        self.status.start()
        try:
            while not self._stop.is_set():
                snapshot = self.status.latest()
                if snapshot.captured_at != last_snapshot_time:
                    self.controller.set_snapshot(snapshot)
                    last_snapshot_time = snapshot.captured_at
                    dirty = True
                events = self.inputs.poll(0.1)
                for event in events:
                    self.controller.handle(event)
                    clear_feedback_at = self.clock.monotonic() + 0.15
                    dirty = True
                now_monotonic = self.clock.monotonic()
                if clear_feedback_at and now_monotonic >= clear_feedback_at:
                    self.controller.clear_press_feedback()
                    clear_feedback_at = 0.0
                    dirty = True
                if now_monotonic >= next_clock_draw:
                    next_clock_draw = now_monotonic + self.clock_redraw_seconds
                    dirty = True
                if dirty:
                    image = self.renderer.render(self.controller.view(self.clock.now()))
                    self.display.present(image)
                    dirty = False
        finally:
            self.status.close()
            self.inputs.close()
            self.display.close()
