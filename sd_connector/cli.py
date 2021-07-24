import click
from ra_utils.async_to_sync import async_to_sync

from sd_connector import AsyncSDConnector
from sd_connector import SDConnector


@click.command()
@click.option(
    "--institution-identifier",
    help="Identifier for the SD institution",
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
    institution_identifier: str,
    username: str,
    password: str,
) -> None:
    sd_connector = SDConnector(username, password)
    print(sd_connector.getDepartment(institution_identifier))
    print(sd_connector.getDepartmentParent("9848725d-2798-4600-9200-000006180002"))
    print(sd_connector.getInstitution(None, institution_identifier))
    print(sd_connector.getOrganization(institution_identifier))
    print(sd_connector.getEmployment(institution_identifier))
    print(sd_connector.getEmploymentChanged(institution_identifier))
    print(sd_connector.getEmploymentChangedAtDate(institution_identifier))
    print(sd_connector.getPerson(institution_identifier))
    print(sd_connector.getPersonChangedAtDate(institution_identifier))
    print(sd_connector.getProfession(institution_identifier))

    sd_aconnector = AsyncSDConnector(username, password)
    print(await sd_aconnector.getDepartment(institution_identifier))
    print(
        await sd_aconnector.getDepartmentParent("9848725d-2798-4600-9200-000006180002")
    )
    print(await sd_aconnector.getInstitution(None, institution_identifier))
    print(await sd_aconnector.getOrganization(institution_identifier))
    print(await sd_aconnector.getEmployment(institution_identifier))
    print(await sd_aconnector.getEmploymentChanged(institution_identifier))
    print(await sd_aconnector.getEmploymentChangedAtDate(institution_identifier))
    print(await sd_aconnector.getPerson(institution_identifier))
    print(await sd_aconnector.getPersonChangedAtDate(institution_identifier))
    print(await sd_aconnector.getProfession(institution_identifier))
    await sd_aconnector.aclose()


if __name__ == "__main__":
    main()
