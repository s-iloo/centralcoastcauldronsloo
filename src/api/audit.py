import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    with db.engine.begin() as connection: 
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions, num_red_ml, num_green_ml, num_blue_ml, gold FROM global_inventory WHERE id=1"))
        data = result.fetchone()
        total_potions = data[0] + data[1] + data[2]
        total_ml = data[3] + data[4] + data[5]
        return {"number_of_potions": total_potions, "ml_in_barrels": total_ml, "gold": data[6]}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
