import os
import time

from google import genai
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner


class DeepResearchAgent:
    def __init__(self, agent_name="deep-research-pro-preview-12-2025"):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.agent_name = agent_name
        self.last_event_id = None
        self.interaction_id = None
        self.console = Console()

    def start_research_stream(self, prompt, agent_config=None):
        """
        Generates a robust stream of events, handling reconnection automatically.
        Yields all events from the underlying API.
        """
        if agent_config is None:
            agent_config = {"type": "deep-research", "thinking_summaries": "auto"}

        retry_delay = 2
        max_delay = 60
        is_complete = False

        # 1. Initial Request
        try:
            stream = self.client.interactions.create(
                input=prompt,
                agent=self.agent_name,
                background=True,
                stream=True,
                agent_config=agent_config,
                timeout=None,
            )
            for event in stream:
                yield event
                if event.event_type == "interaction.start":
                    self.interaction_id = event.interaction.id
                if event.event_id:
                    self.last_event_id = event.event_id
                if event.event_type in ["interaction.complete", "error"]:
                    is_complete = True

            # If stream finishes normally without complete/error (e.g. empty), consider it done or handle?
            # Usually strict stream end means connection close.

        except Exception as e:
            # If we haven't established an interaction yet, we can't reconnect.
            # Re-raise the exception to notify the user.
            if not self.interaction_id:
                raise e
            # Initial connection failed or dropped mid-stream; proceed to reconnection loop.
            pass

        # 2. Reconnection Loop
        while not is_complete and self.interaction_id:
            try:
                # Attempt reconnection immediately; sleep only on failure (see except block)
                stream = self.client.interactions.get(
                    id=self.interaction_id,
                    stream=True,
                    last_event_id=self.last_event_id,
                    timeout=None,
                )

                # Reset delay on successful connection
                retry_delay = 2

                for event in stream:
                    yield event
                    if event.event_id:
                        self.last_event_id = event.event_id
                    if event.event_type in ["interaction.complete", "error"]:
                        is_complete = True

            except Exception:
                # Reconnection failed; back off and retry
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)
                # Ensure we don't busy loop too fast if sleep raises
                if retry_delay < 1:
                    retry_delay = 1

    def research(self, prompt, agent_config=None, output_path=None):
        """Starts and manages the research task with UI."""
        out_file = None
        if output_path:
            out_file = open(output_path, "w", encoding="utf-8")

        accumulated_text = ""
        current_thought = "Connecting..."
        is_complete = False

        def generate_view():
            elements = [Markdown(accumulated_text)]
            if not is_complete:
                elements.append(
                    Panel(
                        Spinner("dots", style="magenta", text=current_thought),
                        title="Deep Research Agent",
                        border_style="blue",
                        padding=(0, 1),
                    )
                )
            return Group(*elements)

        try:
            with Live(
                generate_view(), refresh_per_second=10, console=self.console
            ) as live:
                # Use the robust stream generator
                for event in self.start_research_stream(prompt, agent_config):
                    if event.event_type == "interaction.start":
                        current_thought = "Research Started..."
                        live.update(generate_view())

                    if event.event_type == "content.delta":
                        if event.delta.type == "text":
                            text = event.delta.text
                            accumulated_text += text
                            if out_file:
                                out_file.write(text)
                                out_file.flush()
                            live.update(generate_view())
                        elif event.delta.type == "thought_summary":
                            current_thought = event.delta.content.text
                            live.update(generate_view())

                    if event.event_type in ["interaction.complete", "error"]:
                        is_complete = True
                        live.update(generate_view())
                        if event.event_type == "error":
                            self.console.print(
                                f"[bold red]\nError: {event.error}[/bold red]"
                            )
                            if "Function call is empty" in str(event.error):
                                self.console.print(
                                    "[yellow]Tip: This is a known intermittent issue with the Deep Research Preview model. Please try running the command again.[/yellow]"
                                )

        finally:
            if out_file:
                out_file.close()
