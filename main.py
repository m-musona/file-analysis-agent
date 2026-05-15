import os, sys, argparse
from agent.loop import run_agent

from dotenv import load_dotenv

load_dotenv()


def main():
    p = argparse.ArgumentParser(description="AI file analysis agent")
    p.add_argument("file", help="Path to file to analyze")
    p.add_argument("query", help="Natural-language question about the file")
    p.add_argument("--output", "-o", help="Write result to this file instead of stdout")
    args = p.parse_args()

    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit("Error: GEMINI_API_KEY environment variable not set.")
    if not os.path.exists(args.file):
        sys.exit(f"Error: File not found: {args.file}")

    result = run_agent(
        args.file, args.query
    )  # always returns Markdown from write_report

    if args.output:
        open(args.output, "w").write(result)
        print(f"Report written to {args.output}")
    else:
        print(result)
        print("\n[Structured report also saved to: report.md]")


if __name__ == "__main__":
    main()
