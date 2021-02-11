from dataclasses import dataclass 

@dataclass
class President:
    name: str 
    start: str 
    end: str
    party: str

presidents = [
    President(
        name="Kennedy",
        start="1961-01-01",
        end="1963-01-01",
        party="Democrat"
    ),
    President(
        name="Johnson",
        start="1963-01-01",
        end="1969-01-01",
        party="Democrat"
    ),
    President(
        name="Nixon",
        start="1969-01-01",
        end="1974-01-01",
        party="Republican"
    ),
    President(
        name="Ford",
        start="1974-01-01",
        end="1977-01-01",
        party="Republican"
    ),
    President(
        name="Carter",
        start="1977-01-01",
        end="1981-01-01",
        party="Democrat"
    ),
    President(
        name="Reagan",
        start="1981-01-01",
        end="1989-01-01",
        party="Republican"
    ),
    President(
        name="Bush Sr.",
        start="1989-01-01",
        end="1993-01-01",
        party="Republican"
    ),
    President(
        name="Clinton",
        start="1993-01-01",
        end="2001-01-01",
        party="Democrat"
    ),
    President(
        name="Bush",
        start="2001-01-01",
        end="2009-01-01",
        party="Republican"
    ),
    President(
        name="Obama",
        start="2009-01-01",
        end="2017-01-01",
        party="Democrat"
    ),
    President(
        name="Trump",
        start="2017-01-01",
        end="2018-01-01",
        party="Republican"
    ),
]
