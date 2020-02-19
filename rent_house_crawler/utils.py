from typing import List


def get_or_create(session, model, **kwargs):
    """
    Returns a tuple of (object, created), where object is the retrieved or
    created object and created is a boolean specifying whether a new object was
    created.
    :param session: scoped_session
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


def add_m2m_relationship(session, secondary_ref, instances: List):
    """
    Check if the instance exists in the many-to-many secondary_ref table.
    Append the instance if not exists.
    :param session: scoped_session
    :param secondary_ref: secondary table reference
    :param instances: model instance list
    :return: None
    """
    secondary_ref.extend(instances)
    session.commit()
