#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright 2023-2024 Allen Dema
from __future__ import annotations

import os
import sys
import atexit
import logging
from time import sleep
from typing import Iterator
from pathlib import Path
from functools import lru_cache
from urllib.parse import urljoin, urlparse, urlencode

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(PROJECT_DIR)
DATA_FOLDER = os.path.join(PROJECT_ROOT, "data")
THIS_FILE = Path(__file__).stem

import exception
from parser import Parser
from constants import Product
from exception import InputFileError

import httpx

log_file = Path(DATA_FOLDER, THIS_FILE + ".log")
file_handler = logging.FileHandler(filename=log_file)
stdout_handler = logging.StreamHandler(stream=sys.stdout)

logging.basicConfig(
    level=logging.INFO,
    format="[{%(filename)s:%(funcName)s:%(lineno)d}] %(levelname)s - %(message)s",
    handlers=[file_handler, stdout_handler],
)

log = logging.getLogger("__name__")


@staticmethod
def set_session(
    current_session: httpx.Client = None,
    default_headers: dict = {},
    default_cookies: dict = {},
    **kwargs,
):
    """
    # all default - session without headers nor cookies
    set_session()

    OR

    # default session - with custom made 'default_headers' and 'default_cookies'
    set_session(None,
                default_headers={"default_key": "default_value"},
                default_cookies={})

    OR

    # custom session
    my_custom_session = httpx.Client(headers={"key": "value"},
                                     cookies={"key": "value"})
    set_session(current_session=my_custom_session)

    """

    if not current_session:
        default = httpx.Client(headers=default_headers, cookies=default_cookies, follow_redirects=True)
        current_session = default

    else:
        current_session.headers.update(**kwargs.get("headers", {}))

    globals()["session"] = current_session

    return globals()["session"]


@atexit.register
def close_session():
    session = globals().get("session")
    if session:
        session.close()


class Config:
    def __repr__(self):
        return self.__class__.__name__

    def __init__(
        self,
        base_url="https://www.rewe.de/",
        # ONLY store_id's on www.rewe.de/shop
        store_id="8534540",
        sleep_request=1.0,
    ):
        self.name = self.__class__.__name__

        self.BASE_URL = urljoin(base_url, "/")
        self.BASE_API_ENDPOINT = "shop/api"
        self.STORE_ID = str(store_id)

        self.SLEEP_REQUEST = float(sleep_request)

    def from_file(self, file_path: str = None) -> dict:
        """return a dict from 'file_path' if it exists or raise an exception"""

        sys.path.insert(0, PROJECT_ROOT)
        try:
            from rewe_dl.rewe_dl.utils import load_config
        except Exception as e:
            # don't spam
            # log.error(f"{e}. Trying other import method!")
            from rewe_dl.utils import load_config

        return load_config(file_path)

    def from_web(self, zipcode: str = "56073") -> dict:
        """load config extracted from web/api
        note that you should leave zipcode as is
        because it is not relevant but must be set
        """
        # TODO # can the returned cloudflare cookies used to bypass everything??

        if not self.STORE_ID:
            return

        base_url = "https://www.rewe.de"
        base_api_endpoint = "api/"
        endpoint = "wksmarketsearch/configuration"

        payload = {
            "selectedService": "PICKUP",
            "customerZipCode": zipcode,  # not relevant but must be set
            "wwIdent": self.STORE_ID,
        }

        url = base_url + "/" + base_api_endpoint + endpoint
        r = httpx.post(url, json=payload)

        config = r.cookies

        if not config.get("wksMarketsCookie"):
            msg = "wksMarketsCookie not in api response!"
        return dict(config)

    def user_data_from_web(self) -> dict:
        """get currect userdata from api"""
        # 'wksMarketsCookie' cookie must be set in config.json
        raise NotImplementedError

        base_url = "https://www.rewe.de"
        base_api_endpoint = ""
        endpoint = "content-homepage-backend/userdata"
        cookies = self.from_web()

        global session
        session.cookies.update(cookies)

        config = STORE().call(
            base_url=base_url,
            base_api_endpoint=base_api_endpoint,
            endpoint=endpoint,
            method="get",
        )

        return config

    def load(self) -> dict:
        """load cookies from_file - else get online info"""

        cookies = {}
        try:
            cookies = self.from_file().get("cookies")
        except InputFileError as e:
            log.error(e)
            cookies = self.from_web()
        except Exception as e:
            log.error(e)
            raise InputFileError("Could not get cookies from_web!")
        return cookies

    @staticmethod
    def get_config_file_cookies() -> dict:
        """Return cookies as a dict from default config file"""
        from utils import load_config, json_compact

        cookies_from_config_file = load_config().get("cookies")

        ret_dict = {}
        for cookie_name, cookie_value in cookies_from_config_file.items():
            if cookie_name == "wksMarketsCookie":
                # this cookie value must be compact json and THEN urlencoded
                unwanted_key = "not_needed"

                markets_cookies = urlencode({unwanted_key: json_compact(cookie_value)})
                cookie_value = markets_cookies.removeprefix(unwanted_key + "=")

            ret_dict[cookie_name] = cookie_value

            # cookies.set(cookie_name, cookie_value, domain='www.rewe.de')
            # cookies.set(cookie_name, cookie_value, domain='rewe.de')

        return ret_dict

    def _ensure_session(self):
        if not globals().get("session"):
            try:
                from utils import create_agents

                log.debug("globals() session is none. Loading...")
                self.cookies = self.load()

                set_session(None, deafult_headers=create_agents(), default_cookies=self.cookies)
            except Exception as e:
                raise e


