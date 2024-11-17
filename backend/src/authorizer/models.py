from pydantic import BaseModel
from datetime import datetime


# TODO: if the user coming in does not have these fields then we have a problem.
# why does the user have an id but not the user that made the post?
# can I do this a better way? do I inherit it and add the id?

class User(BaseModel):
    """
    User represents the current user of the app.

    Attributes:
    ----------
    name : str
        is the full name of the user.

    id: str
        is the id of the user based on the platform. 
    """
    name: str
    id: str

class Author(BaseModel):
    """
    Author represents an post author with a name and a screen name.

    Attributes:
    ----------
    name : str
        The full name of the author.
    screen_name : str
        The screen name or handle of the author
    """
    name: str
    screen_name: str


# TODO: check that each post matches the template

class Post(BaseModel):
    """
    Post represents a social media post with various metadata.

    Attributes:
    ----------
    id : int
        The unique identifier for the post.
    favorite_count : int
        The number of times the post has been marked as a favorite.
    favorited : bool
        Indicates whether the post is favorited by the current user.
    retweeted : bool
        Indicates whether the post has been retweeted by the current user.
    full_text : str
        The complete text content of the post.
    created_at : datetime
        The timestamp when the post was created, as a `datetime` object.
    user : Author
        The author of the post.
    """
    id: str
    favorite_count: int
    favorited: bool
    retweeted: bool
    full_text: str
    created_at: datetime 
    user: Author

    class Config:
        extra = "allow"
