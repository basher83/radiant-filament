import argparse
import json
import os
import sys

from .agent import DeepResearchAgent


def parse_agent_config(value):
    """Parse agent config from JSON string or file path."""
    if value is None:
        return None

    # Try as file path first
    if os.path.isfile(value):
        try:
            with open(value, encoding="utf-8") as f:
                return json.load(f)
        except OSError as e:
            raise argparse.ArgumentTypeError(f"Cannot read '{value}': {e}") from None
        except json.JSONDecodeError as e:
            raise argparse.ArgumentTypeError(
                f"Invalid JSON in '{value}': {e}"
            ) from None

    # Otherwise parse as JSON string
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise argparse.ArgumentTypeError(f"Invalid JSON: {e}") from None


def validate_file_search_store(value):
    """Validate file search store name format."""
    if not value.startswith("fileSearchStores/"):
        raise argparse.ArgumentTypeError(
            f"Invalid store format: {value}. Expected: fileSearchStores/<name>"
        )
    return value


def main():
    parser = argparse.ArgumentParser(
        description="Deep Research Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic research
  %(prog)s "Research the history of quantum computing"

  # Save output to file
  %(prog)s "Research AI trends" --output report.md

  # Use polling instead of streaming
  %(prog)s "Research topic" --no-stream

  # Research using a prompt file
  %(prog)s --prompt-file prompt.md --output report.md

  # Follow-up on previous research
  %(prog)s "Elaborate on point 2" --previous-interaction-id <id>

  # Quick follow-up with a model (no deep research)
  %(prog)s "Summarize in 3 bullets" --previous-interaction-id <id> --model gemini-2.5-pro

  # Research with file search
  %(prog)s "Analyze our Q1 report" --file-search fileSearchStores/my-store

  # Custom agent config
  %(prog)s "Research topic" --agent-config '{"thinking_summaries": "none"}'
""",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="The research prompt to execute",
    )
    parser.add_argument(
        "--prompt-file",
        metavar="PATH",
        help="Path to a file containing the research prompt (e.g., prompt.md)",
    )
    parser.add_argument(
        "--agent-name",
        default="deep-research-pro-preview-12-2025",
        help="Name of the agent to use (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Path to save the research report",
    )
    parser.add_argument(
        "--previous-interaction-id",
        metavar="ID",
        help="Continue from a completed interaction (for follow-up questions)",
    )
    parser.add_argument(
        "--model",
        metavar="NAME",
        help="Use a model instead of agent for follow-ups (e.g., gemini-2.5-pro)",
    )
    parser.add_argument(
        "--file-search",
        action="append",
        type=validate_file_search_store,
        metavar="STORE",
        dest="file_search_stores",
        help="File search store name (can be repeated for multiple stores)",
    )
    parser.add_argument(
        "--agent-config",
        metavar="JSON",
        help="Agent config as JSON string or path to JSON file",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Use polling mode instead of streaming",
    )

    args = parser.parse_args()

    # Validation: exactly one of prompt or --prompt-file required
    if args.prompt and args.prompt_file:
        parser.error("Cannot use both positional prompt and --prompt-file")
    if not args.prompt and not args.prompt_file:
        parser.error("Must provide either a prompt or --prompt-file")

    # Read prompt from file if provided
    if args.prompt_file:
        try:
            with open(args.prompt_file, encoding="utf-8") as f:
                args.prompt = f.read()
        except OSError as e:
            parser.error(f"Cannot read prompt file '{args.prompt_file}': {e}")

    # Validation: --model requires --previous-interaction-id
    if args.model and not args.previous_interaction_id:
        parser.error("--model requires --previous-interaction-id")

    # Parse agent config
    try:
        agent_config = parse_agent_config(args.agent_config)
    except argparse.ArgumentTypeError as e:
        parser.error(str(e))

    # Build tools list if file search stores provided
    tools = None
    if args.file_search_stores:
        tools = [
            {
                "type": "file_search",
                "file_search_store_names": args.file_search_stores,
            }
        ]

    try:
        agent = DeepResearchAgent(agent_name=args.agent_name)
        research_method = agent.research_poll if args.no_stream else agent.research
        research_method(
            args.prompt,
            agent_config=agent_config,
            output_path=args.output,
            previous_interaction_id=args.previous_interaction_id,
            model=args.model,
            tools=tools,
        )
    except KeyboardInterrupt:
        print("\nResearch cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