class STORE(Config):
    def __repr__(self):
        return self.__class__.__name__

    def __init__(self, *args, **kwargs):
        """Pass '*args' and '**kwargs' to Config class
        so that self.STORE_ID, self.SLEEP_REQUEST etc will be set/re-set
        """
        super().__init__(*args, **kwargs)
        self._ensure_session()

    def call(
        self,
        base_url: str = None,
        base_api_endpoint: str = "shop/api/",
        endpoint: str = None,
        params: dict = {},
        method: str = "get",
        **kwargs,
    ) -> dict:
        """any **kwargs will be passed to the http request"""
        if not base_url:
            base_url = self.BASE_URL
        if not base_api_endpoint:
            base_api_endpoint = ""
        base_url = urljoin(base_url, "/")

        sleep(self.SLEEP_REQUEST)

        session = globals().get("session")
        if not session or not method.lower() in dir(session):
            log.error("session not pre set")
            raise AttributeError

        if method.lower() in dir(session):
            session_method = getattr(session, method.lower())

            if not session_method:
                log.error("no session_method")
                return

        url = urljoin(base_url, base_api_endpoint + endpoint + "?")

        response = session_method(url, params=urlencode(params, safe=", !"), **kwargs)

        try:
            return response.json()
        except Exception as e:
            raise e

    @staticmethod
    def paginate(
        url: str,
        params: dict,
        page_key: str = "page",
        max_page: int = 2,
        method: str = "get",
        **kwargs,
    ) -> Iterator[dict]:
        """Simply increase the 'page_key' by one till 'max_page' is reached"""

        if not url.startswith("http"):
            raise ValueError

        if not isinstance(params, dict):
            raise AttributeError

        session = globals().get("session")
        if method.lower() in dir(session):
            session_method = getattr(session, method.lower())
        else:
            raise AttributeError

        sleep(0.3)
        while params.get(page_key) <= max_page:
            r = session_method(url, params=params, **kwargs)
            if r.status_code in (200, 206):
                data = r.json()
                yield data

                total_pages = data.get("pagination", {}).get("totalPages")

                if total_pages == 0 or total_pages == max_page:
                    break

                else:
                    params[page_key] += 1

            else:
                log.error(r.status_code)
                log.info(r.status_code)
                # raise exception.HttpError
                return

    def product_infos(
        self,
        product_ids: list[str] = None,
        listing_ids: list[str] = None,
        article_ids: list[str] = None,
    ) -> list[dict]:
        """returns product information as json for all of
        given '*_ids' in one request'
        At least one of listingIds, productIds or articleIds must be set!

        source of info: 'https://www.rewe.de/shop/api/product-tiles?'
        https://www.rewe.de/shop/api/product-tiles?listingIds=8-P54WB8A8-4e6503bb-5212-3dd3-8a1b-7d0b57d7627f&context=tile&serviceTypes=PICKUP
        https://www.rewe.de/shop/api/product-tiles?productIds=2621809
        """

        base_url = "https://www.rewe.de/"
        base_api_endpoint = "shop/api/"
        endpoint = "product-tiles"

        params = {
            "serviceTypes": "PICKUP",
            "market": self.STORE_ID,  # as seen on -> quickFacets -> constraints
        }

        if product_ids:
            params.update({"productIds": ",".join(product_ids)})
        elif listing_ids:
            params.update({"listingIds": ",".join(listing_ids)})
        elif article_ids:
            params.update({"articleIds": ",".join(article_ids)})
        else:
            raise ValueError("At least one of listingIds, productIds or articleIds must be set!")

        r = self.call(base_url, base_api_endpoint, endpoint, params)

        return r

    @lru_cache
    def search(self, search_term: str, max_page: int = 1) -> Iterator[dict]:
        """search for a term using the API
        returns an Iterator of dicts"""
        assert search_term is not None, "search_term must not be None"

        base_url = "https://www.rewe.de"
        endpoint = "products"

        params = {"search": search_term, "market": self.STORE_ID, "page": 1}

        url = f"{base_url}/shop/api/{endpoint}?"

        return self.paginate(url, params, page_key="page", max_page=max_page)

    def search_category(self, category_slug: str, **kwargs) -> Iterator[dict]:
        assert category_slug is not None, "category_slug must not be None"

        return self.products_by_attribute(param_key="categorySlug", param_value=category_slug, **kwargs)

    def search_brand(self, brand_name: str, **kwargs):
        # with search_brand - when default attribute 'new' is used there are no product results
        return self.products_by_attribute(
            attributes=[""], param_key="brand", param_value=brand_name, **kwargs
        )

    def categories(self, search_result: search) -> list[dict]:
        """return categories and subcategories as a flat list of dicts for given 'search_result'"""

        categories = subcategories = []

        def get_subcategories(category: dict) -> None:
            if "subFacetConstraints" in category:
                for subcategory in category.get("subFacetConstraints"):
                    if "subFacetConstraints" not in subcategory:
                        subcategories.append(subcategory)

                    if "subFacetConstraints" in category:
                        get_subcategories(subcategory)

        for page in search_result:
            constraints = None
            facets = page.get("facets", [])
            for fac in facets:
                if fac.get("name").lower() == "category":
                    constraints = fac.get("facetConstraints", [])
                    break

            for category in constraints:
                if "subFacetConstraints" not in category:
                    categories.append(category)

                if "subFacetConstraints" in category:
                    get_subcategories(category)

        # return unique dicts only, as a list
        # from https://stackoverflow.com/posts/38521207/revisions
        return [dict(s) for s in set(frozenset(md.items()) for md in categories + subcategories)]

    def category_names(self, search_result: search) -> list:
        """return a list of unique category names found in 'search_result'"""
        names = set()
        [names.add(category.get("name")) for category in self.categories(search_result)]

        return list(names)

    def category_slugs(self, search_result: search) -> list:
        """return a list of unique category slugs like:
        ['kochen-backen', 'kaese-eier-molkerei'] found in 'search_result'
        """
        slugs = set()
        for category in self.categories(search_result):
            slugs.add(category.get("slug"))

        return list(slugs)

    def product_ids(self, search_result: search) -> Iterator[str]:
        """yield product ids from 'search_result'"""

        def parse_dict(search_result):
            try:
                for product in search_result.get("offers"):
                    yield str(product.get("id", ""))

            except TypeError:
                products = Parser().get_search_results_products(search_result)

                for product in products:
                    yield str(product.get("id", ""))

        def parse_list(search_result):
            for result in search_result:
                for res in result:
                    yield from parse_dict(res)

        if isinstance(search_result, dict):
            yield from parse_dict(search_result)

        if isinstance(search_result, list):
            yield from parse_list(search_result)

    def product_urls(self, search_result: search | dict) -> Iterator[str]:
        for product_id in self.product_ids(search_result):
            product_url = urljoin("https://rewe.de/", f"produkte/{product_id}")

            yield product_url

    def products_by_attribute(
        self,
        # attributes=["new"],
        attributes: list[str] = [""],
        param_key: str = "",
        param_value: str = "",
        max_page: int = 1,
    ) -> Iterator[dict]:
        """returns an iter of products for 'attribute=something"
        and/or 'param_key="filter"' and param_value="nothing"
        until 'max_page' is reached.

        # front end -> https://www.rewe.de/shop/productList?attribute=lactosefree&attribute=glutenfree
        # https://www.rewe.de/shop/api/products?attribute=new&objectsPerPage=40&page=1&search=*&sorting=RELEVANCE_DESC&serviceTypes=PICKUP&market=1940419&debug=false&autocorrect=true
        """

        base_url = "https://www.rewe.de"
        endpoint = "products"

        params = {
            "objectsPerPage": 250,  # 10, 20, 40, 80, 250
            "page": 1,
            "search": "*",
            "sorting": "RELEVANCE_DESC",
            "serviceTypes": "PICKUP",
            "market": self.STORE_ID,
            "wwIdent": self.STORE_ID,
            "debug": "false",
            "autocorrect": "true",
        }

        if param_key and param_value:
            params[param_key] = param_value

        # combine multiple atrributes like attribute=new&attribute=discounted
        params["attribute"] = "&attribute=".join(attributes)

        url = f"{base_url}/shop/api/{endpoint}"

        return self.paginate(url, params, page_key="page", max_page=max_page)

    def get_discounted_products(self, max_page: int = 2):
        """These 'get_*' funcs are for ease of use"""

        return self.products_by_attribute(attributes=["discounted"], max_page=max_page)

    def get_vegan_products(self, max_page: int = 2):
        return self.products_by_attribute(attributes=["vegan"], max_page=max_page)

    def get_new_products(self, max_page: int = 2):
        return self.products_by_attribute(attributes=["new"], max_page=max_page)

    def get_vegetarian_products(self, max_page: int = 2):
        return self.products_by_attribute(attributes=["vegetarian"], max_page=max_page)

    def get_lactosefree_products(self, max_page: int = 2):
        return self.products_by_attribute(attributes=["lactosefree"], max_page=max_page)

    def get_glutenfree_products(self, max_page: int = 2):
        return self.products_by_attribute(attributes=["glutenfree"], max_page=max_page)

    def get_organic_products(self, max_page: int = 2):
        return self.products_by_attribute(attributes=["organic"], max_page=max_page)

    def get_regional_products(self, max_page: int = 2):
        return self.products_by_attribute(attributes=["regional"], max_page=max_page)

    @lru_cache
    def current_userdata(self) -> dict:
        """Return a dict with current store informations.
        # https://www.rewe.de/content-homepage-backend/userdata
        """

        base_url = "https://www.rewe.de/"
        endpoint = "content-homepage-backend/userdata"

        params = {}

        data = self.call(base_url, endpoint=endpoint, params=params)

        return data

    def recommendations(self, product_ids: list[str]) -> dict:
        """returns a dict containing product listingsIds - to be used in 'product_infos'"""
        """https://www.rewe.de/shop/reco/recommendations?context=product-details-recommendations&productIds=3231481"""
        base_url = "https://www.rewe.de/"
        endpoint = "reco/recommendations"

        params = {
            "context": "product-details-recommendations",
            "productIds": ",".join(product_ids),
        }

        response = self.call(
            base_url=base_url,
            base_api_endpoint="shop/",
            endpoint=endpoint,
            params=params,
        )

        return response.json()

    @lru_cache
    def suggestions(self, search_term: str) -> dict:
        """returns a dict containing product infos like listingsIds - to be used in 'product_infos'"""
        """https://www.rewe.de/shop/api/suggestions?q=TUC"""

        base_url = "https://www.rewe.de"
        endpoint = "/suggestions"

        params = {"q": search_term}

        response = self.call(
            base_url=base_url,
            base_api_endpoint="shop/api/",
            endpoint=endpoint,
            params=params,
        )

        return response

    def get_listings_ids(
        self,
        search_result: search = None,
        suggestions: suggestions = None,
        recommendations: recommendations = None,
    ) -> Iterator[str]:
        """get listingsids for 'search_result' and/or 'suggestions' and/or 'recommendations'

        for listing_id "13-4018077895036-7ac521c9-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                          brand?? - product_id - store_id
        ===============================================================================
        """

        listings_ids = []
        append = listings_ids.append

        if suggestions:
            [append(product.get("listingId", "")) for product in suggestions.get("products", [])]

        if recommendations:
            [append(listing_id) for listing_id in recommendations.get("listingIds", [])]

        if search_result:
            for page in search_result:
                for product in page.get("products", {}):
                    articles = Parser._from_emebedded(product, "articles")
                    for art in articles:
                        listing = Parser._from_emebedded(art, "listing", {})

                        append(listing.get("id", ""))

        return listings_ids

    @staticmethod
    def _yield_from_key(search_result: search, key: str) -> Iterator[list]:
        """for every page in 'search_result' get 'key' and yield it"""
        for page in search_result:
            yield from page.get(key, [])

    def _get_alternatives(self, search_results: search) -> Iterator[list]:
        """get alt products (in the same category?) from search result"""
        yield from self._yield_from_key(search_results, key="alternatives")
        # return list(self._yield_from_key(search_results, key="alternatives"))


