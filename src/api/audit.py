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
        # result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, gold FROM global_inventory WHERE id=1"))
        # data = result.fetchone()
        # total_ml = data[0] + data[1] + data[2]
        # gold = data[3]
        total_potions = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM potion_ledger"))
        total_potions = total_potions.fetchone()
        total_potions = total_potions.balance
        red_ml = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM red_ml_ledger"))
        red_ml = red_ml.fetchone()
        red_ml = red_ml.balance

        blue_ml = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM blue_ml_ledger"))
        blue_ml = blue_ml.fetchone()
        blue_ml = blue_ml.balance

        green_ml = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM green_ml_ledger"))
        green_ml = green_ml.fetchone()
        green_ml = green_ml.balance

        gold = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM gold_ledger"))
        gold = gold.fetchone()
        gold = gold.balance
        # potion1 = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id=1"))
        # potion2 = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id=2"))
        # potion3 = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id=3"))
        # potion4 = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id=4"))
        # potion1 = potion1.fetchone()
        # potion1 = potion1[0]
        # potion2 = potion2.fetchone()
        # potion2 = potion2[0]
        # potion3 = potion3.fetchone()
        # potion3 = potion3[0]
        # potion4 = potion4.fetchone()
        # potion4 = potion4[0]

        return {"number_of_potions": total_potions, "ml_in_barrels": red_ml + green_ml + blue_ml, "gold": gold}

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
