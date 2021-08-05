<!--
SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->

# SDConnector

Connector library for SDLon webservices

## Requirements

Python 3.8+

Dependencies:

* <a href="https://more-itertools.readthedocs.io/" class="external-link" target="_blank">More Itertools</a>

## Installation

```console
$ pip install os2mo-sd-connector
```

## Usage
```Python
import asyncio
from os2mo_sd_connector import SDConnector

async def print_org():
    sd_connector = SDConnector("BZ", "username", "password")
    organization = await sd_connector.getOrganization()
    print(organization)

asyncio.run(print_org())
```

## License

This project is licensed under the terms of the MPL-2.0 license.
