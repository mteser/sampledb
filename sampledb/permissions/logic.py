# coding: utf-8
"""

"""

from .. import db
from ..instruments.logic import get_action
from ..object_database import Objects
from .models import Permissions, UserObjectPermissions, PublicObjects


__author__ = 'Florian Rhiem <f.rhiem@fz-juelich.de>'


def object_is_public(object_id):
    return PublicObjects.query.filter_by(object_id=object_id).first() is not None


def set_object_public(object_id, is_public=True):
    if not is_public:
        PublicObjects.query.filter_by(object_id=object_id).delete()
    else:
        db.session.add(PublicObjects(object_id=object_id))
        db.session.commit()


def get_object_permissions(object_id):
    object_permissions = {}
    if object_is_public(object_id):
        object_permissions[None] = Permissions.READ
    else:
        object_permissions[None] = Permissions.NONE
    for user_object_permissions in UserObjectPermissions.query.filter_by(object_id=object_id).all():
        object_permissions[user_object_permissions.user_id] = user_object_permissions.permissions
    for user_id in _get_object_responsible_user_ids(object_id):
        object_permissions[user_id] = Permissions.GRANT
    return object_permissions


def _get_object_responsible_user_ids(object_id):
    object = Objects.get_current_object(object_id, connection=db.engine)
    action = get_action(object.action_id)
    if action is None or action.instrument is None:
        return []
    return [user.id for user in action.instrument.responsible_users]


def get_user_object_permissions(object_id, user_id):
    if user_id is not None:
        # instrument responsible users always have GRANT permissions for an object
        if user_id in _get_object_responsible_user_ids(object_id):
            return Permissions.GRANT
        # other users might have been granted permissions
        user_object_permissions = UserObjectPermissions.query.filter_by(object_id=object_id, user_id=user_id).first()
        if user_object_permissions is not None and user_object_permissions.permissions != Permissions.NONE:
            return user_object_permissions.permissions
    # lastly, the object may be public, so all users have READ permissions
    if object_is_public(object_id):
        return Permissions.READ
    # otherwise the user has no permissions for this object
    return Permissions.NONE


def set_user_object_permissions(object_id, user_id, permissions: Permissions):
    if permissions == Permissions.NONE:
        UserObjectPermissions.query.filter_by(object_id=object_id, user_id=user_id).delete()
    else:
        user_object_permissions = UserObjectPermissions.query.filter_by(object_id=object_id, user_id=user_id).first()
        if user_object_permissions is None:
            user_object_permissions = UserObjectPermissions(user_id=user_id, object_id=object_id, permissions=permissions)
        else:
            user_object_permissions.permissions = permissions
        db.session.add(user_object_permissions)
        db.session.commit()