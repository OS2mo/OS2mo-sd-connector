from uuid import UUID
from typing import Optional

import click
from sd_connector import AsyncSDConnector
from sd_connector import SDConnector
from ra_utils.async_to_sync import async_to_sync


@click.command()
@click.option(
    "--institution-identifier",
    help="Identifier for the SD institution",
)
@click.option(
    "--institution-uuid-identifier",
    type=click.UUID,
    help="UUID identifier for the SD institution",
)
@click.option(
    "--username",
    required=True,
    help="SD username",
)
@click.option(
    "--password",
    required=True,
    help="SD password",
    prompt=True,
    hide_input=True,
)
@async_to_sync
async def main(
    institution_identifier: Optional[str],
    institution_uuid_identifier: Optional[UUID],
    username: str,
    password: str,
):
    if institution_identifier is None and institution_uuid_identifier is None:
        raise click.ClickException("One of --institution-identifier or --institution-uuid-identifier must be set")
    if institution_identifier is not None and institution_uuid_identifier is not None:
        raise click.ClickException("Only one of --institution-identifier or --institution-uuid-identifier must be set")

    sd_connector = SDConnector(username, password)
    #print(sd_connector.getDepartment(institution_identifier))
    #print(sd_connector.getDepartmentParent("9848725d-2798-4600-9200-000006180002"))
    #print(sd_connector.getInstitution(None, institution_identifier))
    #print(sd_connector.getOrganization(institution_identifier))
    #print(sd_connector.getEmployment(institution_identifier))
    #print(sd_connector.getEmploymentChanged(institution_identifier))
    #print(sd_connector.getEmploymentChangedAtDate(institution_identifier))
    #print(sd_connector.getPerson(institution_identifier))
    print(sd_connector.getPersonChangedAtDate(institution_identifier))
    #print(sd_connector.getProfession(institution_identifier))


if __name__ == "__main__":
    main()
