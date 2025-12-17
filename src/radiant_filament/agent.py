import os
import time

from google import genai
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner


class DeepResearchAgent:
    DEFAULT_AGENT_CONFIG = {"type": "deep-research", "thinking_summaries": "auto"}

    def __init__(
        self,
        agent_name: str = "deep-research-pro-preview-12-2025",
        *,
        client: genai.Client | None = None,
    ):
        """Initialize the DeepResearchAgent.

        Args:
            agent_name: The Gemini agent version to use.
            client: Optional pre-configured genai.Client. If not provided,
                creates one using GEMINI_API_KEY environment variable.

        Raises:
            ValueError: If client is None and GEMINI_API_KEY is not set.
        """
        if client is not None:
            self.client = client
        else:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY environment variable is required. "
                    "Get your key at https://aistudio.google.com/app/apikey"
                )
            self.client = genai.Client(api_key=api_key)
        self.agent_name = agent_name
        self.last_event_id = None
        self.interaction_id = None
        self.console = Console()

    def _merge_agent_config(self, user_config):
        """Merge user config with defaults. User values override defaults.

        Args:
            user_config: Optional dict of config overrides. If None, returns defaults.

        Returns:
            dict: Merged configuration with DEFAULT_AGENT_CONFIG as base.
        """
        if user_config is None:
            return self.DEFAULT_AGENT_CONFIG.copy()
        return {**self.DEFAULT_AGENT_CONFIG, **user_config}

    def start_research_stream(
        self,
        prompt,
        agent_config=None,
        previous_interaction_id=None,
        model=None,
        tools=None,
    ):
        """
        Generates a robust stream of events, handling reconnection automatically.
        Yields all events from the underlying API.

        Args:
            prompt: The research prompt or follow-up question.
            agent_config: Optional config to override defaults.
            previous_interaction_id: For follow-up questions on completed research.
            model: Use a model instead of agent. When provided, agent_config is
                ignored. Typically used with previous_interaction_id for follow-ups.
            tools: List of tools (e.g., file_search) for the agent to use.

        Yields:
            Event objects from the API with event_type attribute. Key types:
            interaction.start, content.delta, interaction.complete, error.

        Raises:
            RuntimeError: If reconnection fails after max_retries attempts.
            ConnectionError, TimeoutError, OSError: If initial connection fails
                before an interaction is established.
        """
        merged_config = self._merge_agent_config(agent_config)

        retry_delay = 2
        max_delay = 60
        max_retries = 10
        retry_count = 0
        is_complete = False

        # 1. Initial Request
        try:
            # Build request kwargs
            create_kwargs = {
                "input": prompt,
                "background": True,
                "stream": True,
                "timeout": None,
            }

            # Use model if provided, otherwise use agent
            if model:
                create_kwargs["model"] = model
            else:
                create_kwargs["agent"] = self.agent_name
                create_kwargs["agent_config"] = merged_config

            # Add optional parameters
            if previous_interaction_id:
                create_kwargs["previous_interaction_id"] = previous_interaction_id

            if tools:
                create_kwargs["tools"] = tools

            stream = self.client.interactions.create(**create_kwargs)
            for event in stream:
                yield event
                if event.event_type == "interaction.start":
                    self.interaction_id = event.interaction.id
                if event.event_id:
                    self.last_event_id = event.event_id
                if event.event_type in ["interaction.complete", "error"]:
                    is_complete = True

        except (ConnectionError, TimeoutError, OSError) as e:
            # If we haven't established an interaction yet, we can't reconnect.
            # Re-raise the exception to notify the user.
            if not self.interaction_id:
                raise
            # Initial connection dropped mid-stream; proceed to reconnection loop.
            self.console.print(
                f"[yellow]Stream interrupted: {e}. Reconnecting...[/yellow]"
            )

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

                # Reset retry count on successful stream processing
                retry_count = 0

            except (ConnectionError, TimeoutError, OSError) as e:
                # Reconnection failed; back off and retry
                retry_count += 1
                self.console.print(
                    f"[yellow]Connection interrupted: {e}. "
                    f"Reconnecting ({retry_count}/{max_retries})...[/yellow]"
                )
                if retry_count >= max_retries:
                    raise RuntimeError(
                        f"Failed to reconnect after {max_retries} attempts: {e}"
                    ) from e
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)

    def research(
        self,
        prompt,
        agent_config=None,
        output_path=None,
        previous_interaction_id=None,
        model=None,
        tools=None,
    ):
        """Starts and manages the research task with UI.

        Args:
            prompt: The research prompt or follow-up question.
            agent_config: Optional config to override defaults.
            output_path: Path to save the research report.
            previous_interaction_id: For follow-up questions on completed research.
            model: Use a model instead of agent. When provided, agent_config is
                ignored. Typically used with previous_interaction_id for follow-ups.
            tools: List of tools (e.g., file_search) for the agent to use.

        Raises:
            RuntimeError: If output_path cannot be opened for writing, if the
                API returns an error event, or if reconnection fails.
        """
        out_file = None
        if output_path:
            try:
                out_file = open(output_path, "w", encoding="utf-8")
            except OSError as e:
                raise RuntimeError(f"Cannot write to '{output_path}': {e}") from e

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
                for event in self.start_research_stream(
                    prompt,
                    agent_config=agent_config,
                    previous_interaction_id=previous_interaction_id,
                    model=model,
                    tools=tools,
                ):
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
                            error_str = str(event.error)
                            self.console.print(
                                f"[bold red]\nError: {event.error}[/bold red]"
                            )
                            if "Function call is empty" in error_str:
                                self.console.print(
                                    "[yellow]Tip: This is a known intermittent issue with the Deep Research Preview model. Please try running the command again.[/yellow]"
                                )
                            raise RuntimeError(f"Research error: {error_str}")

        finally:
            if out_file:
                out_file.close()

    def research_poll(
        self,
        prompt,
        agent_config=None,
        output_path=None,
        previous_interaction_id=None,
        model=None,
        tools=None,
        poll_interval=5,
    ):
        """Starts and manages the research task using polling instead of streaming.

        Args:
            prompt: The research prompt or follow-up question.
            agent_config: Optional config to override defaults.
            output_path: Path to save the research report.
            previous_interaction_id: For follow-up questions on completed research.
            model: Use a model instead of agent. When provided, agent_config is
                ignored. Typically used with previous_interaction_id for follow-ups.
            tools: List of tools (e.g., file_search) for the agent to use.
            poll_interval: Seconds between status polls (default: 5).

        Raises:
            RuntimeError: If output_path is not writable, research fails, is
                cancelled, requires action, or completes without output.
            TimeoutError: If polling exceeds max_polls (~1 hour at default interval).
        """
        # Validate output path early (consistent with research() behavior)
        if output_path:
            parent_dir = os.path.dirname(output_path) or "."
            if not os.path.isdir(parent_dir):
                raise RuntimeError(
                    f"Cannot write to '{output_path}': directory does not exist"
                )
            if not os.access(parent_dir, os.W_OK):
                raise RuntimeError(
                    f"Cannot write to '{output_path}': directory not writable"
                )

        merged_config = self._merge_agent_config(agent_config)

        # Build request kwargs
        create_kwargs = {
            "input": prompt,
            "background": True,
            "stream": False,
        }

        if model:
            create_kwargs["model"] = model
        else:
            create_kwargs["agent"] = self.agent_name
            create_kwargs["agent_config"] = merged_config

        if previous_interaction_id:
            create_kwargs["previous_interaction_id"] = previous_interaction_id

        if tools:
            create_kwargs["tools"] = tools

        # Create the interaction
        try:
            interaction = self.client.interactions.create(**create_kwargs)
        except Exception as e:
            self.console.print(f"[bold red]Failed to start research: {e}[/bold red]")
            raise

        self.interaction_id = interaction.id
        current_status = interaction.status
        poll_count = 0
        poll_errors = 0
        max_poll_errors = 3
        max_polls = 720  # ~1 hour at 5s intervals

        def generate_view():
            return Panel(
                Spinner("dots", style="magenta", text=f"Status: {current_status}"),
                title="Deep Research Agent (Polling)",
                border_style="blue",
                padding=(0, 1),
            )

        with Live(generate_view(), refresh_per_second=4, console=self.console) as live:
            while current_status == "in_progress":
                if poll_count >= max_polls:
                    timeout_msg = (
                        f"Research timed out after {poll_count * poll_interval}s"
                    )
                    self.console.print(f"[bold red]{timeout_msg}[/bold red]")
                    raise TimeoutError(timeout_msg)

                time.sleep(poll_interval)
                poll_count += 1

                try:
                    interaction = self.client.interactions.get(id=self.interaction_id)
                    poll_errors = 0  # Reset on success
                except (ConnectionError, TimeoutError, OSError) as e:
                    poll_errors += 1
                    if poll_errors >= max_poll_errors:
                        self.console.print(
                            f"[bold red]Polling failed after {max_poll_errors} "
                            f"errors: {e}[/bold red]"
                        )
                        raise
                    self.console.print(f"[yellow]Poll error: {e}. Retrying...[/yellow]")
                    continue

                current_status = interaction.status
                live.update(generate_view())

        # Handle final status
        if current_status == "requires_action":
            msg = f"Research requires action. Interaction ID: {self.interaction_id}"
            self.console.print(f"[yellow]{msg}[/yellow]")
            raise RuntimeError(msg)

        if current_status == "failed":
            error_msg = getattr(interaction, "error", None) or "Unknown error"
            self.console.print(f"[bold red]Research failed: {error_msg}[/bold red]")
            raise RuntimeError(f"Research failed: {error_msg}")

        if current_status == "cancelled":
            self.console.print("[yellow]Research was cancelled.[/yellow]")
            raise RuntimeError("Research was cancelled")

        if current_status == "completed":
            # Extract final report from text outputs
            if interaction.outputs:
                # Find all text outputs and concatenate them
                text_parts = [
                    output.text
                    for output in interaction.outputs
                    if output.type == "text" and output.text
                ]
                if text_parts:
                    report_text = "".join(text_parts)
                    self.console.print(Markdown(report_text))

                    if output_path:
                        try:
                            with open(output_path, "w", encoding="utf-8") as f:
                                f.write(report_text)
                            self.console.print(
                                f"\n[green]Report saved to {output_path}[/green]"
                            )
                        except OSError as e:
                            self.console.print(
                                f"[bold red]Failed to save report: {e}[/bold red]"
                            )
                            raise RuntimeError(
                                f"Failed to save report to '{output_path}': {e}"
                            ) from e
                else:
                    msg = "Research completed but no text output was received"
                    self.console.print(f"[yellow]{msg}[/yellow]")
                    raise RuntimeError(msg)
            else:
                msg = "Research completed but no output was received"
                self.console.print(f"[yellow]{msg}[/yellow]")
                raise RuntimeError(msg)
