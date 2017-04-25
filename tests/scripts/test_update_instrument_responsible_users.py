# coding: utf-8
"""

"""

import pytest
from sampledb import db
from sampledb.logic import instruments
from sampledb.models.users import User, UserType
import sampledb.__main__ as scripts
from ..test_utils import app_context


@pytest.fixture
def instrument():
    return instruments.create_instrument('Example Instrument', 'Example Instrument Description')


@pytest.fixture
def users():
    users = [
        User(name, 'example@fz-juelich.de', UserType.PERSON)
        for name in ['User 1', 'User 2', 'User 3']
    ]
    for user in users:
        db.session.add(user)
    db.session.commit()
    return users


def test_update_instrument_responsible_users(instrument, users):
    instrument = instruments.get_instruments()[0]
    assert len(instrument.responsible_users) == 0
    instruments.add_instrument_responsible_user(instrument.id, users[0].id)
    instruments.add_instrument_responsible_user(instrument.id, users[1].id)
    assert len(instrument.responsible_users) == 2
    assert instrument.responsible_users == [users[0], users[1]] or instrument.responsible_users == [users[1], users[0]]

    scripts.main([scripts.__file__, 'update_instrument_responsible_users', str(instrument.id), str(users[0].id), str(users[2].id)])

    instrument = instruments.get_instruments()[0]
    assert len(instrument.responsible_users) == 2
    assert instrument.responsible_users == [users[0], users[2]] or instrument.responsible_users == [users[2], users[0]]

    scripts.main([scripts.__file__, 'update_instrument_responsible_users', str(instrument.id)])

    instrument = instruments.get_instruments()[0]
    assert len(instrument.responsible_users) == 0


def test_update_instrument_responsible_users_missing_user(instrument):
    instrument = instruments.get_instruments()[0]
    assert len(instrument.responsible_users) == 0

    with pytest.raises(SystemExit) as exc_info:
        scripts.main([scripts.__file__, 'update_instrument_responsible_users', str(instrument.id), '42'])
    assert exc_info.value != 0

    instrument = instruments.get_instruments()[0]
    assert len(instrument.responsible_users) == 0


def test_update_instrument_responsible_users_invalid_user(instrument):
    instrument = instruments.get_instruments()[0]
    assert len(instrument.responsible_users) == 0

    with pytest.raises(SystemExit) as exc_info:
        scripts.main([scripts.__file__, 'update_instrument_responsible_users', str(instrument.id), 'User 1'])
    assert exc_info.value != 0

    instrument = instruments.get_instruments()[0]
    assert len(instrument.responsible_users) == 0


def test_update_instrument_responsible_users_missing_instrument(users):
    with pytest.raises(SystemExit) as exc_info:
        scripts.main([scripts.__file__, 'update_instrument_responsible_users', '1', str(users[0].id)])
    assert exc_info.value != 0


def test_update_instrument_responsible_users_invalid_instrument(instrument, users):
    instrument = instruments.get_instruments()[0]
    assert len(instrument.responsible_users) == 0

    with pytest.raises(SystemExit) as exc_info:
        scripts.main([scripts.__file__, 'update_instrument_responsible_users', 'Example Instrument', str(users[0].id)])
    assert exc_info.value != 0

    instrument = instruments.get_instruments()[0]
    assert len(instrument.responsible_users) == 0


def test_update_instrument_responsible_users_missing_arguments(instrument, users):
    instrument = instruments.get_instruments()[0]
    assert len(instrument.responsible_users) == 0

    with pytest.raises(SystemExit) as exc_info:
        scripts.main([scripts.__file__, 'update_instrument_responsible_users'])
    assert exc_info.value != 0

    instrument = instruments.get_instruments()[0]
    assert len(instrument.responsible_users) == 0