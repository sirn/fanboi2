from collections import OrderedDict
from sqlalchemy import event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import attributes, object_mapper, mapper
from sqlalchemy.orm.exc import UnmappedColumnError
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column, Table, ForeignKeyConstraint
from sqlalchemy.sql.sqltypes import Integer, String, DateTime


_versioned_mappers = []


def _is_fk_column(column, table):
    """Returns :type:`True` if column is referencing :attr:`table`.

    :param column: SQLAlchemy column.
    :param table: SQLAlchemy table.

    :type column: sqlalchemy.sql.schema.Column
    :type table: sqlalchemy.sql.schema.Table
    :rtype: bool
    """
    for fk in column.foreign_keys:
        if fk.references(table):
            return True
    return False


def _is_versioning_column(column):
    """Returns :type:`True` if column belongs to versioning table.

    :param column: SQLAlchemy column to check.

    :type column: sqlalchemy.sql.schema.Column
    :rtype: bool
    """
    return "version_meta" in column.info


def _copy_history_column(column):
    """Create a history copy of a SQLAlchemy column. The copied column will
    share the same SQL data type with the original column, but without defaults
    and its unique constraint removed.

    :param column: SQLAlchemy column to copy.

    :type column: sqlalchemy.sql.schema.Column
    :rtype: sqlalchemy.sql.schema.Column
    """
    new_column = column.copy()
    new_column.unique = False
    new_column.default = new_column.server_default = None
    if new_column.primary_key:
        new_column.autoincrement = False
    column.info['history_copy'] = new_column
    return new_column


def _history_mapper(model_mapper):
    """Configure SQLAlchemy mapper and enable history support.

    :param model_mapper: SQLAlchemy mapper object for a model.

    :type model_mapper: sqlalchemy.orm.mapper.Mapper
    :rtype: sqlalchemy.orm.mapper.Mapper
    """
    model_class = model_mapper.class_
    model_table = model_mapper.local_table

    for prop in model_mapper.iterate_properties:
        getattr(model_class, prop.key).impl.active_history = True

    super_mapper = model_mapper.inherits
    super_history_mapper = getattr(model_class, '__history_mapper__', None)
    super_fks = []

    properties = OrderedDict()
    polymorphic_on = None

    if not super_mapper or model_table is not super_mapper.local_table:
        version_meta = {"version_meta": True}
        new_columns = []

        for column in model_table.c:
            if _is_versioning_column(column):
                continue

            try:
                original_prop = model_mapper.get_property_by_column(column)
            except UnmappedColumnError:
                continue

            new_column = _copy_history_column(column)
            new_columns.append(new_column)

            if super_mapper and \
               _is_fk_column(column, super_mapper.local_table):
                super_fks.append(
                    (new_column.key,
                     list(super_history_mapper.local_table.primary_key)[0]))

            if column is model_mapper.polymorphic_on:
                polymorphic_on = new_column

            if len(original_prop.columns) > 1 or \
               original_prop.columns[0].key != original_prop.key:
                properties[original_prop.key] = tuple(
                    c.info['history_copy'] for c in original_prop.columns)

        if super_mapper:
            super_fks.append((
                'version',
                super_history_mapper.local_table.c.version))

        new_columns.append(
            Column('version',
                   Integer,
                   primary_key=True,
                   autoincrement=False,
                   nullable=False,
                   info=version_meta))

        new_columns.append(
            Column('change_type',
                   String,
                   nullable=False,
                   info=version_meta))

        new_columns.append(
            Column('changed_at',
                   DateTime(timezone=True),
                   default=func.now(),
                   nullable=False,
                   info=version_meta))

        if super_fks:
            new_columns.append(ForeignKeyConstraint(*zip(*super_fks)))

        new_table = Table(
            model_table.name + '_history',
            model_table.metadata,
            *new_columns,
            schema=model_table.schema)
    else:
        for column in model_mapper.c:
            if column.key not in super_history_mapper.local_table.c:
                new_column = _copy_history_column(column)
                super_history_mapper.local_table.append_column(new_column)
        new_table = None

    if super_history_mapper:
        bases = (super_history_mapper.class_,)
        if new_table is not None:
            properties['change_type'] = (
                (new_table.c.change_type,) + tuple(
                    super_history_mapper.attrs.change_type.columns))
            properties['changed_at'] = (
                (new_table.c.changed_at,) + tuple(
                    super_history_mapper.attrs.changed_at.columns))
    else:
        bases = model_mapper.base_mapper.class_.__bases__

    model_class.__history_mapper__ = mapper(
        type.__new__(type, "%sHistory" % (model_class.__name__), bases, {}),
        new_table,
        inherits=super_history_mapper,
        polymorphic_on=polymorphic_on,
        polymorphic_identity=model_mapper.polymorphic_identity,
        properties=properties)

    if not super_history_mapper:
        model_table.append_column(
            Column('version',
                   Integer,
                   default=1,
                   nullable=False))
        model_mapper.add_property('version', model_table.c.version)


def make_versioned(session, retrieve=None):
    """Enable the versioned mapper. If ``retrieve`` is given, the function
    will be used for retrieving a list of mapper objects (see also
    :func:`make_versioned_class`).

    :param session: SQLAlchemy session object.
    :param retrieve: Function for retrieve a list of mapper objects.

    :type session: sqlalchemy.orm.session.Session
    :type retrieve: function | None

    :rtype: sqlalchemy.orm.session.Session
    """
    _make_history_event(session)

    if retrieve is None:
        retrieve = lambda: _versioned_mappers

    for model_mapper in retrieve():
        _history_mapper(model_mapper)