class Basket:
    def __repr__(self):
        return self.__class__.__name__

    def __init__(self, *args, **kwargs):
        self.STORE = STORE(*args, **kwargs)

    def add(self, listings_ids: list[str], quantity: int = 1) -> Iterator[httpx.Response] | None:
        """Add something to basket"""
        """https://www.rewe.de/shop/api/baskets/listings/13-4001686301524-4e6503bb-5212-3dd3-8a1b-7d0b57d7627f"""

        base_url = "https://www.rewe.de/shop"
        cookies = Config.load()

        for listing_id in listings_ids:
            sleep(self.STORE.SLEEP_REQUEST)

            endpoint = f"baskets/listings/{listing_id}"

            payload = {
                "context": "product-details-recommendations",
                "includeTimeslot": "false",
                "quantity": quantity,
            }

            url = f"{base_url}/api/{endpoint}"

            response = httpx.post(url, data=payload, cookies=cookies)

            yield response

        return None


class Branch:
    def __repr__(self):
        return self.__class__.__name__

    def __init__(self, *args, **kwargs):
        self.STORE = STORE(*args, **kwargs)

    @lru_cache()
    def in_zipcode(self, zipcode: str) -> dict:
        """Returns a dict of all branches around 'zipcode' that have pickup"""
        """https://www.rewe.de/shop/api/marketselection/zipcodes/56073/services/pickup"""

        base_url = "https://www.rewe.de"
        endpoint = f"/shop/marketselection/zipcodes/{zipcode}/services/pickup"

        r = self.call(base_url, endpoint=endpoint)

        return r

    @staticmethod
    def _has_pickup(branch: dict) -> bool:
        return branch.get("pickupVariant").lower() == "abholservice"

    @lru_cache()
    def first_in_zipcode(self, zipcode: str) -> dict | None:
        """Get first branch that has pickup in 'zipcode'"""
        """https://www.rewe.de/shop/api/marketselection/zipcodes/56073/services/pickup"""

        data = self.in_zipcode(zipcode).json()

        for branch in data:
            if self._has_pickup(branch):
                return branch

        return None

    @staticmethod
    def _get_branch_id_and_zipcode(branch_dict: dict) -> tuple[str, str]:
        branch_id = branch_dict.get("wwIdent", "")
        branch_zipcode = branch_dict.get("zipCode", "")

        return str(branch_id), str(branch_zipcode)


