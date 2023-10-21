import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    with db.engine.begin() as connection: 
        print("barrels_delivered")
        print(barrels_delivered)
        num_red_ml = 0
        num_blue_ml = 0
        num_green_ml = 0
        gold = 0
        for barrel in barrels_delivered:
            #means its red
            if barrel.sku == "SMALL_RED_BARREL":
                #only buying one barrel rn 
                num_red_ml += barrel.ml_per_barrel * barrel.quantity
                gold += barrel.price * barrel.quantity
            #means its green 
            elif barrel.sku == "SMALL_GREEN_BARREL": 
                num_green_ml += barrel.ml_per_barrel * barrel.quantity
                gold += barrel.price * barrel.quantity
            elif barrel.sku == "SMALL_BLUE_BARREL":
                num_blue_ml += barrel.ml_per_barrel * barrel.quantity
                gold += barrel.price * barrel.quantity
        if gold > 0:
            connection.execute(sqlalchemy.text("INSERT INTO gold_ledger (change) VALUES (:goldset)"), {'goldset':-gold})
        if num_red_ml > 0:
            connection.execute(sqlalchemy.text("INSERT INTO red_ml_ledger (change) VALUES (:red_ml)"), {'red_ml':num_red_ml})
        if num_green_ml > 0:
            connection.execute(sqlalchemy.text("INSERT INTO green_ml_ledger (change) VALUES (:green_ml)"), {'green_ml':num_green_ml})
        if num_blue_ml > 0:
            connection.execute(sqlalchemy.text("INSERT INTO blue_ml_ledger (change) VALUES (:blue_ml)"), {'blue_ml':num_blue_ml})
        
        print("GOLD CHANGE " + str(-gold))
        print("RED CHANGE " + str(num_red_ml) + ", GREEN CHANGE " + str(num_green_ml) + ", BLUE CHANGE " + str(num_blue_ml))

        return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    with db.engine.begin() as connection: 
        print(wholesale_catalog)
        #get num ml 
        # result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_blue_ml, num_green_ml, gold FROM global_inventory WHERE id=1"))
        gold = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM gold_ledger"))
        red = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM red_ml_ledger"))
        green = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM green_ml_ledger"))
        blue = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM blue_ml_ledger"))
        red = red.fetchone()
        print("RED ML QTY: " + str(red.balance))
        green = green.fetchone()
        print("GREEN ML QTY: " + str(green.balance))
        blue = blue.fetchone()
        print("BLUE ML QTY: " + str(blue.balance))
        data = gold.fetchone()
        print("GOLD QTY " + str(data.balance))

        # getting all the inventory that i have and my gold
        num_red_ml = red.balance
        num_blue_ml = blue.balance
        num_green_ml = green.balance
        gold = data.balance

        potions = [("red", num_red_ml), ("blue", num_blue_ml), ("green", num_green_ml)]
        potions = sorted(potions, key=lambda x: x[1])

        print(gold)
        print(potions)
        plan = []
        # plan buy barrels based on num_ml of potions
        for potion in potions:
            pot_type = potion[0]
            for barrel in wholesale_catalog:
                if pot_type == "red":
                    if barrel.sku == "SMALL_RED_BARREL":
                        if gold >= barrel.price:
                            gold -= barrel.price
                            plan.append({"sku": "SMALL_RED_BARREL", "quantity": 1}) 
                if pot_type == "blue":
                    if barrel.sku == "SMALL_BLUE_BARREL":
                        if gold >= barrel.price: 
                            gold -= barrel.price
                            plan.append({"sku": "SMALL_BLUE_BARREL", "quantity": 1})
                if pot_type == "green":
                    if barrel.sku == "SMALL_GREEN_BARREL":
                        if gold >= barrel.price: 
                            gold -= barrel.price
                            plan.append({"sku": "SMALL_GREEN_BARREL", "quantity": 1})
        print(plan)
        print(gold)

        return plan