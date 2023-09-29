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
        result = connection.execute(sqlalchemy.text("SELECT gold, num_red_ml FROM global_inventory WHERE id=1"))
        data = result.fetchone()
        gold = data[0]
        price = 0
        ml = 0
        num_red_ml = data[1]
        for barrel in barrels_delivered:
            price += barrel.price
            ml += barrel.ml_per_barrel
        remaining_gold = gold - price
        remaining_ml = num_red_ml + ml
        value ={'goldset':remaining_gold}
        sql = sqlalchemy.text("UPDATE global_inventory SET gold=:goldset")
        connection.execute(sql, value)
        value2 = {'mlset':remaining_ml}
        sql2 = sqlalchemy.text("UPDATE global_inventory SET num_red_ml=:mlset")
        connection.execute(sql2, value2)
        print("your remaining gold is " + remaining_gold)
        print("your remaining ml is " + remaining_ml)
        
        return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    with db.engine.begin() as connection: 
        #get num red potions
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, gold FROM global_inventory WHERE id=1"))
        #parse to get int
        data = result.fetchone()
        num_red_potions = data[0]
        gold = data[1]
        #check if inventory is less than 10 
        if num_red_potions < 10:
            for barrel in wholesale_catalog:
                if barrel.sku == "SMALL_RED_BARREL":
                    if gold >= barrel.price: 
                        return [
                            {
                            "sku": "SMALL_RED_BARREL",
                            "quantity": barrel.quantity,
                            }
                        ]
        return "INVENTORY LESS THAN 10"