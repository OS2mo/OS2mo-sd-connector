<!--
SPDX-FileCopyrightText: Magenta ApS

SPDX-License-Identifier: MPL-2.0
-->

# SDConnector

Connector library for SDLon webservices

## Usage
Install into your project using `pip`:
```
pip install os2mo-sd-connector
```

Then import it inside a Python file:
```
import asyncio
from os2mo_sd_connector import SDConnector

async def print_org():
    sd_connector = SDConnector("BZ", "username", "password")
    organization = await sd_connector.getOrganization()
    print(organization)

asyncio.run(print_org())
```