def make_versioned_class(register=None):
    """Factory for creating a Versioned mixin. If ``register`` is given, the
    function will be used for registering the mapper object (see also
    :func:`make_versioned`).

    :param register: Function for registering a mapper object.
    :type register: function | None

    :rtype: class
    """
    if register is None:
        register = lambda m: _versioned_mappers.append(m)

    class _Versioned(object):
        """Mixin for enabling versioning for a model."""

        @declared_attr
        def __mapper_cls__(cls):
            def _map(cls, *args, **kwargs):
                model_mapper = mapper(cls, *args, **kwargs)
                register(model_mapper)
                return model_mapper
            return _map

    return _Versioned


def _is_versioned_object(obj):
    """Returns `True` if object is version-enabled.

    :param obj: SQLAlchemy model object.

    :type obj: sqlalchemy.ext.declarative.api.Base
    :rtype: bool
    """
    return hasattr(obj, '__history_mapper__')


def _create_version(obj, session, type_=None, force=False):
    """Create a new version for the given :attr:`obj`.

    :param obj: SQLAlchemy model object.
    :param session: SQLAlchemy session object.
    :param type_: Type of a change.
    :param force: Flag to always create version.

    :type obj: sqlalchemy.ext.declarative.api.Base
    :type session: sqlalchemy.orm.scoping.scoped_session
    :type type_: string
    :type force: bool
    """
    obj_mapper = object_mapper(obj)
    history_mapper = obj.__history_mapper__
    history_class = history_mapper.class_

    obj_state = attributes.instance_state(obj)
    obj_changed = False
    attr = {}

    for obj_mapper_, history_mapper_ in zip(
            obj_mapper.iterate_to_root(),
            history_mapper.iterate_to_root()):

        if history_mapper_.single:
            continue

        for history_column in history_mapper_.local_table.c:
            if _is_versioning_column(history_column):
                continue

            obj_column = obj_mapper_.local_table.c[history_column.key]

            try:
                prop = obj_mapper.get_property_by_column(obj_column)
            except UnmappedColumnError:
                continue

            # Force deferred columns to load.
            if prop.key not in obj_state.dict:
                getattr(obj, prop.key)

            added_, unchanged_, deleted_ = attributes.get_history(obj, prop.key)

            if deleted_:
                attr[prop.key] = deleted_[0]
                obj_changed = True
            elif unchanged_:
                attr[prop.key] = unchanged_[0]
            elif added_:
                obj_changed = True

    if not obj_changed:
        for prop in obj_mapper.iterate_properties:
            if isinstance(prop, RelationshipProperty) and \
               attributes.get_history(
                   obj,
                   prop.key,
                   passive=attributes.PASSIVE_NO_INITIALIZE).has_changes():
                for p in prop.local_columns:
                    if p.foreign_keys:
                        obj_changed = True
                        break
                if obj_changed is True:
                    break

    if not obj_changed and not force:
        return

    attr['version'] = obj.version
    attr['change_type'] = type_
    history = history_class()
    for key, value in attr.items():
        setattr(history, key, value)

    session.add(history)
    obj.version += 1


def _create_history_dirty(session, objs):
    """Create a new version for dirty objects.

    :param session: SQLAlchemy sesion object.
    :param objs: Dirty objects usually obtained by ``session.dirty``
    :type session: sqlalchemy.orm.session.Session
    :type objs: list[sqlalchemy.ext.declarative.api.Base]
    """
    for obj in objs:
        if _is_versioned_object(obj):
            _create_version(obj, session, type_='update')


def _create_history_deleted(session, objs):
    """Create a new version for deleted objects. This method will also create
    a new version for relation that do not have ``cascade`` parameter set in
    which SQLAlchemy will default to set its foreign keys to ``NULL``.

    :param session: SQLAlchemy sesion object.
    :param objs: Dirty objects usually obtained by ``session.deleted``
    :type session: sqlalchemy.orm.session.Session
    :type objs: list[sqlalchemy.ext.declarative.api.Base]
    """
    for obj in objs:
        if _is_versioned_object(obj):
            _create_version(obj, session, type_='delete', force=True)

        # Also handle NULL fks from SQLAlchemy Cascades. See also:
        # 6e1f34 lib/sqlalchemy/orm/dependency.py#L423-L424
        obj_mapper = object_mapper(obj)
        related = None

        def _create_cascade_version(target_obj):
            if not target_obj in objs:
                _create_version(target_obj,
                                session,
                                type_='update.cascade',
                                force=True)

        for prop in obj_mapper.iterate_properties:
            if isinstance(prop, RelationshipProperty) and \
               not prop.cascade.delete and \
               not prop.passive_deletes == 'all' and \
               _is_versioned_object(prop.mapper.class_):
                related = getattr(obj, prop.key)
                try:
                    for target_obj in related:
                        _create_cascade_version(target_obj)
                except TypeError:
                    _create_cascade_version(related)


def _make_history_event(session):
    """Registers an event for recording versioned object.

    :param session: SQLAlchemy session object.
    :type session: sqlalchemy.orm.session.Session
    :rtype: sqlalchemy.orm.session.Session
    """
    @event.listens_for(session, 'before_flush')
    def update_history(session_, context, instances):
        _create_history_dirty(session_, session_.dirty)
        _create_history_deleted(session_, session_.deleted)
    return session
