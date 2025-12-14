import argparse
import sys

from .agent import DeepResearchAgent


def main():
    parser = argparse.ArgumentParser(description="Deep Research Agent CLI")
    parser.add_argument("prompt", help="The research prompt to execute")
    parser.add_argument(
        "--agent-name",
        default="deep-research-pro-preview-12-2025",
        help="Name of the agent to use",
    )
    parser.add_argument(
        "--output",
        help="Path to save the research report",
    )

    args = parser.parse_args()

    try:
        agent = DeepResearchAgent(agent_name=args.agent_name)
        agent.research(args.prompt, output_path=args.output)
    except KeyboardInterrupt:
        print("\nResearch cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
