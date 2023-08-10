# analytics-digest-helper

This helper is used to generate the analytics digest twitter thread based on the [Dune dashboard](https://dune.com/lido/lido-weekly-digest).

## Overview

The script fetches data from the Dune Dashboard, processes it, and generates a markdown file that serves as the basis for the Twitter thread. The markdown file is then saved in the `threads` directory with the date as the filename.

The script also generates graphs based on the fetched data and saves them in the `graphs` directory.

## How it Works

The script uses the `dune-client` package to fetch data from the Dune Dashboard. Dune data is processed in chunks for each query, before being sent to GPT3.5/4 to write each section of the thread and then compose the entire thread.

The script also uses the `matplotlib` and `seaborn` packages to generate relevant graphs based on the fetched data.

## Setup

1. Clone the repository.
2. Install the required Python packages using the command `poetry install`.
3. Set up the environment variables. Example environment variables in `.env.example`
4. Run the script using the command `python3 main.py`. The script can also be run with specified start and end dates with `python3 main.py --sd <START_DATE like "2023-07-31"> --ed <END_DATE like "2023-08-06">` to specify the digest dates manually.
