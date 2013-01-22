from zope.interface import Interface


class IBoard(Interface):
    """Model representing board."""
    pass


class ITopic(Interface):
    """Model representing topic."""
    pass


class IPost(Interface):
    """Model representing post."""
    pass


class IBoardResource(Interface):
    """Resource representing board."""
    pass


class ITopicResource(Interface):
    """Resource representing topic."""
    pass


class IPostResource(Interface):
    """Resource representing post."""
    pass