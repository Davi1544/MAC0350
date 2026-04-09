from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel, Column, TIMESTAMP, text

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    username: str
    handle: str = Field(index=True, unique=True) # make it unique later
    email: str = Field(index=True, unique=True)
    password: str
    bio: str

    tweets: List["Tweet"] = Relationship(
        back_populates="user",
    )
    
class Tweet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    content: str
    post_date: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))

    # User connection
    user_id : Optional[int] = Field(default=None, foreign_key="usuario.id")
    user: Optional["Usuario"] = Relationship(
        back_populates="tweets"
    )

    # Add the foreign key column for parent tweet
    parent_id: Optional[int] = Field(default=None, foreign_key="tweet.id")
    
    # Self-referential relationship
    parent: Optional["Tweet"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Tweet.id"}
    )
    children: List["Tweet"] = Relationship(back_populates="parent",
                                           sa_relationship_kwargs={
            "cascade": "all, delete"
        })