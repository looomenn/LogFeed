[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua/)

# LogFeed

A small tool for visualising evtx logs in feed-like manner.

![Preview](assets/screenshot.png)

## Usage

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1.  Clone the repository:

    ```bash
    git clone https://github.com/looomenn/LogFeed.git
    cd LogFeed
    ```

2.  Run the application:
    ```bash
    uv run streamlit run main.py
    ```

## Project Structure

```text
LogFeed/
├── modules/
│   ├── parser.py        # evtx parser module
│   └── ui.py            # html/css
├── main.py              # main application file
├── pyproject.toml       # dependency configuration
└── README.md
```

# License

MIT © [Ange1o](https://github.com/looomenn)
