"""Main client class for the BYMR API SDK."""

import json
import time
import warnings
from typing import Dict, Any, Optional
from urllib.parse import urlencode

import requests
from urllib3.exceptions import InsecureRequestWarning

from .exceptions import (
    BYMRAPIError,
    AuthenticationError,
    ValidationError,
    NetworkError,
    ServerError,
)
from .models import UpdateSavedRequest, SaveBaseRequest, BaseData, UserData


class BYMRClient:
    """
    Client for interacting with the BYMR (Build Your Monster Ranch) API.

    Example:
        ```python
        client = BYMRClient(bearer_token="your_token_here")

        # Update saved status
        response = client.update_saved(version=128, baseid=14926, type="build")

        # Save base data
        base_data = BaseData(version=128, baseid=0, basesaveid=1472264, basename="MyBase")
        response = client.save_base(base_data)
        ```
    """

    DEFAULT_BASE_URL = "https://server.bymrefitted.com"
    DEFAULT_CDN_URL = "https://cdn.bymrefitted.com"
    FLASH_VERSION = "32,0,0,465"
    USER_AGENT = "Adobe Flash Player 32"
    REQUIRED_FIELDS = ["baseid", "basesaveid", "points", "basevalue", "buildingdata", "champion"]

    def __init__(
        self,
        bearer_token: str,
        base_url: str = None,
        cdn_url: str = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        state_file: str = None,
        user_file: str = None,
    ):
        """
        Initialize the BYMR API client.

        Args:
            bearer_token: JWT bearer token for authentication
            base_url: Optional custom base URL (defaults to server.bymrefitted.com)
            cdn_url: Optional custom CDN URL (defaults to cdn.bymrefitted.com)
            timeout: Request timeout in seconds (default: 30)
            verify_ssl: Whether to verify SSL certificates (default: True)
            state_file: Optional path to JSON file for persisting state (default: None)
            auto_sync: If True, sync with server on initialization (default: True)
        """
        self.bearer_token = bearer_token
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.cdn_url = cdn_url or self.DEFAULT_CDN_URL
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.state_file = state_file
        self.user_file = user_file

        # Suppress SSL warnings if SSL verification is disabled
        if not self.verify_ssl:
            warnings.filterwarnings("ignore", category=InsecureRequestWarning)

        self.auto_sync = True

        # State management
        self.base_data: Optional[BaseData] = None
        self._last_response: Optional[Dict[str, Any]] = None

        self.session = requests.Session()
        self._setup_default_headers()

        # Load state from file or server
        self._initialize_state()

    def _setup_default_headers(self) -> None:
        """Setup default headers for all requests."""
        self.session.headers.update(
            {
                "Host": self.base_url.replace("https://", "").replace("http://", ""),
                "x-flash-version": self.FLASH_VERSION,
                "Accept-Language": "en-gb",
                "Accept": "*/*",
                "User-Agent": self.USER_AGENT,
                "Authorization": f"Bearer {self.bearer_token}",
                "Referer": f"{self.cdn_url}/swfs/bymr-stable.swf",
            }
        )

    def _initialize_state(self) -> None:
        """Initialize state from server or local file."""
        if self.state_file:
            self._load_user_from_file()

        if self.user_data and isinstance(self.user_data, UserData):
            try:
                self.sync_with_server()
            except Exception as e:
                raise e

    def _save_to_json_file(self, path, data):
        import os

        dir_path = os.path.dirname(os.path.abspath(path))
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _save_state_to_file(self) -> None:
        """Save current state to JSON file."""
        if not self.state_file or not self.user_file:
            raise ValueError("Unable to save state to file, state_file or user_file is undefined")

        import os

        state = self.base_data.to_dict()
        user = self.user_data.to_dict()

        self._save_to_json_file(self.state_file, state)
        self._save_to_json_file(self.user_file, user)

    def _load_user_from_file(self) -> bool:
        # think about result return types with data, and error
        import os

        if not os.path.exists(self.user_file):
            return False

        try:
            with open(self.user_file, "r") as f:
                user_json = json.load(f)

            self.user_data = UserData.from_dict(user_json)
            return True
        except Exception as e:
            raise e

    def _load_state_from_file(self) -> bool:
        """Load state from JSON file.

        Returns:
            True if state was loaded successfully, False otherwise
        """
        if not self.state_file:
            return False

        import os

        if not os.path.exists(self.state_file):
            return False

        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)

            if state.get("base_data"):
                self.base_data = BaseData.from_dict(state)

            return True
        except Exception as e:
            raise e

    def set_auto_sync(self, bool):
        self.auto_sync = bool

    def sync_with_server(self) -> Dict[str, Any]:
        """Sync current state with server by saving and getting latest response.

        Returns:
            Server response with updated state

        Raises:
            ValueError: If no base_data is loaded
        """
        if not self.auto_sync:
            return

        if self.user_data is None:
            raise ValueError("No user data loaded.")

        server_base_data = self._make_request(
            method="POST",
            endpoint="/base/updatesaved",
            data=self.user_data.to_dict(),
        )

        if self.base_data is None:
            self.base_data = BaseData.from_dict(server_base_data)
        else:
            self.base_data.update_from_dict(server_base_data)

        self.user_data = UserData(
            version=server_base_data.get("version", "0"),
            baseid=server_base_data.get("baseid", "0"),
            lastupdate=server_base_data.get("lastupdate", "0"),
            type=server_base_data.get("type", "build"),
        )

        self._save_state_to_file()

        return server_base_data

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: URL query parameters

        Returns:
            API response as dictionary

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If request validation fails
            NetworkError: If network-related errors occur
            ServerError: If server returns 5xx errors
            BYMRAPIError: For other API errors
        """
        url = f"{self.base_url}{endpoint}"

        try:
            # Prepare data as URL-encoded form data
            encoded_data = None
            if data:
                # Convert nested dicts/lists to JSON strings for form encoding
                form_data = {}
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        form_data[key] = json.dumps(value, separators=(",", ":"))
                    elif value is None:
                        form_data[key] = "null"
                    else:
                        form_data[key] = str(value)
                encoded_data = urlencode(form_data)

            response = self.session.request(
                method=method,
                url=url,
                data=encoded_data,
                params=params,
                timeout=self.timeout,
                verify=self.verify_ssl,
                headers=(
                    {"Content-Type": "application/x-www-form-urlencoded"} if encoded_data else None
                ),
            )

            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed. Check your bearer token.",
                    status_code=response.status_code,
                    response=self._safe_json_parse(response),
                )
            elif response.status_code == 400:
                raise ValidationError(
                    "Request validation failed.",
                    status_code=response.status_code,
                    response=self._safe_json_parse(response),
                )
            elif 500 <= response.status_code < 600:
                raise ServerError(
                    f"Server error: {response.status_code}",
                    status_code=response.status_code,
                    response=self._safe_json_parse(response),
                )
            elif response.status_code != 200:
                raise BYMRAPIError(
                    f"API request failed: {response.status_code}",
                    status_code=response.status_code,
                    response=self._safe_json_parse(response),
                )

            # Parse and return response
            return self._safe_json_parse(response)

        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise BYMRAPIError(f"Request failed: {str(e)}")

    @staticmethod
    def _safe_json_parse(response: requests.Response) -> Dict[str, Any]:
        """
        Safely parse JSON response.

        Args:
            response: requests Response object

        Returns:
            Parsed JSON as dictionary, or empty dict if parsing fails
        """
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError):
            # If response is not JSON, return text in a dict
            return {"raw_response": response.text}

    def mutate_server(self, mutation) -> Dict[str, Any]:
        """
        Save complete base data to the server.

        Args:
            base_data: BaseData object containing all base information
            modify_resources: If True, send current resource values as deltas.
                            If False (default), send zero-delta to preserve server values.

        Returns:
            API response dictionary

        Example:
            ```python
            from bymr_api.models import BaseData, BuildingData, Resources

            base_data = BaseData(
                version=128,
                baseid=0,
                basesaveid=1472264,
                basename="MyAwesomeBase",
                resources=Resources(r1=1000, r2=500),
            )
            response = client.save_base(base_data)
            ```
        """
        base_data_dict = self.base_data.to_dict()

        request_data_dict = {field: base_data_dict[field] for field in self.REQUIRED_FIELDS}

        for field in mutation:
            request_data_dict[field] = mutation[field]

        response = self._make_request(
            method="POST",
            endpoint="/base/save",
            data=request_data_dict,
        )

        self.sync_with_server()

        return response

    def save_base_from_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save base data directly from a dictionary (useful for raw data manipulation).

        Args:
            data: Dictionary containing base data

        Returns:
            API response dictionary

        Example:
            ```python
            data = {
                "version": 128,
                "baseid": 0,
                "basesaveid": 1472264,
                "basename": "MyBase",
                # ... other fields
            }
            response = client.save_base_from_dict(data)
            ```
        """
        return self._make_request(
            method="POST",
            endpoint="/base/save",
            data=data,
        )

    def update_bearer_token(self, new_token: str) -> None:
        """
        Update the bearer token for authentication.

        Args:
            new_token: New JWT bearer token

        Example:
            ```python
            client.update_bearer_token("new_token_here")
            ```
        """
        self.bearer_token = new_token
        self.session.headers.update({"Authorization": f"Bearer {self.bearer_token}"})

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    # State management convenience methods

    def increment_resources(
        self, r1: int = 0, r2: int = 0, r3: int = 0, r4: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Increment resources by the specified amounts.

        Args:
            r1: Amount to add to resource 1
            r2: Amount to add to resource 2
            r3: Amount to add to resource 3
            r4: Amount to add to resource 4
            auto_save: If True, automatically save to server (default: True)

        Returns:
            Server response if auto_save is True, None otherwise

        Raises:
            ValueError: If no base_data is loaded

        Example:
            ```python
            # Increment resources and save
            response = client.increment_resources(r1=1000, r2=500)

            # Just update local state without saving
            client.increment_resources(r1=1000, auto_save=False)
            client.save()  # Save later
            ```
        """
        if self.base_data is None:
            raise ValueError("No base data loaded. Call save_base() first or use set_base_data()")

        resource_mutation = {
            "resources": {
                "r1": r1,
                "r2": r2,
                "r3": r3,
                "r4": r4,
                "r1max": self.base_data.resources.r1max,
                "r2max": self.base_data.resources.r2max,
                "r3max": self.base_data.resources.r3max,
                "r4max": self.base_data.resources.r4max,
            }
        }

        self.mutate_server(resource_mutation)

    def set_resources(
        self,
        r1: Optional[int] = None,
        r2: Optional[int] = None,
        r3: Optional[int] = None,
        r4: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Set resources to specific values.

        Args:
            r1: New value for resource 1 (None to keep current)
            r2: New value for resource 2 (None to keep current)
            r3: New value for resource 3 (None to keep current)
            r4: New value for resource 4 (None to keep current)
            auto_save: If True, automatically save to server (default: True)

        Returns:
            Server response if auto_save is True, None otherwise

        Raises:
            ValueError: If no base_data is loaded

        Example:
            ```python
            # Set specific resources
            response = client.set_resources(r1=5000, r2=5000)
            ```
        """
        if self.base_data is None:
            raise ValueError("No base data loaded. Call save_base() first or use set_base_data()")

        # Calculate deltas (difference between desired and current values)
        delta_r1 = (r1 - self.base_data.resources.r1) if r1 is not None else 0
        delta_r2 = (r2 - self.base_data.resources.r2) if r2 is not None else 0
        delta_r3 = (r3 - self.base_data.resources.r3) if r3 is not None else 0
        delta_r4 = (r4 - self.base_data.resources.r4) if r4 is not None else 0

        resource_mutation = {
            "resources": {
                "r1": delta_r1,
                "r2": delta_r2,
                "r3": delta_r3,
                "r4": delta_r4,
                "r1max": self.base_data.resources.r1max,
                "r2max": self.base_data.resources.r2max,
                "r3max": self.base_data.resources.r3max,
                "r4max": self.base_data.resources.r4max,
            }
        }

        self.mutate_server(resource_mutation)

    def set_champion(self, champion_data):
        self.mutate_server({"champion": champion_data})

    def increment_points(self, amount: int) -> Optional[Dict[str, Any]]:
        """
        Increment points by the specified amount.

        Args:
            amount: Amount to add to points
            auto_save: If True, automatically save to server (default: True)

        Returns:
            Server response if auto_save is True, None otherwise

        Raises:
            ValueError: If no base_data is loaded
        """
        if self.base_data is None:
            raise ValueError("No base data loaded. Call save_base() first or use set_base_data()")

        return self.mutate_server({"points": self.base_data.points + amount})

    def purchase_item(self, item_id: str, quantity: int = 1) -> Optional[Dict[str, Any]]:
        """
        Purchase an item using credits.

        Args:
            item_id: Item identifier (e.g., "MUSHROOM2")
            quantity: Quantity to purchase (default: 1)
            auto_save: If True, automatically save to server (default: True)

        Returns:
            Server response if auto_save is True, None otherwise

        Raises:
            ValueError: If no base_data is loaded

        Example:
            ```python
            # Purchase mushroom upgrade
            response = client.purchase_item("MUSHROOM2", quantity=1)

            # Purchase multiple items
            client.purchase_item("ITEM_ID", quantity=5)
            ```
        """
        if self.base_data is None:
            raise ValueError("No base data loaded. Call save_base() first or use set_base_data()")

        purchase_mutation = {"purchase": [item_id, quantity]}

        self.mutate_server(purchase_mutation)

    def destroy_base(
        self,
        baseid: str,
        attack_data: Optional[Dict[str, Any]] = None,
        attacker_champion: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Attack and destroy a base given its baseid.

        Args:
            baseid: The target base ID to attack
            attack_data: Optional attack data containing monsters and champions.
                        If not provided, uses a default empty attack.
            attacker_champion: Optional list of attacker champion data.

        Returns:
            API response dictionary from the save request

        Example:
            ```python
            # Destroy a base with default attack
            response = client.destroy_base("20444959358270")

            # Destroy with custom attack data
            attack_data = {
                "monsters": [...],
                "champions": [...]
            }
            response = client.destroy_base("20444959358270", attack_data=attack_data)
            ```
        """
        if self.base_data is None:
            raise ValueError("No base data loaded. Call sync_with_server() first.")

        # Default attack data if not provided
        if attack_data is None:
            attack_data = {"monsters": [], "champions": []}

        # Load the target base in attack mode
        load_data = {
            "checkpromotion": 1,
            "type": "attack",
            "baseid": baseid,
            "attackData": attack_data,
            "userid": "",
        }

        target_base = self._make_request(
            method="POST",
            endpoint="/base/load",
            data=load_data,
        )

        # Prepare save data to mark base as destroyed
        current_time = int(time.time())

        save_data = {
            "attackloot": {"r1": 0, "r2": 0, "r3": 0, "r4": 0},
            "mushrooms": target_base.get("mushrooms", {"s": 0, "l": []}),
            "monsterupdate": [],
            "lastupdate": 0,
            "baseseed": target_base.get("baseseed", 0),
            "destroyed": 1,
            "monsters": target_base.get("monsters", {}),
            "buildingdata": target_base.get("buildingdata", {}),
            "flinger": target_base.get("flinger", 0),
            "aiattacks": target_base.get("aiattacks", {}),
            "attackid": target_base.get("attackid", 0),
            "catapult": target_base.get("catapult", 0),
            "version": target_base.get("version", 128),
            "resources": {
                "r1": 0,
                "r2": 0,
                "r3": 0,
                "r4": 0,
                "r1max": 0,
                "r2max": 0,
                "r3max": 0,
                "r4max": 0,
            },
            "tutorialstage": target_base.get("tutorialstage", 205),
            "baseid": baseid,
            "timeplayed": 3,
            "basevalue": target_base.get("basevalue", 0),
            "over": 1,
            "buildinghealthdata": target_base.get("buildinghealthdata", {}),
            "buildingresources": target_base.get("buildingresources", {}),
            "researchdata": target_base.get("researchdata", {}),
            "basesaveid": target_base.get("basesaveid", 0),
            "damage": 100,
            "basename": target_base.get("basename", ""),
            "stats": target_base.get("stats", {}),
            "inventory": target_base.get("inventory", {}),
            "frontpage": target_base.get("frontpage", {}),
            "attackreport": "",
            "lockerdata": target_base.get("lockerdata", {}),
            "protect": 0,
            "quests": target_base.get("quests", {}),
            "lootreport": {
                "isInferno": False,
                "r1": 0,
                "r2": 0,
                "r3": 0,
                "r4": 0,
                "name": target_base.get("name", ""),
            },
            "monsterbaiter": target_base.get("monsterbaiter", {}),
            "empirevalue": target_base.get("empirevalue", 0),
            "achieved": [],
            "clienttime": current_time,
            "points": target_base.get("points", 0),
            "siege": None,
            "attackersiege": None,
            "academy": target_base.get("academy", {}),
            "attackerchampion": attacker_champion or [],
            "effects": [],
        }

        # Send the save request to destroy the base
        response = self._make_request(
            method="POST",
            endpoint="/base/save",
            data=save_data,
        )

        return response

    def takeover_cell(
        self,
        baseid: str,
        resources: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """
        Take over a world map cell after destroying it.

        Args:
            baseid: The base ID of the cell to take over
            resources: Optional dict with r1, r2, r3, r4 resource costs.
                      Defaults to 5,500,000 each.

        Returns:
            API response dictionary

        Example:
            ```python
            # Take over with default resources
            response = client.takeover_cell("20444959360271")

            # Take over with custom resources
            response = client.takeover_cell("20444959360271", resources={"r1": 1000000, "r2": 1000000, "r3": 1000000, "r4": 1000000})
            ```
        """
        if resources is None:
            resources = {"r1": 0, "r2": 0, "r3": 0, "r4": 0}

        takeover_data = {
            "baseid": baseid,
            "resources": resources,
        }

        response = self._make_request(
            method="POST",
            endpoint="/worldmapv2/takeovercell",
            data=takeover_data,
        )

        return response

    def load_base(
        self,
        baseid: str,
        load_type: str = "build",
    ) -> Dict[str, Any]:
        """
        Load a base in the specified mode.

        Args:
            baseid: The base ID to load
            load_type: The load type - "build" or "attack" (default: "build")

        Returns:
            API response dictionary with base data

        Example:
            ```python
            # Load base in build mode
            base_data = client.load_base("20444959360271")

            # Load base in attack mode
            base_data = client.load_base("20444959360271", load_type="attack")
            ```
        """
        load_data = {
            "checkpromotion": 1,
            "type": load_type,
            "baseid": baseid,
            "userid": "",
        }

        response = self._make_request(
            method="POST",
            endpoint="/base/load",
            data=load_data,
        )

        return response

    def save_outpost(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save an outpost base with the provided data.

        Args:
            base_data: Dictionary containing the base data from load_base

        Returns:
            API response dictionary
        """
        current_time = int(time.time())

        save_data = {
            "mushrooms": base_data.get("mushrooms", {"s": 0, "l": []}),
            "monsterupdate": [],
            "baseseed": base_data.get("baseseed", 0),
            "buildinghealthdata": base_data.get("buildinghealthdata", {}),
            "monsters": base_data.get("monsters", {}),
            "buildingdata": base_data.get("buildingdata", {}),
            "flinger": base_data.get("flinger", 0),
            "aiattacks": base_data.get("aiattacks", {}),
            "clienttime": current_time,
            "catapult": base_data.get("catapult", 0),
            "version": base_data.get("version", 128),
            "resources": base_data.get("resources", {}),
            "tutorialstage": base_data.get("tutorialstage", 205),
            "baseid": base_data.get("baseid"),
            "timeplayed": base_data.get("timeplayed", 0) + 1,
            "basevalue": base_data.get("basevalue", 0),
            "buildingresources": base_data.get("buildingresources", {}),
            "rewards": base_data.get("rewards", {}),
            "researchdata": base_data.get("researchdata", {}),
            "basesaveid": base_data.get("basesaveid", 0),
            "damage": base_data.get("damage", 0),
            "basename": base_data.get("basename", "basename"),
            "stats": base_data.get("stats", {}),
            "inventory": base_data.get("inventory", {}),
            "frontpage": base_data.get("frontpage", {}),
            "lockerdata": base_data.get("lockerdata", {}),
            "events": base_data.get("events", {}),
            "quests": base_data.get("quests", {}),
            "monsterbaiter": base_data.get("monsterbaiter", {}),
            "empirevalue": base_data.get("empirevalue", 0),
            "achieved": base_data.get("achieved", []),
            "academy": base_data.get("academy", {}),
            "points": base_data.get("points", 0),
            "siege": None,
            "attackersiege": None,
            "lastupdate": base_data.get("lastupdate", 0),
            "effects": [],
        }

        response = self._make_request(
            method="POST",
            endpoint="/base/save",
            data=save_data,
        )

        return response

    def destroy_and_takeover(
        self,
        baseid: str,
        attack_data: Optional[Dict[str, Any]] = None,
        attacker_champion: Optional[list] = None,
        takeover_resources: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """
        Destroy a base and take it over.

        Note: Starter kit cannot be purchased on freshly taken over empty bases.
        Use buy_starter_kit() on bases that already have buildings.

        Args:
            baseid: The target base ID to attack and take over
            attack_data: Optional attack data containing monsters and champions
            attacker_champion: Optional list of attacker champion data
            takeover_resources: Optional dict with r1, r2, r3, r4 resource costs

        Returns:
            Final API response dictionary

        Example:
            ```python
            # Destroy and takeover a base
            response = client.destroy_and_takeover("20444959360271")
            ```
        """
        # Step 1: Destroy the base
        self.destroy_base(baseid, attack_data, attacker_champion)

        # Step 2: Take over the cell
        self.takeover_cell(baseid, takeover_resources)

        # Step 3: Load the base in build mode
        outpost_data = self.load_base(baseid, load_type="build")

        # Step 4: Save the outpost to finalize takeover
        response = self.save_outpost(outpost_data)

        return response

    def buy_starter_kit(self, baseid: str) -> Dict[str, Any]:
        """
        Purchase starter kit for an outpost that already has buildings.

        Note: This only works on bases that have buildingdata (not empty bases).
        The starter kit provides resources to build/upgrade, it doesn't create buildings.

        Args:
            baseid: The base ID to purchase starter kit for

        Returns:
            API response dictionary

        Example:
            ```python
            # Buy starter kit for an existing outpost
            response = client.buy_starter_kit("20444959360271")
            ```
        """
        # Load the base
        base_data = self.load_base(baseid, load_type="build")

        # Check if base has buildings
        if not base_data.get("buildingdata") or len(base_data.get("buildingdata", {})) <= 1:
            print(f"Warning: Base {baseid} has no buildings. Starter kit may not work.")

        # Set starter kit flag
        if "stats" not in base_data:
            base_data["stats"] = {}
        if "achievements" not in base_data["stats"]:
            base_data["stats"]["achievements"] = {"s": {}, "c": {}}
        elif "s" not in base_data["stats"]["achievements"]:
            base_data["stats"]["achievements"]["s"] = {}

        base_data["stats"]["achievements"]["s"]["starterkit"] = 1

        # Save with starter kit flag
        response = self.save_outpost(base_data)

        return response

    def get_area(
        self,
        x: int,
        y: int,
        width: int = 10,
        height: int = 10,
        send_resources: int = 0,
    ) -> Dict[str, Any]:
        """
        Get world map area data for the specified coordinates.

        Args:
            x: X coordinate on the world map
            y: Y coordinate on the world map
            width: Width of the area to fetch (default: 10)
            height: Height of the area to fetch (default: 10)
            send_resources: Whether to include resource data (default: 0)

        Returns:
            API response dictionary containing map cell data

        Example:
            ```python
            # Get area around coordinates (360, 270)
            area_data = client.get_area(x=360, y=270)
            ```
        """
        area_data = {
            "width": width,
            "x": x,
            "sendresources": send_resources,
            "y": y,
            "height": height,
        }

        response = self._make_request(
            method="POST",
            endpoint="/worldmapv2/getarea",
            data=area_data,
        )

        return response

    def get_enemy_bases_from_area(
        self,
        area_response: Dict[str, Any],
        current_username: str,
        include_wild_monsters: bool = False,
    ) -> list:
        """
        Extract enemy base IDs from area response data.

        Args:
            area_response: Response from get_area()
            current_username: The current user's username to exclude from targets
            include_wild_monsters: If True, include wild monster bases (b=1) in the results (default: False)

        Returns:
            List of dictionaries containing enemy base info (bid, name, uid, coords)
        """
        enemy_bases = []
        data = area_response.get("data", {})

        for x_coord, y_data in data.items():
            for y_coord, cell_data in y_data.items():
                # Skip if no base ID
                if "bid" not in cell_data:
                    continue

                # Get cell type (b=1: wild monster, b=3: player base)
                cell_type = cell_data.get("b", 0)

                # Skip if it's not a valid target
                if include_wild_monsters:
                    # Include both wild monsters (b=1) and player bases (b=3)
                    if cell_type not in [1, 3]:
                        continue
                else:
                    # Only include player bases (b=3)
                    if cell_type != 3:
                        continue

                # Skip if it's the current user's base (only applies to player bases)
                cell_name = cell_data.get("n", "")
                if cell_type == 3 and cell_name.lower() == current_username.lower():
                    continue

                # Skip if already destroyed (d=1)
                if cell_data.get("d", 0) == 1:
                    continue

                enemy_bases.append(
                    {
                        "bid": cell_data["bid"],
                        "name": cell_name,
                        "uid": cell_data.get("uid", 0),
                        "x": x_coord,
                        "y": y_coord,
                        "level": cell_data.get("l", 0),
                        "damage": cell_data.get("dm", 0),
                    }
                )

        return enemy_bases

    def destroy_all_enemy_bases(
        self,
        x: int,
        y: int,
        current_username: str,
        width: int = 10,
        height: int = 10,
        attack_data: Optional[Dict[str, Any]] = None,
        attacker_champion: Optional[list] = None,
        takeover_resources: Optional[Dict[str, int]] = None,
        delay_between_attacks: float = 1.0,
        include_wild_monsters: bool = False,
    ) -> Dict[str, Any]:
        """
        Get area data, find all enemy bases, and destroy/takeover each one.

        Args:
            x: X coordinate on the world map
            y: Y coordinate on the world map
            current_username: Your username to exclude your own bases
            width: Width of the area to scan (default: 10)
            height: Height of the area to scan (default: 10)
            attack_data: Optional attack data for destroy_base
            attacker_champion: Optional champion data for destroy_base
            takeover_resources: Optional resources for takeover
            delay_between_attacks: Seconds to wait between each attack (default: 1.0)
            include_wild_monsters: If True, also destroy and takeover wild monster bases (default: False)

        Returns:
            Dictionary with results summary and details

        Example:
            ```python
            # Destroy all enemy bases in area around (360, 270)
            result = client.destroy_all_enemy_bases(
                x=360,
                y=270,
                current_username="josesteve",
            )
            print(f"Destroyed {result['destroyed_count']} bases")

            # Include wild monster bases too
            result = client.destroy_all_enemy_bases(
                x=360,
                y=270,
                current_username="josesteve",
                include_wild_monsters=True,
            )
            ```
        """
        # Step 1: Get the area data
        area_response = self.get_area(x=x, y=y, width=width, height=height)

        if area_response.get("error", 1) != 0:
            return {
                "success": False,
                "error": "Failed to fetch area data",
                "area_response": area_response,
            }

        # Step 2: Extract enemy bases
        enemy_bases = self.get_enemy_bases_from_area(
            area_response, current_username, include_wild_monsters
        )

        if not enemy_bases:
            return {
                "success": True,
                "destroyed_count": 0,
                "message": "No enemy bases found in the specified area",
                "enemy_bases": [],
            }

        # Step 3: Destroy and takeover each enemy base
        results = []
        destroyed_count = 0

        for base in enemy_bases:
            try:
                print(
                    f"Attacking base {base['bid']} owned by {base['name']} at ({base['x']}, {base['y']})..."
                )

                response = self.destroy_and_takeover(
                    baseid=base["bid"],
                    attack_data=attack_data,
                    attacker_champion=attacker_champion,
                    takeover_resources=takeover_resources,
                )

                results.append(
                    {
                        "base": base,
                        "success": True,
                        "response": response,
                    }
                )
                destroyed_count += 1
                print(f"  ✓ Successfully destroyed and took over base {base['bid']}")

                # Delay between attacks to avoid rate limiting
                if delay_between_attacks > 0:
                    time.sleep(delay_between_attacks)

            except Exception as e:
                results.append(
                    {
                        "base": base,
                        "success": False,
                        "error": str(e),
                    }
                )
                print(f"  ✗ Failed to destroy base {base['bid']}: {e}")

        return {
            "success": True,
            "destroyed_count": destroyed_count,
            "total_enemy_bases": len(enemy_bases),
            "results": results,
            "enemy_bases": enemy_bases,
        }

    def conquer_entire_map(
        self,
        main_base_coords: list,
        current_username: str,
        attack_range: int = 10,
        max_iterations: int = 100,
        attack_data: Optional[Dict[str, Any]] = None,
        attacker_champion: Optional[list] = None,
        takeover_resources: Optional[Dict[str, int]] = None,
        delay_between_attacks: float = 1.0,
        delay_between_iterations: float = 2.0,
        include_wild_monsters: bool = False,
    ) -> Dict[str, Any]:
        """
        Iteratively conquer all bases within range, expanding from your owned bases.

        This method starts from your main base(s) and conquered outposts, then:
        1. Scans the area around all owned bases
        2. Attacks all enemy bases within range
        3. Adds newly conquered bases to owned list
        4. Repeats until no more bases are within range

        Args:
            main_base_coords: List of (x, y) tuples for your starting bases [(360, 270), ...]
            current_username: Your username to exclude your own bases
            attack_range: How far from owned bases to scan for enemies (default: 10)
            max_iterations: Maximum expansion iterations to prevent infinite loops (default: 100)
            attack_data: Optional attack data for destroy_base
            attacker_champion: Optional champion data for destroy_base
            takeover_resources: Optional resources for takeover
            delay_between_attacks: Seconds to wait between each attack (default: 1.0)
            delay_between_iterations: Seconds to wait between expansion iterations (default: 2.0)
            include_wild_monsters: If True, also destroy wild monster bases (default: False)

        Returns:
            Dictionary with conquest results and statistics

        Example:
            ```python
            # Start conquest from main base at (360, 270)
            result = client.conquer_entire_map(
                main_base_coords=[(360, 270)],
                current_username="josesteve",
                attack_range=10,
            )
            print(f"Total bases conquered: {result['total_conquered']}")
            ```
        """
        print(f"\n🗺️  Starting conquest from {len(main_base_coords)} base(s)")
        print(f"   Attack range: {attack_range}")
        print(f"   Include wild monsters: {include_wild_monsters}\n")

        # Track all owned bases (starts with main bases)
        owned_bases = set()
        for x, y in main_base_coords:
            owned_bases.add((x, y))

        total_conquered = 0
        iteration = 0
        all_iteration_results = []

        while iteration < max_iterations:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"🔄 Iteration {iteration}: Scanning from {len(owned_bases)} owned bases")
            print(f"{'='*60}\n")

            # Collect all unique enemy bases within range of ANY owned base
            targets_dict = {}  # Use dict to deduplicate by baseid
            wild_monsters_dict = {}  # Track wild monsters separately

            for base_x, base_y in owned_bases:
                print(f"📍 Scanning area around owned base ({base_x},{base_y})...")

                try:
                    area_response = self.get_area(
                        x=base_x,
                        y=base_y,
                        width=attack_range,
                        height=attack_range,
                    )

                    if area_response.get("error", 1) != 0:
                        print(f"   ✗ Failed to fetch area data")
                        continue

                    # Get player bases
                    enemy_bases = self.get_enemy_bases_from_area(
                        area_response,
                        current_username,
                        include_wild_monsters,
                    )

                    # Add to targets dict (deduplicates by baseid)
                    for base in enemy_bases:
                        targets_dict[base["bid"]] = base

                    # Also scan for wild monsters (always, for fallback)
                    wild_bases = self.get_enemy_bases_from_area(
                        area_response,
                        current_username,
                        include_wild_monsters=True,
                    )

                    # Filter to only wild monsters (not player bases)
                    for base in wild_bases:
                        if base not in enemy_bases:  # It's a wild monster
                            wild_monsters_dict[base["bid"]] = base

                    if enemy_bases:
                        print(f"   ✓ Found {len(enemy_bases)} enemy base(s) in range")

                except Exception as e:
                    print(f"   ✗ Error scanning area: {e}")

            # Convert dict to list
            targets = list(targets_dict.values())
            wild_monsters = list(wild_monsters_dict.values())

            # If no player bases found but wild monsters exist, attack 1 wild monster to expand
            if not targets and wild_monsters:
                print(
                    f"\n⚠️  No player bases in range, but found {len(wild_monsters)} wild monster(s)"
                )
                print(f"   Attacking 1 wild monster base to continue expansion...\n")
                targets = [wild_monsters[0]]  # Just take the first one
            elif not targets:
                print(f"\n✅ No more enemy bases within range!")
                print(f"   Conquest complete after {iteration} iteration(s)")
                break

            print(f"\n🎯 Found {len(targets)} unique target(s) to attack this iteration\n")

            # Attack all targets
            iteration_conquered = 0
            iteration_failed = 0
            newly_conquered = []

            for i, base in enumerate(targets, 1):
                try:
                    print(
                        f"[{i}/{len(targets)}] Attacking {base['bid']} ({base['name']}) at ({base['x']},{base['y']})..."
                    )

                    response = self.destroy_and_takeover(
                        baseid=base["bid"],
                        attack_data=attack_data,
                        attacker_champion=attacker_champion,
                        takeover_resources=takeover_resources,
                    )

                    # Add to owned bases
                    new_coords = (int(base["x"]), int(base["y"]))
                    owned_bases.add(new_coords)
                    newly_conquered.append(base)
                    iteration_conquered += 1
                    total_conquered += 1

                    print(f"          ✓ Successfully conquered! Now own {len(owned_bases)} bases")

                    if delay_between_attacks > 0:
                        time.sleep(delay_between_attacks)

                except Exception as e:
                    iteration_failed += 1
                    print(f"          ✗ Failed: {e}")

            all_iteration_results.append(
                {
                    "iteration": iteration,
                    "targets_found": len(targets),
                    "conquered": iteration_conquered,
                    "failed": iteration_failed,
                    "newly_conquered": newly_conquered,
                }
            )

            print(f"\n📊 Iteration {iteration} Summary:")
            print(f"   Conquered: {iteration_conquered}/{len(targets)}")
            print(f"   Total owned bases: {len(owned_bases)}")
            print(f"   Total conquered: {total_conquered}")

            # Delay before next iteration
            if delay_between_iterations > 0 and iteration < max_iterations:
                time.sleep(delay_between_iterations)

        print(f"\n{'='*60}")
        print(f"🏆 CONQUEST COMPLETE!")
        print(f"   Total iterations: {iteration}")
        print(f"   Total bases conquered: {total_conquered}")
        print(f"   Total owned bases: {len(owned_bases)}")
        print(f"{'='*60}\n")

        return {
            "success": True,
            "total_conquered": total_conquered,
            "total_owned_bases": len(owned_bases),
            "iterations": iteration,
            "owned_bases": list(owned_bases),
            "iteration_results": all_iteration_results,
        }
