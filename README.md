# mastodon-podcast-bot

Python script that parses a podcast RSS/Atom feed and publishes a post to a Mastodon account if it sees a new entry.

## Requirements

This project requires Python 3.10 or higher.

Running scripts included in this project using any version of Python below 3.10 or using a Python interpreter that does not support language features included in Python 3.10 is **not** supported.

## Installing

It is highly recommended that you set up a virtual environment for this project and install the dependencies within the virtual environment. The following example uses Python's `venv` module to create the virtual environment, once a copy of this repository as been cloned locally.

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Running the Script

Starting with version 1.0, the script supports using either an `.env` environment file to store configuration information for a single feed or a `feeds.json` JSON file to store configuration information for multiple feeds.

The script will automatically create the SQLite3 database if one does not already exist.

### Mastodon Credentials and Authentication

To create the Mastodon OAuth secret file, refer to the [Mastodon.py](https://mastodonpy.readthedocs.io/en/stable/) documentation for instructions. Any secret files should be stored under `secrets/`, as any file (with exception of the included [README.md](secrets/README.md) file) are filtered out by way of the repository's `.gitignore`.

### Command-Line Flags and Options

There are several flags and options that can be set through the command line:

| Flag/Option | Description |
|---------------|-------------|
| `--dry-run` | Runs the scripts, but skips creating any database entries (though a database file if one doesn't exist) and does not create any posts. |
| `-e`, `--env-file` | Set a custom path for the `.env` file that contains the required podcast feed and configuration settings. |
| `-f`, `--feeds-file` | Set a custom path for the feeds JSON file that contains the required podcast feed and configuration settings. |
| `-m`, `--multiple-feeds` | Runs the script in multi-feed mode, which uses information stored in a podcast feed JSON file. |
| `--skip-clean` | Skips the database clean-up step to remove old entries. This step is also skipped if the `--dry-run` flag is also set. |

### Single Feed .env File

Once the dependencies have been installed, make a copy of the `.env.dist` file and name the file `.env`. This file will contain configuration settings that the script will need.

| Setting | Description |
|---------|-------------|
| PODCAST_NAME | Name of the podcast to be included in the post. |
| PODCAST_FEED_URL | URL for the podcast feed to retrieve and parse episodes. |
| MASTODON_USE_SECRETS_FILE | Set whether or not a Mastodon secrets file will be used for authenticiation. (Default: True ) |
| MASTODON_SECRETS_FILE (or MASTODON_SECRET) | OAuth secret file that will be used to authenticate your Mastodon user account against your Mastodon server. Note that the `MASTODON_SECRETS_FILE` setting is replacing the `MASTODON_SECRET` setting. The value from `MASTODON_SECRET` is still being read, but the setting will be deprecated in the near future. |
| MASTODON_CLIENT_SECRET | Mastodon API client secret used for authentication. |
| MASTODON_ACCESS_TOKEN | Mastodon API access token used for authentiication. |
| MASTODON_API_BASE_URL | The base API URL for your Mastodon instance. Refer to your Mastodon instance for the appropriate URL to use. |
| DB_FILE | Location of the SQLite3 file that will be used to store episodes that the script has already been processed. |
| DB_CLEAN_DAYS | Number of days to keep records in the SQLite3. Used by the clean-up function to remove older entries. This value should be greater than the value set for `RECENT_DAYS`. (Default: 90) |
| LOG_FILE | Path for the log file the script will use to log events to. If no log file path is provided, logging will be disabled. |
| RECENT_DAYS | Number of days in a podcast RSS feed to process. Any episodes older than that will be skipped. (Default: 5) |
| MAX_EPISODES | Maximum number of episodes to retrieve from the podcast feed and process. (Default: 50) |
| MAX_DESCRIPTION_LENGTH | Maximum length (in characters) of the podcast episode description to be included in the post. (Default: 275) |
| PODCAST_GUID_FILTER | String used as a filter episode GUIDs values to include and exclude GUIDs that to not include the string. |
| USER_AGENT | User Agent string to provide when retrieving a podcast feed. (Default: User Agent string for Firefox 122 on Linux). |
| POST_TEMPLATE_DIR | Path for the directory containing the Jinja2 template file. |
| POST_TEMPLATE | Path for the Jinja2 template file that will be used to format the post. |

### Multiple Feed feeds.json File

The `feeds.json` file needs to be a valid JSON file that contains an array of objects, one for each podcast, with the following attributes:

| Attribute | Description |
|---------|-------------|
| name | Name of the podcast to be included in the post. |
| database_file | Location of the SQLite3 file that will be used to store episodes that the script has already been processed. |
| database_clean_days | Number of days to keep records in the SQLite3. Used by the clean-up function to remove older entries. This value should be greater than the value set for `recent_days`. (Default: 90) |
| recent_days | Number of days in a podcast RSS feed to process. Any episodes older than that will be skipped. (Default: 5) |
| max_episodes | Maximum number of episodes to retrieve from the podcast feed and process. (Default: 50) |
| log_file | Path for the log file the script will use to log events to. If no log file path is provided, logging will be disabled. |
| max_description_length | Maximum length (in characters) of the podcast episode description to be included in the post. (Default: 275) |
| podcast_feed_url | URL for the podcast feed to retrieve and parse episodes. |
| short_name | Short podcast identifier used to tag each entry in the database. |
| podcast_guid_filter | String used as a filter episode GUIDs values to include and exclude GUIDs that to not include the string. |
| mastodon_use_secrets_file | Set whether or not a Mastodon secrets file will be used for authenticiation. (Default: True ) |
| mastodon_secrets_file (or mastodon_secret) | OAuth secret file that will be used to authenticate your Mastodon user account against your Mastodon server. Note that the `mastodon_secrets_file` key is replacing the `mastodon_secret` key. The value from `mastodon_secret` is still being read, but the setting will be deprecated in the near future. |
| mastodon_client_secret | Mastodon API client secret used for authentication. |
| mastodon_access_token | Mastodon API access token used for authentiication. |
| mastodon_api_base_url | The base API URL for your Mastodon instance. Refer to your Mastodon instance for the appropriate URL to use. |
| user_agent | User Agent string to provide when retrieving a podcast feed. (Default: User Agent string for Firefox 122 on Linux). |
| template_directory | Path for the directory containing the Jinja2 template file. |
| template_file | Path for the Jinja2 template file that will be used to format the post. |

## Development

Use the included `requirements-dev.txt` to install both the script and script development dependencies.

The project makes generous use to type hints to help with code documentation and can be very helpful when using Python language servers in Visual Studio Code, tools such as [mypy](http://mypy-lang.org), and others.

For code linting and formatting, the project makes use of Ruff and Black.

## Code of Conduct

This project follows version 2.1 of the [Contributor Covenant's](https://www.contributor-covenant.org) Code of Conduct.

## License

This project is licensed under the terms of the [MIT License](LICENSE).
