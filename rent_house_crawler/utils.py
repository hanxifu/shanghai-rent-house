def _get_or_created(session, model, **kwargs):
    """
    Returns a tuple of (object, created), where object is the retrieved or
    created object and created is a boolean specifying whether a new object was
    created.
    :param session: database session
    :param model: model
    :param kwargs: model keywords
    :return: (instance, created)
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance, True


def _add_m2m_relationship(secondary_ref, instance):
    """
    Check if the instance exists in the many-to-many secondary_ref table.
    Append the instance if not exists.
    :param secondary_ref: secondary table reference
    :param instance: model instance
    :return: None
    """
    if instance not in secondary_ref:
        secondary_ref.append(instance)


def get_or_create(session, model, **kwargs):
    """
    This is used for one-to-many/one-to-one/many-to-one relationship. For
    many to many relationship, please use :func:get_or_created_m2m().
    :param session: database session
    :param model: model
    :param kwargs: model keywords
    :return: (instance, created)
    """
    return _get_or_created(session, model, **kwargs)


def get_or_create_m2m(session, model, secondary_ref, **kwargs):
    """
    This is used for many-to-many relationship. For other database
    relationships, please use :func:get_or_created().
    :param session: database session
    :param model: model
    :param secondary_ref: secondary table reference
    :param kwargs: model keywords
    :return: (instance, created)
    """
    instance, created = _get_or_created(session, model, **kwargs)
    _add_m2m_relationship(secondary_ref, instance)
    session.commit()
    return instance, created
