def get_or_create(session, model, **kwargs):
    """
    Returns a tuple of (object, created), where object is the retrieved or
    created object and created is a boolean specifying whether a new object was
    created.
    :param session: database session
    :param model: model
    :param kwargs: keywords
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
