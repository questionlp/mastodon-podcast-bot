# mastodon-podcast-bot

Python application that parses a podcast RSS/Atom feed and publishes a post to a Mastodon account if it sees a new entry.

## Requirements

This application requires Python 3.10 or higher.

Running this application using any version of Python below 3.10 or using a Python interpreter that does not support language features included in Python 3.10 is **not** supported.

## Installing

It is highly recommended that you set up a virtual environment for this application and install the dependencies within the virtual environment. The following example uses Python's `venv` module to create the virtual environment, once a copy of this repository as been cloned locally.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Once the dependencies have been installed, make a copy of the `.env.dist` file and name the file `.env`. This file will contain configuration settings that the application will need.

| Setting | Description |
|---------|-------------|
| DB_FILE | Location of the SQLite3 file that will be used to store episodes that the application has already been processed. |
| DB_CLEAN_DAYS | Number of days to keep records in the SQLite3. Used by the clean-up function to remove older entries. This value should be greater than the value set for `RECENT_DAYS`. (Default: 90) |
| RECENT_DAYS | Number of days in a podcast RSS feed to process. Any episodes older than that will be skipped. (Default: 5) |
| MAX_EPISODES | Maximum number of episodes to retrieve from the podcast feed. (Default: 50) |
| PODCAST_FEED | URL for the podcast feed the application will pull episodes from. |
| PODCAST_NAME | Name of the podcast to be included in the post. |
| PODCAST_GUID_FILTER | String used as a filter episode GUIDs values to include and exclude GUIDs that to not include the string. |
| POST_TEMPLATE_DIR | Path of the directory containing the Jinja2 template file. |
| POST_TEMPLATE | File name of the Jinja2 template file that will be used to format the post. |
| MASTODON_SECRET | OAuth secret file that will be used to authenticate your Mastodon user account against your Mastodon server. |
| MASTODON_API_BASE_URL | The base API URL for your Mastodon instance. Refer to your Mastodon instance for the appropriate URL to use. |

To create the Mastodon OAuth secret file, refer to the [Mastodon.py](https://mastodonpy.readthedocs.io/en/stable/) documentation for instructions. Any secret files should be stored under `secrets/`, as any file (with exception of the included [README.md](secrets/README.md) file) are filtered out by way of the repository's `.gitignore`.

Running the application can be done by running the following command:

```bash
python3 podcast_bot.py
```

The application will automatically create the SQLite3 database if one does not already exist.

There are several flags and options that can be set through the command line:

| Flag/Argument | Description |
|---------------|-------------|
| `--dry-run` | Runs the application, but skips creating any database entries (though a database file if one doesn't exist) and does not create any posts. |
| `--skip-clean` | Skips the database clean-up step to remove old entries. This step is also skipped if the `--dry-run` flag is also set. |
| `--env file` | Set a custom path for the `.env` file that contains the required application settings. |

## Development

This application makes generous use to type hints to help with code documentation and can be very helpful when using Python language servers in Visual Studio Code, tools such as [mypy](http://mypy-lang.org), and others.

## Code of Conduct

This project follows version 2.1 of the [Contributor Covenant's](https://www.contributor-covenant.org) Code of Conduct.

## License

This application is licensed under the terms of the [MIT License](LICENSE).
