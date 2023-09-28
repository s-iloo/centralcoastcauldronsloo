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
    print(barrels_delivered)

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """

    with db.engine.begin() as connection: 
         #gives num potions
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory WHERE id=1"))
        data = result.fetchone()
        price = 0
        if data[0] < 10:
            gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory WHERE id=1"))
            for barrel in wholesale_catalog: 
                if barrel.sku == "SMALL_RED_BARREL": 
                    price += barrel.price
        
            remaining_gold = gold.fetchone()[0] - price
            sql = sqlalchemy.text("UPDATE global_inventory SET gold=:gold WHERE id=1")
            connection.execute(sql, gold=remaining_gold)
            # connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold=%s WHERE id=1"), remaining_gold)
                        
            return [
                {
                    "sku": "SMALL_RED_BARREL",
                    "quantity": 1,
                }
            ]
        else:
            print(result)    
            print(wholesale_catalog)