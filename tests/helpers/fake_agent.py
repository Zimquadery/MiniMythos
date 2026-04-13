import sys
import json


def main():
    prompt = ""
    for i, arg in enumerate(sys.argv):
        if arg == "--prompt" and i + 1 < len(sys.argv):
            prompt = sys.argv[i + 1]
            break

    if "score" in prompt.lower():
        print(json.dumps([{"path": "src/main.py", "score": 5, "reason": "test score"}]))
    elif "attack" in prompt.lower():
        print(json.dumps({"vulnerabilities": [], "evidence": "test evidence"}))
    else:
        print(prompt)


if __name__ == "__main__":
    main()
