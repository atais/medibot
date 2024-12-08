import json

from requests import Session


def initial_filters(session: Session) -> None:
    response = session.get(
        "https://api-gateway-online24.medicover.pl/service-selector-configurator/api/search-appointments/filters?RegionId=204")
    print(json.dumps(json.loads(response.content)))
