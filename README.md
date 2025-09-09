## About
Python library to call the APIs that the store itself calls.  
To get good parsed results from those API calls see [`parser.py`](https://github.com/allendema/rewe_dl/blob/main/rewe_dl/parser.py).  

*NOTE: THIS CODE WILL SOON BE PART OF ANOTHER PROJECT - AND SO IT WILL MOVED INTO ANOTHER REPOSITORY.*

[![Python Version from PEP 621 TOML](https://shields.sp-codes.de/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fallendema%2Frewe_dl%2Fmain%2Fpyproject.toml)](https://github.com/allendema/rewe_dl/main/pyproject.toml)
[![Formatter](https://shields.sp-codes.de/badge/formatter-ruff-blue)](https://github.com/astral-sh/ruff)
[![github commits](https://shields.sp-codes.de/github/last-commit/allendema/rewe_dl)](https://github.com/allendema/rewe_dl/commits/main)

## Usage
<details>
    <summary>Prerequisites</summary>

    sudo apt-get install git
    python -m ensurepip --upgrade

</details>

```bash
git clone https://github.com/allendema/rewe_dl && cd rewe_dl
```  
```bash
pip install requirements.txt
```  
```bash
pip install -e rewe_dl
```

Optional [apprise](https://github.com/caronc/apprise/wiki/) can be used to send send notifications to more than 100 services/apps.

See [Config](https://github.com/allendema/rewe_dl/main/README.md#config) options!


## Examples
You can:
  - save product infos to JSON
  - save product infos to JSONL
  - save product infos to SQL
  - save product images
  - save product calories or other details
  - monitor your _basket_ with your fav products
  - compare prices and get notified when prices change
  - save products to SQL for further analysis
  - analyse the output data the way you like, for example: inflation analysis.
  - _and_ whatever you want.


<details>
    <summary>examples/discounted_to_json.py</summary>
    https://github.com/allendema/rewe_dl/blob/7948de8ebc401af4791cdd66fd928daac58d749e/rewe_dl/examples/discounted_to_json.py#L26-L37
</details>

<details>
    <summary>examples/discounted_to_sql.py</summary>
    https://github.com/allendema/rewe_dl/blob/7948de8ebc401af4791cdd66fd928daac58d749e/rewe_dl/examples/discounted_to_sql.py#L23-L35
</details>

<details>
    <summary>examples/my_basket.py</summary>
    https://github.com/allendema/rewe_dl/blob/7948de8ebc401af4791cdd66fd928daac58d749e/rewe_dl/examples/my_basket.py#L23-L37
</details>

<details>
    <summary>examples/newest_products_to_sql.py</summary>
    https://github.com/allendema/rewe_dl/blob/7948de8ebc401af4791cdd66fd928daac58d749e/rewe_dl/examples/newest_products_to_sql.py#L19-L26
</details>

<details>
    <summary>examples/notify_when_price.py</summary>
    https://github.com/allendema/rewe_dl/blob/7948de8ebc401af4791cdd66fd928daac58d749e/rewe_dl/examples/notify_when_price.py#L54-L66
</details>

<details>
    <summary>examples/raw_responses_to_json.py</summary>
    https://github.com/allendema/rewe_dl/blob/7948de8ebc401af4791cdd66fd928daac58d749e/rewe_dl/examples/raw_responses_to_json.py#L26-L43
</details>


See `rewe_dl/examples` folder for some more starting examples to embedd it into your own project.


## Config
### Getting the cookies
Depending on store location, some stores will have different prices.

To not use the default store, go to [https://shop.rewe.de](https://shop.rewe.de)  
and select your pickup store.

Right click -> Inspect source -> Web Storage -> Cookies  
and copy the value from `marketsCookie` into the `config.json` file.


### Notifications/Webhooks
If you don't want to install apprise, you can use [matrix.org](https://matrix.org) or [telegram.org](https://telegram.org).  

- Matrix:
    Fill the `matrix` dict in `rewe_dl/config.json` file.
- Telegram:
    Fill the `telegram` dict in `rewe_dl/config.json` file.
- Apprise (Optional): The config file in `~/.config/apprise` (without any extension) will be used.  
    Configure your wanted notifications/webhooks options based on the [wiki](https://github.com/caronc/apprise/wiki/).


## Changes
API endpoints or data structure might change!
If you have any issues report them or open a pull request.

This project will be a part of another project which uses multiple stores using an REST API with Fastapi.


<details>

<summary>Development</summary>

### Development
If you want to modify something:  
  - `pip install requirements-dev.txt`
  - The `pyproject.toml` file is used for linting/formatting with `ruff`.
  - Make your changes.
  - If you add tests, run them with `python3 ./scripts/run_tests.py`.
  - Run `ruff check --fix .`
  - Run `ruff format .`
  - Create a [Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).

</details>


## Credits
Inspired from [gallery-dl](https://github.com/mikf/gallery-dl), the code structure is similiar and some is code straight reused.  
Where applicable - docstrings point to original code creators.
