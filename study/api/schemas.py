"""Input/output contracts for /measure (pydantic v2)."""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, model_validator


class MeasureRequest(BaseModel):
    mode: Literal["with-odds", "odds-free"] = "with-odds"

    # with-odds mode: one of the two input forms
    odds_hda: Optional[List[List[float]]] = Field(
        None, description="decimal 1X2 odds per match: [[H,D,A], ...]")
    p_fav: Optional[List[float]] = Field(
        None, description="de-vigged favourite probability per match (alternative to odds_hda)")
    o_fav: Optional[List[float]] = Field(
        None, description="favourite odds per match; default = fair odds 1/p_fav")

    # odds-free mode
    upset_rate: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Elo upset rate (results only)")

    bootstrap: int = Field(300, ge=50, le=2000, description="bootstrap SE replicates")

    @model_validator(mode="after")
    def _check(self):
        if self.mode == "odds-free":
            if self.upset_rate is None:
                raise ValueError("odds-free mode requires `upset_rate`")
        else:
            if not self.odds_hda and not self.p_fav:
                raise ValueError("with-odds mode requires `odds_hda` or `p_fav`")
            if self.odds_hda and any(len(r) != 3 for r in self.odds_hda):
                raise ValueError("each odds_hda row must be [Home, Draw, Away]")
            if self.o_fav is not None and self.p_fav is not None \
                    and len(self.o_fav) != len(self.p_fav):
                raise ValueError("o_fav and p_fav must have the same length")
        return self


class Nearest(BaseModel):
    code: str
    name: str
    delta: float


class Equivalence(BaseModel):
    code: str
    name: str
    residual_gap: float
    se_combined: float
    margin: float
    same_asymmetry: bool


class Anomaly(BaseModel):
    flag: str
    detail: str
