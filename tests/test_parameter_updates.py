import pytest
from services import parameter_service


def test_parameter_batch_save(isolated_reports):
    rows = parameter_service.list_parameters(include_inactive=True)
    rows[0]['unit'] = 'updated unit'
    rows[1]['active'] = False
    parameter_service.update_parameters(rows)
    saved = {r['id']: r for r in parameter_service.list_parameters(include_inactive=True)}
    assert saved[rows[0]['id']]['unit'] == 'updated unit'
    assert saved[rows[1]['id']]['active'] is False


@pytest.mark.parametrize('invalid', ['blank', 'duplicate', 'missing'])
def test_invalid_parameter_batch_does_not_partially_save(isolated_reports, invalid):
    before = parameter_service.list_parameters(include_inactive=True)
    rows = [dict(row) for row in before]
    rows[0]['unit'] = 'must not be saved'
    if invalid == 'blank':
        rows[1]['name'] = ' '
    elif invalid == 'duplicate':
        rows[1]['name'] = rows[0]['name'].upper()
    else:
        rows[1]['id'] = -1
    with pytest.raises(ValueError):
        parameter_service.update_parameters(rows)
    assert parameter_service.list_parameters(include_inactive=True) == before