class Cli(Config):
    """Used to read product links from text or json files and process them"""

    def __repr__(self):
        return self.__class__.__name__

    def __init__(self, *args, **kwargs):
        self.STORE = STORE(*args, **kwargs)

    @staticmethod
    @lru_cache()
    def id_from_url(url: str) -> str:
        """Return id from 'url' as str'"""
        path = urlparse(url).path

        if "/produkte/" in path:
            product_id = path.rpartition("/")[2]
            product_id = product_id.removeprefix("p")

            return str(product_id)

        elif "/c/" in path:
            category_slug = path.rpartition("/c/")[2]

            return str(category_slug)

    def from_links(self, urls: Iterator[str]) -> Iterator[Product]:
        """Return an iter of 'Product' asdict for every product in 'urls'"""

        product_ids = [self.id_from_url(url) for url in urls]

        raw_products = self.STORE.product_infos(product_ids=product_ids)

        return list(Parser().parse_product_infos(raw_products))

    def from_links_of_categories(self, urls: Iterator[str], max_page: int = 1) -> Iterator[Product]:
        """Return an iter of 'Product' for every product in category 'urls'"""

        category_slugs = [self.id_from_url(url) for url in urls]

        for category_slug in category_slugs:
            search_result = self.STORE.search_category(category_slug, max_page=max_page)

            product_mds = Parser().parse_search_category(search_result)

            yield from product_mds

    @lru_cache()
    def from_text_file(self, text_file: str) -> None:
        product_urls = set()
        categories = set()

        for line in open(text_file, mode="r"):
            if line.startswith("#"):
                continue

            if not line.startswith("https"):
                continue

            url = line[:120]

            if "/c/" in url:
                categories.add(self.id_from_url(url))

            if ("/p/" or "/produkte/") in url:
                product_urls.add(url)

        if product_urls:
            self.from_links(product_urls)
        if categories:
            self.from_links_of_categories(categories)
