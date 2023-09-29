import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    with db.engine.begin() as connection: 
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_red_ml FROM global_inventory WHERE id=1"))
        data = result.fetchone()
        num_red_potions = data[0]
        num_red_ml = data[1]
        for potion in potions_delivered:
            #if we have a red potion add to num_red_potions
            #also subtract from num red ml when bottling potions 
            if potion.potion_type[0] == 100:
                num_red_potions += potion.quantity
                num_red_ml -= potion.quantity * 100
        
        value = {'potions':num_red_potions}
        value2 = {'ml':num_red_ml}

        # "UPDATE global_inventory SET num_red_potions=:potions, "

        sql = sqlalchemy.text("UPDATE global_inventory SET num_red_potions=:potions",)
        sql2 = sqlalchemy.text("UPDATE global_inventory SET num_red_ml=:ml")
        connection.execute(sql, value)
        connection.execute(sql2, value2)

        print(potions_delivered)
        return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory WHERE id=1"))
        ml = result.fetchone()
        ml = ml[0]
        quantity = ml / 100
        print("bottle quantity: " + str(quantity))
        return [
                {
                    "potion_type": [100, 0, 0, 0],
                    "quantity": quantity,
                }
            ]
