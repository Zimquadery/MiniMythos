# MiniMythos

AI Security Boss — orchestrates headless agents to find proven security bugs.

## Installation

### From GitHub

```bash
pip install git+https://github.com/Zimquadery/MiniMythos.git
```

### Editable install (for development)

```bash
git clone https://github.com/Zimquadery/MiniMythos.git
cd MiniMythos
pip install -e ".[dev]"
```

## Usage

```bash
minimythos /path/to/codebase [options]
```

| Option              | Description                             | Default       |
|---------------------|-----------------------------------------|---------------|
| `-a, --agent`       | Agent CLI command (e.g. `opencode`)     | `opencode`    |
| `-b, --batch-size`  | Number of files per scoring batch       | `10`          |
| `-t, --threshold`   | Min vulnerability score (1-10)          | `7`           |
| `-p, --max-parallel`| Max concurrent agents                   | `5`           |
| `-o, --output`      | Output directory for reports            | target path   |


## License

MIT
